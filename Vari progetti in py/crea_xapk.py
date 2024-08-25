import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import json  # Per creare il manifest.json
import tempfile  # Per creare una directory temporanea

# Funzione per creare il file manifest.json
def crea_manifest(temp_dir, package_name, apk_name, obb_file):
    manifest_content = {
        "xapk_version": 1,
        "name": apk_name,  # Usa il nome del file APK senza estensione
        "package_name": package_name,
        "version_code": 1,  # Valore predefinito
        "version_name": "1.0",  # Valore predefinito
        "min_sdk_version": 21,
        "target_sdk_version": 30,
        "obb": [
            {
                "file": obb_file,
                "install_location": f"Android/obb/{package_name}/"
            }
        ]
    }
    
    # Crea il file manifest.json
    manifest_path = os.path.join(temp_dir, "manifest.json")
    with open(manifest_path, 'w') as manifest_file:
        json.dump(manifest_content, manifest_file, indent=4)

def seleziona_apk():
    apk_path.set(filedialog.askopenfilename(filetypes=[("APK files", "*.apk")]))

def seleziona_obb():
    obb_path.set(filedialog.askopenfilename(filetypes=[("OBB files", "*.obb")]))

def crea_xapk():
    # Controlla che i campi siano stati riempiti
    if not apk_path.get() or not obb_path.get() or not package_name.get():
        messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
        return

    # Estrai il nome del file APK senza estensione
    apk_name = os.path.splitext(os.path.basename(apk_path.get()))[0]

    # Crea una directory temporanea
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Creazione della struttura delle cartelle Android/obb/<package_name>
        android_dir = os.path.join(temp_dir, "Android")
        obb_dir = os.path.join(android_dir, "obb", package_name.get())
        os.makedirs(obb_dir, exist_ok=True)
        
        # Copia l'APK nella cartella principale
        shutil.copy(apk_path.get(), temp_dir)
        
        # Copia l'OBB nella cartella obb/<package_name>
        shutil.copy(obb_path.get(), obb_dir)
        
        # Crea il manifest.json
        crea_manifest(temp_dir, package_name.get(), apk_name, os.path.basename(obb_path.get()))
        
        # Chiedi all'utente dove salvare il file XAPK
        xapk_save_path = filedialog.asksaveasfilename(
            defaultextension=".xapk",
            filetypes=[("XAPK files", "*.xapk")],
            title="Salva il file XAPK come"
        )
        
        if not xapk_save_path:
            messagebox.showwarning("Operazione annullata", "Nessun percorso di salvataggio selezionato.")
            return
        
        # Comprimi il tutto in un file ZIP (XAPK)
        with zipfile.ZipFile(xapk_save_path, 'w', zipfile.ZIP_DEFLATED) as xapk_file:
            for foldername, subfolders, filenames in os.walk(temp_dir):
                for filename in filenames:
                    if filename != os.path.basename(xapk_save_path):  # Evita di includere il file XAPK stesso
                        file_path = os.path.join(foldername, filename)
                        arcname = os.path.relpath(file_path, temp_dir)
                        xapk_file.write(file_path, arcname)

        messagebox.showinfo("Successo", f"File XAPK creato con successo in {xapk_save_path}")
    finally:
        # Elimina la directory temporanea e tutti i file al suo interno
        shutil.rmtree(temp_dir, ignore_errors=True)

# Creazione della GUI con tkinter
root = tk.Tk()
root.title("Creatore di XAPK")

# Definizione delle variabili
apk_path = tk.StringVar()
obb_path = tk.StringVar()
package_name = tk.StringVar()

# Layout della GUI
tk.Label(root, text="Seleziona APK:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=apk_path, width=40).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Sfoglia", command=seleziona_apk).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Seleziona OBB:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=obb_path, width=40).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Sfoglia", command=seleziona_obb).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Package Name:").grid(row=2, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=package_name, width=40).grid(row=2, column=1, padx=10, pady=5)

tk.Button(root, text="Crea XAPK", command=crea_xapk).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
