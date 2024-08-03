import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        input_file.set(file_path)

def split_video():
    file_path = input_file.get()
    if not file_path:
        messagebox.showerror("Errore", "Seleziona un file MP4 da dividere.")
        return

    if not os.path.isfile(file_path):
        messagebox.showerror("Errore", f"Il file '{file_path}' non esiste.")
        return

    # Definisci la durata dei segmenti in secondi (10 minuti)
    segment_duration = 600  

    # Directory di output per i segmenti e la playlist
    output_dir = os.path.splitext(os.path.basename(file_path))[0] + "_segments"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # File M3U8 di output
    output_playlist = os.path.join(output_dir, "playlist.m3u8")

    # Comando ffmpeg per segmentare il video e creare la playlist M3U8
    command = [
        "ffmpeg", "-i", file_path, "-c", "copy", "-map", "0",
        "-f", "segment", "-segment_time", str(segment_duration),
        "-segment_list", output_playlist, 
        "-segment_format", "mpegts", os.path.join(output_dir, "segment%03d.ts")
    ]

    subprocess.run(command)

    messagebox.showinfo("Completato", f"Divisione completata e playlist creata con successo in {output_dir}")

# Crea la finestra principale
root = tk.Tk()
root.title("Divisione Video MP4")

# Variabile per il percorso del file di input
input_file = tk.StringVar()

# Layout della UI
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Seleziona un file MP4:")
label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, textvariable=input_file, width=50)
entry.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Sfoglia", command=select_file)
button_browse.grid(row=0, column=2, padx=5, pady=5)

button_split = tk.Button(frame, text="Dividi", command=split_video)
button_split.grid(row=1, column=0, columnspan=3, pady=10)

# Avvia l'applicazione
root.mainloop()
