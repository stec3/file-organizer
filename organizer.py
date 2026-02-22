import os
import shutil
import datetime

try:
    cartella = input('Trascina la cartella e premi invio: ').strip().strip('"').strip("'")

    if not os.path.exists(cartella):
        print('Errore: percorso non trovato')
        exit()

    if not os.path.isdir(cartella):
        print('Errore: il percorso non è una cartella')
        exit ()
    files = os.listdir(cartella)

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

    print('\n--- ANTEPRIMA ---')
    for file in files:
        if os.path.isdir(os.path.join(cartella, file)):
            print(f'{file} » Cartella, salto')
        else:
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            print(f'{file} » {cartella_dest}')

    conferma = input('\nVuoi procedere? (y/n): ')

    if conferma.lower() == 'y':
        for file in files:
            if file.startswith('.'):
                continue
            if os.path.isdir(os.path.join(cartella, file)):
                continue
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            percorso_dest = os.path.join(cartella, cartella_dest)
            os.makedirs(percorso_dest, exist_ok=True)
            shutil.move(os.path.join(cartella, file), percorso_dest)
            print(f'Spostato: {file} » {cartella_dest}')
        print('Organizzazione completata!')
    else:
        print('Operazione annullata.')

except PermissionError:
    print('Errore: non hia i permessi per acccedere a questa cartella')
except Exception as e:
    print(f'Errore inaspettato: {e}')

if conferma.lower() == 'y':
    log_path = os.path.join(cartella, 'organizer_log.txt')
    with open(log_path, 'a') as log:
        for file in files:
            if file.startswith('.') or file == 'organizer_log.txt':
                continue
            if os.path.isdir(os.path.join(cartella, file)):
                continue
            nome, estensione = os.path.splitext(file)
            cartella_dest = destinazioni.get(estensione, 'Altri')
            percorso_dest = os.path.join(cartella, cartella_dest)
            os.makedirs(percorso_dest, exist_ok=True)
            percorso_finale = os.path.join(percorso_dest, file)
            if os.path.exists(percorso_finale):
                print(f'Saltato (esiste già): {file}')
                continue
            shutil.move(os.path.join(cartella, file), percorso_dest)
            ora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            log.write(f'{ora}  - {file} » {cartella_dest}\n')
            print(f'Spostato: {file} » {cartella_dest}')
    print('\nOrganizzazione completata!')
