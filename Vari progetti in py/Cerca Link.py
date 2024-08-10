import tkinter as tk
from tkinter import filedialog
import re

def find_links_in_files():
    # Apri la finestra di dialogo per selezionare i file (qualsiasi file)
    file_paths = filedialog.askopenfilenames(
        title="Seleziona i file",
        filetypes=[("All files", "*.*")]
    )
    
    # Espressione regolare per trovare i link completi
    url_pattern = re.compile(r'https?://[^\s"\'>]+')
    
    # Insieme per contenere tutti i link unici trovati
    unique_links = set()
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                links = url_pattern.findall(content)
                unique_links.update(links)
        except (UnicodeDecodeError, IOError):
            print(f"Non è stato possibile leggere il file: {file_path}")
    
    # Scrivi i link trovati e unici in un file .txt
    if unique_links:
        with open("found_links.txt", 'w', encoding='utf-8') as output_file:
            for link in unique_links:
                output_file.write(link + '\n')
        print(f"Trovati {len(unique_links)} link unici. Salvati in 'found_links.txt'.")
    else:
        print("Nessun link trovato.")

# Crea la finestra principale
root = tk.Tk()
root.title("Trova Link nei File")

# Crea un pulsante per avviare la ricerca
button = tk.Button(root, text="Seleziona File e Trova Link", command=find_links_in_files)
button.pack(pady=20)

# Esegui la finestra principale
root.mainloop()
