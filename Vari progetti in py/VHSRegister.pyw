import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import threading
import time

class VHSRegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VHS Register")
        self.root.geometry("500x520")  # Ottimizza la dimensione della finestra
        self.root.config(bg="#2F4F4F")
        self.root.resizable(False, False)

        # Percorso di ffmpeg (assicurati che il percorso di ffmpeg.exe sia corretto)
        self.ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
        
        # Variabili per la registrazione
        self.recording = False
        self.processes = []
        self.recorded_files = []

        # Creazione della GUI
        self.create_widgets()

    def create_widgets(self):
        # Titolo retro
        title_label = tk.Label(self.root, text="VHS Register", font=("Courier New", 20, "bold"), fg="#00FF00", bg="#2F4F4F")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # URL Entry
        url_frame = tk.Frame(self.root, bg="#2F4F4F")
        url_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        
        self.url_entry = tk.Entry(url_frame, font=("Courier New", 12), width=40, bg="#333333", fg="#FFFFFF", bd=2, relief="sunken")
        self.url_entry.grid(row=0, column=0, padx=10, sticky="ew")
        
        # Aggiungi URL Button sotto al titolo
        add_button = ttk.Button(self.root, text="Aggiungi URL", command=self.add_url, style="Retro.TButton")
        add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Listbox per visualizzare i file registrati
        self.file_listbox = tk.Listbox(self.root, height=10, width=50, font=("Courier New", 12), bg="#333333", fg="#FFFFFF", bd=2, relief="sunken")
        self.file_listbox.grid(row=3, column=0, columnspan=2, pady=10)

        # Pulsanti retro
        button_frame = tk.Frame(self.root, bg="#2F4F4F")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20, padx=30, sticky="ew")

        self.record_button = ttk.Button(button_frame, text="Avvia Registrazione Selezionata", command=self.start_selected_recording, style="Retro.TButton")
        self.record_button.grid(row=0, column=0, padx=10, pady=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Registrazione Selezionata", command=self.stop_selected_recording, style="Retro.TButton", state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=5)

        # Pulsanti Converti e Cancella affiancati
        self.delete_button = ttk.Button(button_frame, text="Cancella URL Selezionato", command=self.delete_selected_url, style="Retro.TButton")
        self.delete_button.grid(row=1, column=0, padx=10, pady=5)

        self.convert_button = ttk.Button(button_frame, text="Converti Selezionato in MP4", command=self.convert_selected_to_mp4, style="Retro.TButton", state=tk.DISABLED)
        self.convert_button.grid(row=1, column=1, padx=10, pady=5)

        # Timer per la registrazione
        self.timer_label = tk.Label(self.root, text="Tempo: 00:00", font=("Courier New", 12), fg="#00FF00", bg="#2F4F4F")
        self.timer_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Menu contestuale per incollare l'URL
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Incolla Link", command=self.paste_url)

        # Associa il tasto destro al menu contestuale
        self.file_listbox.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Mostra il menu contestuale per incollare un URL."""
        self.context_menu.post(event.x_root, event.y_root)

    def paste_url(self):
        """Incolla un URL dalla clipboard nella Entry."""
        url = self.root.clipboard_get()
        if url:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(tk.END, url)

    def add_url(self):
        """Aggiungi un URL alla lista."""
        url = self.url_entry.get().strip()
        if url:
            self.file_listbox.insert(tk.END, url)
            self.url_entry.delete(0, tk.END)

    def delete_selected_url(self):
        """Cancella l'URL selezionato dalla lista."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            url = self.file_listbox.get(selected_index)
            # Chiedi conferma prima di cancellare
            confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler cancellare l'URL: {url}?")
            if confirm:
                self.file_listbox.delete(selected_index)
                messagebox.showinfo("Info", f"URL {url} cancellato.")
        else:
            messagebox.showwarning("Attenzione", "Seleziona un URL per cancellarlo.")

    def update_timer(self):
        """Aggiorna il timer della registrazione."""
        if self.recording:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"Tempo: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def start_selected_recording(self):
        """Avvia la registrazione per il link selezionato."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            url = self.file_listbox.get(selected_index)
            self.recording = True
            self.start_time = time.time()  # Inizia il timer
            self.update_timer()
            self.record_video(url)
            
            # Disabilita i pulsanti appropriati
            self.record_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.convert_button.config(state=tk.DISABLED)

    def stop_selected_recording(self):
        """Ferma la registrazione selezionata."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            url = self.file_listbox.get(selected_index)
            # Trova il processo associato a questo URL e fermalo
            for process in self.processes:
                if process.args[2] == url:  # Controlla se il link è quello giusto
                    process.terminate()
                    self.processes.remove(process)
                    break
            self.recording = False
            self.stop_button.config(state=tk.DISABLED)
            self.convert_button.config(state=tk.NORMAL)
            messagebox.showinfo("Info", f"Registrazione per {url} fermata")

    def record_video(self, url):
        """Registra il video per un URL specificato."""
        output_file = f"recording_{int(time.time())}.ts"
        command = [self.ffmpeg_path, "-i", url, "-c", "copy", output_file]
        process = subprocess.Popen(command)
        self.processes.append(process)
        self.recorded_files.append(output_file)
        self.file_listbox.insert(tk.END, output_file)

    def convert_selected_to_mp4(self):
        """Converte il file selezionato in MP4 e cancella il file .ts originale."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            filename = self.file_listbox.get(selected_index)
            if filename.endswith(".ts"):
                output_file = filename.replace(".ts", ".mp4")
                try:
                    subprocess.run([self.ffmpeg_path, "-i", filename, "-c", "copy", output_file], check=True)
                    # Cancella il file .ts dopo la conversione
                    os.remove(filename)
                    self.file_listbox.delete(selected_index)  # Rimuovi il file dalla lista
                    messagebox.showinfo("Info", f"Conversione completata e file {filename} eliminato.")
                except subprocess.CalledProcessError:
                    messagebox.showerror("Errore", "Si è verificato un errore durante la conversione.")
            else:
                messagebox.showwarning("Attenzione", "Seleziona un file .ts per la conversione.")
        else:
            messagebox.showwarning("Attenzione", "Seleziona un file per la conversione.")

def run_app():
    root = tk.Tk()
    app = VHSRegisterApp(root)
    root.mainloop()

run_app()
