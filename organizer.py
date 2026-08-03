"""file-organizer - sorts the files of a folder into subfolders by type.

Usage:
    python organizer.py                 # asks for the folder, drag and drop it
    python organizer.py ~/Downloads     # or pass it directly
    python organizer.py --dry-run       # show the plan, move nothing
    python organizer.py --undo          # put back what the last run moved

Every move is recorded in organizer_log.txt inside the organized folder, which
is what makes --undo possible.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime

LOG_NAME = "organizer_log.txt"

# Extension -> destination folder. Anything not listed goes to "Altri".
DESTINATIONS = {
    ".jpg": "Immagini", ".jpeg": "Immagini", ".png": "Immagini",
    ".gif": "Immagini", ".heic": "Immagini", ".webp": "Immagini",
    ".svg": "Immagini", ".tiff": "Immagini",

    ".pdf": "Documenti", ".doc": "Documenti", ".docx": "Documenti",
    ".txt": "Documenti", ".rtf": "Documenti", ".odt": "Documenti",
    ".xls": "Documenti", ".xlsx": "Documenti", ".csv": "Documenti",
    ".ppt": "Documenti", ".pptx": "Documenti", ".pages": "Documenti",

    ".mp4": "Video", ".mov": "Video", ".avi": "Video", ".mkv": "Video",

    ".mp3": "Musica", ".wav": "Musica", ".m4a": "Musica", ".flac": "Musica",

    ".zip": "Archivi", ".rar": "Archivi", ".7z": "Archivi",
    ".tar": "Archivi", ".gz": "Archivi", ".dmg": "Archivi",
}

FALLBACK = "Altri"


def parse_args():
    """Read the command line options."""
    parser = argparse.ArgumentParser(
        prog="organizer.py",
        description="Sort the files of a folder into subfolders by type.",
    )
    # nargs="?" makes the path optional: without it the script asks, which is
    # what allows dragging the folder into the terminal window.
    parser.add_argument("folder", nargs="?", default=None,
                        help="folder to organize (asked interactively if omitted)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen, move nothing")
    parser.add_argument("--undo", action="store_true",
                        help="move back the files of the last run, using the log")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="skip the confirmation prompt")
    return parser.parse_args()


def ask_folder(given):
    """Return the folder to work on, asking for it when not given.

    macOS adds quotes around a dragged path when it contains spaces, and a
    trailing space after the drop: both are stripped here.
    """
    raw = given if given is not None else input("Drag and drop the folder and press enter: ")
    folder = os.path.expanduser(raw.strip().strip('"').strip("'").strip())

    if not folder:
        sys.exit("Error: no folder given.")
    if not os.path.exists(folder):
        sys.exit(f"Error: path not found: {folder}")
    if not os.path.isdir(folder):
        sys.exit(f"Error: this is a file, not a folder: {folder}")
    return folder


def free_path(destination_dir, filename):
    """Return a path inside destination_dir that no existing file occupies.

    Without this, moving report.pdf into a folder that already contains a
    report.pdf would silently destroy one of the two: shutil.move overwrites
    the target without asking. Here the second one becomes "report (1).pdf".
    """
    candidate = os.path.join(destination_dir, filename)
    if not os.path.exists(candidate):
        return candidate

    stem, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(destination_dir, f"{stem} ({counter}){extension}")
        counter += 1
    return candidate


def build_plan(folder):
    """Decide where every file goes, once.

    Returns a list of (source, destination) pairs. The whole point of building
    the plan up front is that the preview and the actual move read the *same*
    list: two separate loops deciding the same thing independently is exactly
    how this script ended up moving files without logging them.
    """
    plan = []

    for name in sorted(os.listdir(folder)):
        source = os.path.join(folder, name)

        # Hidden files (.DS_Store and friends) and the log itself are not part
        # of the user's content: skipping them here means they never show up in
        # the preview either.
        if name.startswith(".") or name == LOG_NAME:
            continue
        if os.path.isdir(source):
            continue

        extension = os.path.splitext(name)[1].lower()
        folder_name = DESTINATIONS.get(extension, FALLBACK)
        destination = free_path(os.path.join(folder, folder_name), name)
        plan.append((source, destination))

    return plan


def show_plan(plan, folder):
    """Print what is about to happen, grouped by destination folder."""
    if not plan:
        print("Nothing to organize: no loose files in this folder.")
        return

    by_folder = {}
    for source, destination in plan:
        # The name of the folder the file is going into, e.g. "Immagini".
        group = os.path.basename(os.path.dirname(destination))
        by_folder.setdefault(group, []).append((source, destination))

    print(f"\n--- PREVIEW: {len(plan)} files in {folder} ---")
    for group in sorted(by_folder):
        print(f"\n  {group}/")
        for source, destination in by_folder[group]:
            name = os.path.basename(source)
            renamed = os.path.basename(destination)
            # Signal renames explicitly: a file quietly landing under another
            # name is the kind of surprise that makes a tool untrustworthy.
            suffix = f"   (renamed to {renamed}, name already taken)" if renamed != name else ""
            print(f"    {name}{suffix}")


def apply_plan(plan, folder):
    """Move the files and record every move in the log."""
    log_path = os.path.join(folder, LOG_NAME)
    moved = 0

    # The log is opened once for the whole run, in append mode so previous runs
    # are kept: it is the history the --undo option reads back.
    with open(log_path, "a", encoding="utf-8") as log:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"# run {stamp}\n")

        for source, destination in plan:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            try:
                shutil.move(source, destination)
            except OSError as error:
                # One unmovable file (locked, no permission) must not abort the
                # other two hundred.
                print(f"  ! skipped {os.path.basename(source)}: {error}")
                continue

            # Full paths, tab separated: --undo needs to know exactly where
            # each file came from, and a tab cannot appear in a macOS filename.
            log.write(f"{source}\t{destination}\n")
            moved += 1
            print(f"  {os.path.basename(source)} -> {os.path.basename(os.path.dirname(destination))}/")

    print(f"\nDone: {moved} files organized. Log: {log_path}")


def undo_last_run(folder):
    """Move back the files of the most recent run, reading the log."""
    log_path = os.path.join(folder, LOG_NAME)
    if not os.path.exists(log_path):
        sys.exit(f"Error: no log found in {folder}, nothing to undo.")

    lines = open(log_path, encoding="utf-8").read().splitlines()

    # Walk backwards to the last "# run" marker: everything after it belongs to
    # the most recent run.
    start = None
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].startswith("# run"):
            start = index
            break

    if start is None:
        sys.exit("Error: the log has no run to undo.")

    entries = [line.split("\t") for line in lines[start + 1:] if "\t" in line]
    if not entries:
        sys.exit("Error: the last run moved no file.")

    print(f"Undoing {len(entries)} moves from {lines[start][2:]}")
    restored = 0
    for source, destination in entries:
        if not os.path.exists(destination):
            print(f"  ! {os.path.basename(destination)} is no longer there, skipped")
            continue
        # free_path again on the way back: the user may have created a new file
        # with the original name in the meantime.
        shutil.move(destination, free_path(os.path.dirname(source), os.path.basename(source)))
        restored += 1

    # Remove the destination folders left empty, so undoing really goes back to
    # the state before the run instead of leaving a row of empty folders.
    for _, destination in entries:
        directory = os.path.dirname(destination)
        if os.path.isdir(directory) and not os.listdir(directory):
            os.rmdir(directory)

    # The undone run is removed from the log, so calling --undo twice does not
    # try to undo the same moves again.
    with open(log_path, "w", encoding="utf-8") as log:
        log.write("\n".join(lines[:start]) + ("\n" if start else ""))

    print(f"Done: {restored} files moved back.")


def main():
    args = parse_args()
    folder = ask_folder(args.folder)

    if args.undo:
        undo_last_run(folder)
        return

    plan = build_plan(folder)
    show_plan(plan, folder)
    if not plan:
        return

    if args.dry_run:
        print("\nDry run: nothing was moved.")
        return

    if not args.yes and input("\nProceed? (y/n): ").strip().lower() not in ("y", "yes"):
        print("Cancelled.")
        return

    apply_plan(plan, folder)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl-C during a long run: a clean line instead of a stack trace.
        print("\nInterrupted.")
    except PermissionError as error:
        sys.exit(f"Error: no permission to access this folder ({error}).")
