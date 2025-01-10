import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import csv

class REXIMONApp:
    def __init__(self, root):
        self.root = root
        self.root.title("REXIMON")
        self.root.geometry("400x280")
        self.root.configure(bg="#355E3B")

        self.root.resizable(False, False)

        icon_path = 'Rex.ico'
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Il file {icon_path} non è stato trovato. L'icona non sarà impostata.")

        # Stile
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        self.style.configure("TLabel", background="#355E3B", foreground="white", font=("Arial", 10))
        self.style.configure("TEntry", background="#F0FFF0", foreground="black", font=("Arial", 10))

        # Variabili di classe
        self.original_content = ""
        self.extracted_text = []
        self.extraction_data = []
        self.original_file_path = None
        
        # Frame principale con scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configurare il main_frame per espandersi
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Canvas per la scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg="#355E3B", width=500, height=320)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configurare il canvas per riempire lo spazio disponibile
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Creare la finestra del canvas con il frame scrollabile
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configurare il canvas per usare la scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Binding per gestire il ridimensionamento
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Frame per i delimitatori
        self.delim_frame = ttk.Frame(self.scrollable_frame)
        self.delim_frame.pack(pady=5)
        
        # Lista per tenere traccia delle entries dei delimitatori
        self.delimiter_entries = []
        
        # Primo set di delimitatori
        self.add_delimiter_fields()
        
        # Pulsanti dell'interfaccia
        ttk.Button(self.scrollable_frame, text="Aggiungi Delimitatori", command=self.add_delimiter_fields).pack(pady=5)
        ttk.Button(self.scrollable_frame, text="Apri File Originale", command=self.load_file).pack(pady=10)
        ttk.Button(self.scrollable_frame, text="Estrai Testo", command=self.extract_text).pack(pady=10)
        ttk.Button(self.scrollable_frame, text="Reinserisci Testo Modificato", command=self.reinsert_modified_text).pack(pady=10)

        # Label per il nome del file
        self.file_label = ttk.Label(self.scrollable_frame, text="Nessun file caricato", wraplength=400, anchor="center")
        self.file_label.pack(pady=10)

    def on_frame_configure(self, event=None):
        """Gestisce il ridimensionamento del frame scrollabile"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Gestisce il ridimensionamento del canvas"""
        # Aggiorna la larghezza della finestra del canvas per corrispondere al canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def add_delimiter_fields(self):
        """Aggiunge campi per nuovi delimitatori"""
        frame = ttk.Frame(self.delim_frame)
        frame.pack(pady=2)
        
        start_var = tk.StringVar()
        end_var = tk.StringVar()
        
        ttk.Label(frame, text="Inizio:").pack(side=tk.LEFT, padx=2)
        start_entry = ttk.Entry(frame, textvariable=start_var, width=15)
        start_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(frame, text="Fine:").pack(side=tk.LEFT, padx=2)
        end_entry = ttk.Entry(frame, textvariable=end_var, width=15)
        end_entry.pack(side=tk.LEFT, padx=2)
        
        remove_btn = ttk.Button(frame, text="X", width=2,
                              command=lambda: self.remove_delimiter_fields(frame))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.delimiter_entries.append((start_entry, end_entry, frame))

    def remove_delimiter_fields(self, frame):
        """Rimuove un set di campi delimitatori"""
        if len(self.delimiter_entries) > 1:
            for i, (start, end, f) in enumerate(self.delimiter_entries):
                if f == frame:
                    self.delimiter_entries.pop(i)
                    frame.destroy()
                    break

    def get_all_delimiters(self):
        """Raccoglie tutti i delimitatori validi dalle entries"""
        delimiters = []
        for start_entry, end_entry, _ in self.delimiter_entries:
            start = start_entry.get().strip()
            end = end_entry.get().strip()
            if start or end:
                delimiters.append((start, end))
        return delimiters

    def load_file(self):
        """Carica il file originale"""
        file_path = filedialog.askopenfilename(filetypes=[("Tutti i File", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.original_content = file.read()
                self.original_file_path = file_path
                self.file_label.config(text=f"File caricato: {os.path.basename(file_path)}")
                # Reset delle estrazioni precedenti
                self.extracted_text = []
                self.extraction_data = []
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile caricare il file: {e}")

    def extract_text(self):
        """Estrae il testo usando i delimitatori specificati"""
        if not self.original_content:
            messagebox.showerror("Errore", "Carica un file prima di estrarre il testo.")
            return

        delimiters = self.get_all_delimiters()
        if not delimiters:
            messagebox.showerror("Errore", "Inserisci almeno un set di delimitatori.")
            return

        # Reset delle estrazioni precedenti
        self.extracted_text = []
        self.extraction_data = []

        # Processa ogni linea
        for line_num, line in enumerate(self.original_content.split('\n')):
            for start_delim, end_delim in delimiters:
                if start_delim in line and end_delim in line:
                    try:
                        # Trova tutte le occorrenze nella stessa linea
                        current_pos = 0
                        while True:
                            # Trova la prossima occorrenza del delimitatore di inizio
                            start_pos = line.find(start_delim, current_pos)
                            if start_pos == -1:
                                break
                                
                            # Trova il delimitatore di fine dopo quello di inizio
                            end_pos = line.find(end_delim, start_pos + len(start_delim))
                            if end_pos == -1:
                                break

                            # Estrai il testo tra i delimitatori
                            extracted = line[start_pos + len(start_delim):end_pos].strip()
                            
                            if extracted:
                                # Prepara il testo estratto con il marker
                                marked_text = f"##|{extracted}"
                                
                                # Salva i dati dell'estrazione
                                extraction_info = {
                                    'line_number': line_num,
                                    'line': line,
                                    'start_delim': start_delim,
                                    'end_delim': end_delim,
                                    'extracted_text': extracted,
                                    'start_pos': start_pos,
                                    'end_pos': end_pos + len(end_delim)
                                }
                                
                                # Aggiungi solo se non è già stato estratto
                                if marked_text not in self.extracted_text:
                                    self.extracted_text.append(marked_text)
                                    self.extraction_data.append(extraction_info)
                            
                            # Sposta la posizione corrente dopo il delimitatore di fine
                            current_pos = end_pos + len(end_delim)

                    except Exception as e:
                        print(f"Errore nell'estrazione: {e}")
                        continue

        if self.extracted_text:
            # Salva il testo estratto
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("File di Testo", "*.txt")],
                initialfile="estratto_testo.txt"
            )
            if save_path:
                try:
                    with open(save_path, "w", encoding="utf-8") as file:
                        file.write("\n".join(self.extracted_text))
                    messagebox.showinfo("Successo", f"Testo estratto salvato in: {save_path}")
                except Exception as e:
                    messagebox.showerror("Errore", f"Impossibile salvare il file: {e}")
        else:
            messagebox.showinfo("Info", "Nessun testo estratto. Verifica i delimitatori.")

    def reinsert_modified_text(self):
        """Reinserisce il testo modificato nel file originale"""
        if not self.extracted_text or not self.extraction_data:
            messagebox.showerror("Errore", "Nessun testo estratto da reinserire.")
            return

        # Carica il file modificato
        modified_file_path = filedialog.askopenfilename(
            filetypes=[("File di Testo", "*.txt")]
        )
        if not modified_file_path:
            return

        try:
            # Leggi il file modificato
            with open(modified_file_path, 'r', encoding='utf-8') as file:
                modified_lines = [line.strip() for line in file.readlines()]

            # Verifica il formato
            if not all(line.startswith("##|") for line in modified_lines):
                messagebox.showerror("Errore", "Il file modificato non è nel formato corretto (##|).")
                return

            # Rimuovi il marker ##| dai testi modificati
            modified_texts = [line[3:] for line in modified_lines]  # Rimuove "##|"

            # Prepara il contenuto per la sostituzione
            lines = self.original_content.split('\n')
            
            # Per ogni modifica da applicare
            for mod_text, extraction_info in zip(modified_texts, self.extraction_data):
                line_num = extraction_info['line_number']
                line = extraction_info['line']
                start_delim = extraction_info['start_delim']
                end_delim = extraction_info['end_delim']
                
                # Costruisci il nuovo testo con i delimitatori
                new_text = f"{start_delim}{mod_text}{end_delim}"
                
                # Sostituisci il testo originale nella linea
                old_text = line[extraction_info['start_pos']:extraction_info['end_pos']]
                lines[line_num] = lines[line_num].replace(old_text, new_text)

            # Unisci le linee modificate
            modified_content = '\n'.join(lines)

            # Salva il file modificato
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("File di Testo", "*.txt")]
            )
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                messagebox.showinfo("Successo", "File modificato salvato con successo!")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il reinserimento: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = REXIMONApp(root)
    root.mainloop()
