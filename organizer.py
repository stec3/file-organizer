# Standard Python libraries for filesystem operations, file manipulation, and date/time handling
import os
import shutil
import datetime

try:
    # Asks for the path of the folder to organize, removes spaces and quotes added by MacOS when dragging and dropping
    cartella = input('Drag and drop the folder and press enter: ').strip().strip('"').strip("'")

# Checks if the path exists
    if not os.path.exists(cartella):
        print('Error: path not found')
        exit()

# Checks if the path it's a folder and not a file
    if not os.path.isdir(cartella):
        print('Error: the path is not a folder')
        exit ()
        # Reads all files and folders in the chosen path
    files = os.listdir(cartella)

# Maps each extension to its destination folder
    destinazioni = {
        '.jpg': 'Immagini',
        '.jpeg': 'Immagini',
        '.png': 'Immagini',
        '.pdf': 'Documenti',
        '.docx': 'Documenti',
        '.mp4': 'Video',
        '.mp3': 'Musica',
        '.zip': 'Archivi',
    }

# Shows preview without moving anything
    print('\n--- PREVIEW ---')
    for file in files:
        if os.path.isdir(os.path.join(cartella, file)):
            print(f'{file} » Folder, skipping')
        else:
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            print(f'{file} » {cartella_dest}')

# Asks for confirmation before proceeding
    conferma = input('\nDo you want to proceed? (y/n): ')

    if conferma.lower() == 'y':
        for file in files:
            if file.startswith('.'):
                continue
            if os.path.isdir(os.path.join(cartella, file)):
                continue
            # Skips folders
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            percorso_dest = os.path.join(cartella, cartella_dest)
            # Creates the destination folder if it doesn't exist
            os.makedirs(percorso_dest, exist_ok=True)
            shutil.move(os.path.join(cartella, file), percorso_dest)
            print(f'Moved: {file} » {cartella_dest}')
        print('Organization completed!')
    else:
        print('Operation cancelled.')

except PermissionError:
    print('Error: you do not have permission to access this folder')
except Exception as e:
    print(f'Unexpected error: {e}')

if conferma.lower() == 'y':
    log_path = os.path.join(cartella, 'organizer_log.txt')
    with open(log_path, 'a') as log:
        for file in files:
            # Skips hidden files and the log file
            if file.startswith('.') or file == 'organizer_log.txt':
                continue
            if os.path.isdir(os.path.join(cartella, file)):
                continue
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            percorso_dest = os.path.join(cartella, cartella_dest)
            os.makedirs(percorso_dest, exist_ok=True)
            percorso_finale = os.path.join(percorso_dest, file)
            # Skips if file already exists in destination
            if os.path.exists(percorso_finale):
                print(f'Skipped (already exists): {file}')
                continue
            # Moves the file to destination folder
            shutil.move(os.path.join(cartella, file), percorso_dest)
            ora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            # Saves the operation in the log file with timestamp, file name and destination folder
            log.write(f'{ora}  - {file} » {cartella_dest}\n')
            print(f'Moved: {file} » {cartella_dest}')
    print('\nOrganization completed!')