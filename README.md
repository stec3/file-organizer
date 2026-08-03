# file-organizer

A Python script that sorts the files of a folder into subfolders by type — with a preview before anything moves, and an undo for when you change your mind.

No dependencies: standard library only.

## Features

- **Preview first** — see exactly where every file would go, grouped by destination, before a single one moves
- **Never overwrites** — a file whose name is already taken at the destination is renamed `report (1).pdf`, not silently replaced
- **Undo** — `--undo` puts the last run back exactly where it was, empty folders included
- **Operation log** — every move is recorded with its full source and destination path, which is what makes undo possible
- **Dry run** — `--dry-run` shows the plan and touches nothing
- Skips hidden files, subfolders and its own log
- One unmovable file (locked, no permission) does not abort the rest of the run

## Usage

```bash
python organizer.py                  # asks for the folder: drag and drop it in
python organizer.py ~/Downloads      # or pass the path directly
python organizer.py ~/Downloads -y   # skip the confirmation prompt
python organizer.py --dry-run        # show the plan, move nothing
python organizer.py --undo           # move back what the last run moved
```

Example preview:

```
--- PREVIEW: 8 files in /Users/me/Downloads ---

  Documenti/
    note.txt
    report.pdf   (renamed to report (1).pdf, name already taken)

  Immagini/
    foto.jpg
    vacanza.png
```

## Where files go

| Folder | Extensions |
|---|---|
| `Immagini` | jpg, jpeg, png, gif, heic, webp, svg, tiff |
| `Documenti` | pdf, doc, docx, txt, rtf, odt, xls, xlsx, csv, ppt, pptx, pages |
| `Video` | mp4, mov, avi, mkv |
| `Musica` | mp3, wav, m4a, flac |
| `Archivi` | zip, rar, 7z, tar, gz, dmg |
| `Altri` | anything else |

To change the mapping, edit the `DESTINATIONS` dictionary at the top of `organizer.py`.

## The log

`organizer_log.txt` is written inside the organized folder:

```
# run 2026-08-03 17:29:48
/Users/me/Downloads/foto.jpg	/Users/me/Downloads/Immagini/foto.jpg
```

Full paths, tab separated, one line per file, appended run after run. `--undo` reads the last block, moves those files back and removes that block from the log, so undoing twice in a row does nothing the second time.

## License

MIT
