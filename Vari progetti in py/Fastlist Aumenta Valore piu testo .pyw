import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import ttkbootstrap as ttk # Importa ttkbootstrap
from ttkbootstrap.constants import * # Per costanti come PRIMARY, SUCCESS, INFO
import re

class AumentaValoreM3UApp: # Nome classe cambiato
    def __init__(self, root_window):
        self.style = ttk.Style(theme="litera") 
        self.root = self.style.master 
        self.root.title("Aumenta Valore M3U") # Titolo finestra cambiato
        
        # Imposta dimensioni e centra la finestra
        window_width = 800
        window_height = 900
        self.root.geometry(f"{window_width}x{window_height}")
        self.center_window(window_width, window_height)

        main_frame = ttk.Frame(self.root, padding="15 15 15 15") 
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_rowconfigure(3, weight=1)  
        main_frame.grid_rowconfigure(6, weight=1)  
        main_frame.grid_columnconfigure(0, weight=1) 

        app_title = ttk.Label(main_frame, text="Aumenta Valore - Processore M3U", font=("Helvetica", 16, "bold")) # Titolo interno cambiato
        app_title.grid(row=0, column=0, pady=(0, 15), sticky="w")

        guide_button = ttk.Button(main_frame, text="Guida", command=self.show_guide, bootstyle="info-outline")
        guide_button.grid(row=0, column=0, pady=(0,15), padx=(0,5), sticky="e")

        placeholder_frame = ttk.Labelframe(main_frame, text="Configurazione", padding="10 10 10 10")
        placeholder_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        placeholder_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(placeholder_frame, text="Segnaposto nel titolo #EXTINF:").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.placeholder_var = tk.StringVar(value="[x]")
        self.placeholder_entry = ttk.Entry(placeholder_frame, textvariable=self.placeholder_var, width=20, bootstyle="primary")
        self.placeholder_entry.grid(row=0, column=1, pady=5, sticky="ew")

        input_label_frame = ttk.Labelframe(main_frame, text="Testo di Input (formato M3U)", padding="10 10 10 10")
        input_label_frame.grid(row=2, column=0, sticky="nsew", pady=(0,10))
        input_label_frame.grid_rowconfigure(0, weight=1)
        input_label_frame.grid_columnconfigure(0, weight=1)
        
        self.input_text_widget = scrolledtext.ScrolledText(input_label_frame, height=10, width=80, relief=tk.FLAT, borderwidth=1, font=("Consolas", 10))
        self.input_text_widget.grid(row=0, column=0, sticky="nsew")
        
        load_file_button = ttk.Button(input_label_frame, text="Carica da File...", command=self.load_text_from_file, bootstyle="secondary")
        load_file_button.grid(row=1, column=0, pady=(10,0), sticky="e")

        self.process_button = ttk.Button(main_frame, text="Processa Testo", command=self.process_text, bootstyle="success")
        self.process_button.grid(row=4, column=0, pady=15, ipady=5, sticky="ew") 

        output_label_frame = ttk.Labelframe(main_frame, text="Output Generato", padding="10 10 10 10")
        output_label_frame.grid(row=5, column=0, sticky="nsew", pady=(0,10))
        output_label_frame.grid_rowconfigure(0, weight=1)
        output_label_frame.grid_columnconfigure(0, weight=1)

        self.output_text_widget = scrolledtext.ScrolledText(output_label_frame, height=10, width=80, relief=tk.FLAT, borderwidth=1, font=("Consolas", 10))
        self.output_text_widget.grid(row=0, column=0, sticky="nsew")
        
        output_management_frame = ttk.Frame(output_label_frame)
        output_management_frame.grid(row=1, column=0, sticky="ew", pady=(10,0))
        output_management_frame.grid_columnconfigure(0, weight=1) 
        output_management_frame.grid_columnconfigure(1, weight=1)
        output_management_frame.grid_columnconfigure(2, weight=1)

        self.copy_output_button = ttk.Button(output_management_frame, text="Copia Output", command=self.copia_output, bootstyle="primary-outline")
        self.copy_output_button.grid(row=0, column=0, padx=(0,5), sticky="ew")

        self.save_output_button = ttk.Button(output_management_frame, text="Salva Output...", command=self.salva_output, bootstyle="primary-outline")
        self.save_output_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.clear_output_button = ttk.Button(output_management_frame, text="Pulisci Output", command=self.pulisci_output, bootstyle="danger-outline")
        self.clear_output_button.grid(row=0, column=2, padx=(5,0), sticky="ew")

    def center_window(self, width, height):
        # Ottieni le dimensioni dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcola la posizione x e y per centrare la finestra
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f'{width}x{height}+{x}+{y}')


    def show_guide(self):
        guide_text = """
Guida Rapida - Aumenta Valore M3U

1. Segnaposto:
   - Inserisci nel campo "Segnaposto nel titolo #EXTINF" 
     la stringa esatta che vuoi rimpiazzare all'interno 
     delle righe `#EXTINF` (es. [x], {{NUM}}, ecc.).

2. Testo di Input:
   - Clicca "Carica da File..." per selezionare un file 
     .m3u o .txt.
   - Oppure, incolla direttamente il contenuto del tuo file 
     M3U nell'area di testo.
   - Il file dovrebbe contenere blocchi di informazioni per 
     ciascuna traccia, tipicamente:
     #EXTINF:durata,Titolo con [segnaposto]
     #EXTVLCOPT:opzioni (opzionale)
     http://.../nome_file_con_numero_episodio.mp4

3. Processa Testo:
   - Clicca il bottone "Processa Testo".
   - Il programma analizzerà ogni blocco:
     a. Cercherà un URL che termini con .mp4, .mkv, 
        .avi, o .ts.
     b. Estrarrà un numero dal nome del file (es. da 
        "Ep_007_ITA.mp4" estrarrà "7").
     c. Sostituirà il segnaposto nel titolo `#EXTINF` 
        con il numero estratto.
   - Se un numero non può essere estratto o l'URL non è 
     trovato, il blocco originale verrà mantenuto.

4. Output:
   - Il testo processato apparirà nell'area "Output Generato".
   - Puoi usare "Copia Output" o "Salva Output...".
   - "Pulisci Output" cancella l'area di output.

Esempio:
Input nel file:
  #EXTINF:-1,Episodio [ID]
  https://.../Serie_Ep_015.mp4
Segnaposto inserito nella GUI: [ID]
Output generato:
  #EXTINF:-1,Episodio 15
  https://.../Serie_Ep_015.mp4
        """
        messagebox.showinfo("Guida Utente", guide_text, parent=self.root)


    def load_text_from_file(self):
        filepath = filedialog.askopenfilename(
            parent=self.root, 
            title="Apri file M3U o Testo",
            filetypes=(("File M3U", "*.m3u"),("File di testo", "*.txt"), ("Tutti i file", "*.*"))
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.input_text_widget.delete("1.0", tk.END)
                    self.input_text_widget.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Errore Lettura File", f"Impossibile leggere il file:\n{e}", parent=self.root)

    def process_text(self):
        input_text = self.input_text_widget.get("1.0", tk.END)
        placeholder_to_replace = self.placeholder_var.get().strip()

        if not placeholder_to_replace:
            messagebox.showerror("Errore", "Per favore, definisci il segnaposto da sostituire (es. [x]).", parent=self.root)
            return
        
        if not input_text.strip():
            messagebox.showinfo("Info", "Il testo di input è vuoto.", parent=self.root)
            return

        url_number_regex = re.compile(
            r"(?:_Ep_|_episode_|Episodio_|Season_|S\d{1,2}Ep\d{1,2}_|_)(\d+)(?:_ITA)?\.(?:mp4|mkv|avi|ts)|" 
            r"[/_-](\d{1,4})[^/]*\.(?:mp4|mkv|avi|ts)"                         
        , re.IGNORECASE)

        processed_text_parts = []
        
        if input_text.startswith("#EXTM3U"):
            first_newline = input_text.find('\n')
            if first_newline != -1:
                processed_text_parts.append(input_text[:first_newline + 1])
                input_text_for_blocks = input_text[first_newline + 1:]
            else: 
                processed_text_parts.append(input_text)
                input_text_for_blocks = ""
        else:
            input_text_for_blocks = input_text

        last_block_end = 0
        for block_match in re.finditer(
            r"(#EXTINF:[^\n]+(?:\n#EXTVLCOPT:[^\n]+)*\n(?:[^\s#][^\n]*\.(?:mp4|mkv|avi|ts))[^\n]*)",
            input_text_for_blocks,
            re.MULTILINE | re.IGNORECASE
        ):
            processed_text_parts.append(input_text_for_blocks[last_block_end:block_match.start()])
            
            block_text = block_match.group(1).strip()
            last_block_end = block_match.end()
            block_lines = block_text.split('\n')
            
            if not block_lines: 
                processed_text_parts.append(block_text)
                continue

            extinf_line = ""
            url_line = ""
            new_extinf_line_index = -1

            for i, line_in_block in enumerate(block_lines):
                if line_in_block.startswith("#EXTINF:"):
                    extinf_line = line_in_block
                    new_extinf_line_index = i
                elif line_in_block.lower().endswith((".mp4", ".mkv", ".avi", ".ts")): # Cerca l'URL
                    url_line = line_in_block
            
            if extinf_line and url_line and new_extinf_line_index != -1:
                num_match = url_number_regex.search(url_line)
                if num_match:
                    extracted_number_str = next((g for g in num_match.groups() if g is not None), None)
                    if extracted_number_str:
                        try:
                            episode_number = int(extracted_number_str)
                            modified_extinf = extinf_line.replace(placeholder_to_replace, str(episode_number))
                            block_lines[new_extinf_line_index] = modified_extinf
                            processed_text_parts.append("\n".join(block_lines))
                        except ValueError:
                            processed_text_parts.append(block_text) 
                    else:
                        processed_text_parts.append(block_text) 
                else:
                    processed_text_parts.append(block_text) 
            else:
                processed_text_parts.append(block_text) 
        
        processed_text_parts.append(input_text_for_blocks[last_block_end:])
        self.output_text_widget.delete("1.0", tk.END)
        final_output_str = "".join(processed_text_parts)
        final_output_str = re.sub(r'\n{3,}', '\n\n', final_output_str.strip())

        self.output_text_widget.insert("1.0", final_output_str + "\n" if final_output_str else "")
        messagebox.showinfo("Successo", "Testo processato!", parent=self.root)

    def pulisci_output(self):
        if self.output_text_widget.get("1.0", tk.END).strip():
            if messagebox.askyesno("Conferma", "Sei sicuro di voler cancellare tutto l'output?", parent=self.root):
                self.output_text_widget.delete("1.0", tk.END)

    def copia_output(self):
        testo_output = self.output_text_widget.get("1.0", tk.END).strip()
        if testo_output:
            self.root.clipboard_clear()
            self.root.clipboard_append(testo_output)
            messagebox.showinfo("Copiato", "Il contenuto dell'output è stato copiato negli appunti.", parent=self.root)
        else:
            messagebox.showinfo("Info", "L'area di output è vuota. Nulla da copiare.", parent=self.root)

    def salva_output(self):
        testo_output = self.output_text_widget.get("1.0", tk.END).strip()
        if not testo_output:
            messagebox.showinfo("Info", "L'area di output è vuota. Nulla da salvare.", parent=self.root)
            return

        percorso_file = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".m3u", 
            filetypes=(("File M3U", "*.m3u"),("File di testo", "*.txt"), ("Tutti i file", "*.*")),
            title="Salva output come..."
        )
        if percorso_file:
            try:
                with open(percorso_file, "w", encoding="utf-8", newline='\n') as file:
                    file.write(self.output_text_widget.get("1.0", tk.END).rstrip('\n') + '\n')
                messagebox.showinfo("Salvato", f"L'output è stato salvato in:\n{percorso_file}", parent=self.root)
            except Exception as e:
                messagebox.showerror("Errore di Salvataggio", f"Non è stato possibile salvare il file.\nErrore: {e}", parent=self.root)

if __name__ == '__main__':
    app = AumentaValoreM3UApp(None) # Nome classe cambiato
    app.root.mainloop()