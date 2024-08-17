import os
import tkinter as tk
from tkinter import messagebox, ttk
import psutil

# Funzione per pulire i file temporanei
def pulisci_file_temporanei():
    temp_path = os.getenv('TEMP')
    eliminati = []
    non_eliminati = []
    
    # Mostra una barra di progresso
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(os.listdir(temp_path)) if os.path.exists(temp_path) else 100
    
    try:
        for root_dir, dirs, files in os.walk(temp_path):  # Evita di sovrascrivere "root"
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    os.remove(file_path)
                    eliminati.append(file_path)
                except Exception as e:
                    non_eliminati.append((file_path, str(e)))
                
                # Aggiorna la barra di progresso
                progress_bar["value"] += 1
                root.update_idletasks()  # Usa "root" correttamente qui
        
        # Mostra i risultati
        risultato = f"File eliminati:\n{len(eliminati)} file eliminati\n"
        risultato += f"{len(non_eliminati)} file non eliminati\n"
        if non_eliminati:
            risultato += "\nFile non eliminati:\n" + "\n".join([f"{file}: {errore}" for file, errore in non_eliminati])
        
        messagebox.showinfo("Risultato", risultato)
    
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {e}")
    finally:
        progress_bar["value"] = 0  # Resetta la barra di progresso

# Funzione per chiudere i processi inutili
def chiudi_processi_inutili():
    processi_chiusi = []
    
    # Mostra una barra di progresso
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(list(psutil.process_iter(['pid', 'name'])))
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processi_da_chiudere = ['notepad.exe', 'calculator.exe']  # Aggiungi processi inutili
            if proc.info['name'] in processi_da_chiudere:
                os.kill(proc.info['pid'], 9)
                processi_chiusi.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
        # Aggiorna la barra di progresso
        progress_bar["value"] += 1
        root.update_idletasks()  # Usa "root" correttamente qui
    
    if processi_chiusi:
        risultato = f"Processi chiusi:\n" + "\n".join(processi_chiusi)
    else:
        risultato = "Nessun processo chiuso."
    
    messagebox.showinfo("Risultato", risultato)
    progress_bar["value"] = 0  # Resetta la barra di progresso

# Funzione per liberare memoria (simulata)
def libera_memoria():
    try:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_full_info()
        memoria_liberata = mem_info.uss / (1024 * 1024)  # Converti in MB
        
        messagebox.showinfo("Memoria Ottimizzata", f"Memoria liberata: {memoria_liberata:.2f} MB")
    
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {e}")

# Creazione della finestra principale
root = tk.Tk()
root.title("Ottimizzatore PC")

# Aggiungi un'icona (assicurati di avere un file icona .ico nel percorso indicato)
# root.iconbitmap('percorso/della/tua/icona.ico')

# Imposta dimensioni della finestra
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Etichetta titolo
title_label = tk.Label(root, text="Ottimizzatore PC", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# Barra di progresso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Pulsanti per le varie operazioni
btn_pulisci_temp = tk.Button(root, text="Pulisci file temporanei", command=pulisci_file_temporanei, bg="#4CAF50", fg="white", font=("Helvetica", 12))
btn_pulisci_temp.pack(pady=10)

btn_chiudi_processi = tk.Button(root, text="Chiudi processi inutili", command=chiudi_processi_inutili, bg="#FF5722", fg="white", font=("Helvetica", 12))
btn_chiudi_processi.pack(pady=10)

btn_libera_memoria = tk.Button(root, text="Libera memoria", command=libera_memoria, bg="#2196F3", fg="white", font=("Helvetica", 12))
btn_libera_memoria.pack(pady=10)

# Esecuzione della finestra principale
root.mainloop()
