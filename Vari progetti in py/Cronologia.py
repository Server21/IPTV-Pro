import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
import platform
import shutil
import tempfile

# Funzione per ottenere il percorso della cronologia di Brave in base al sistema operativo
def get_brave_history_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.getenv('LOCALAPPDATA'), "BraveSoftware", "Brave-Browser", "User Data", "Default", "History")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser/Default/History")
    elif system == "Linux":
        return os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/History")
    else:
        return None

# Funzione per ottenere il percorso della cartella delle sessioni di Brave in base al sistema operativo
def get_brave_sessions_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.getenv('LOCALAPPDATA'), "BraveSoftware", "Brave-Browser", "User Data", "Default", "Sessions")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Sessions")
    elif system == "Linux":
        return os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/Sessions")
    else:
        return None

# Funzione per cancellare la cronologia di Brave
def cancella_cronologia():
    try:
        # Ottieni il percorso corretto della cronologia in base al sistema operativo
        path_to_brave_history = get_brave_history_path()
        
        # Verifica se il percorso è valido
        if path_to_brave_history is None:
            messagebox.showerror("Errore", "Sistema operativo non supportato.")
            return

        # Verifica se il file della cronologia esiste
        if not os.path.exists(path_to_brave_history):
            messagebox.showerror("Errore", "Non riesco a trovare il file della cronologia.")
            return

        # Crea una copia temporanea del file di cronologia
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "History")
        shutil.copy2(path_to_brave_history, temp_path)

        # Connessione al database SQLite nella copia temporanea
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # Cancella la cronologia
        cursor.execute("DELETE FROM urls")
        conn.commit()

        # Chiudi la connessione
        conn.close()

        # Sovrascrivi il file originale con la versione modificata
        shutil.copy2(temp_path, path_to_brave_history)

        # Rimuovi la cartella temporanea
        shutil.rmtree(temp_dir)

        messagebox.showinfo("Successo", "Cronologia cancellata con successo!")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# Funzione per cancellare le schede recenti di Brave
def cancella_schede_recenti():
    try:
        # Ottieni il percorso corretto della cartella delle sessioni in base al sistema operativo
        path_to_sessions = get_brave_sessions_path()

        # Verifica se il percorso è valido
        if path_to_sessions is None:
            messagebox.showerror("Errore", "Sistema operativo non supportato.")
            return

        # Verifica se la cartella delle sessioni esiste
        if not os.path.exists(path_to_sessions):
            messagebox.showerror("Errore", "Non riesco a trovare la cartella delle sessioni.")
            return

        # Cancella tutti i file nella cartella delle sessioni
        for filename in os.listdir(path_to_sessions):
            file_path = os.path.join(path_to_sessions, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                messagebox.showerror("Errore", f"Non riesco a cancellare {file_path}: {str(e)}")
                return

        messagebox.showinfo("Successo", "Schede recenti cancellate con successo!")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# Funzione per cancellare sia cronologia che schede recenti
def cancella_tutto():
    cancella_cronologia()
    cancella_schede_recenti()

# Funzione per creare la GUI
def crea_gui():
    root = tk.Tk()
    root.title("Cancellazione Cronologia e Schede Recenti di Brave")

    # Etichetta
    label = tk.Label(root, text="Premi il pulsante per cancellare cronologia e schede recenti di Brave")
    label.pack(pady=10)

    # Bottone per cancellare cronologia e schede recenti
    button = tk.Button(root, text="Cancella Tutto", command=cancella_tutto)
    button.pack(pady=20)

    # Avvio della GUI
    root.mainloop()

# Avvia la GUI
crea_gui()
