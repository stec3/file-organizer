import os

cartella = input('Trascina la cartella e premi invio: ').strip().strip('"').strip("'")
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

for file in files:
    if os.path.isdir(os.path.join(cartella, file)):
        print(f'{file} » Cartella')
    else:
        nome, estensione = os.path.splitext(file)
        cartella_dest = destinazioni.get(estensione, 'Altri')
        print(f'{file} » {cartella_dest}')