import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import re
import json
import os
import webbrowser
from datetime import datetime, timedelta # Aggiunto timedelta

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Percorso a VLC (si può modificare dalle impostazioni)
DEFAULT_VLC_PATH = r"D:\Programmi\VLCPortable\vlc\vlc.exe" # Modifica se necessario
# Percorso a Brave (si può modificare dalle impostazioni)
DEFAULT_BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" # Modifica se necessario

# Regex di fallback per trovare URL .m3u8 nel sorgente o nei log
M3U8_REGEX = re.compile(r'(https?://[^" \?]+?\.m3u8[^"]*)')

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Impostazioni")
        self.geometry("500x350")
        self.resizable(False, False)
        self.config_data = config # Rinominato per chiarezza, per evitare collisioni con il metodo config() dei widget
        self.result = None
        
        # Applica tema
        style = ttk.Style(self)
        # Usa uno stile specifico per il Toplevel SettingsDialog per evitare conflitti
        # con gli stili globali dell'applicazione principale.
        settings_style_prefix = "SettingsDialog." 
        frame_style = settings_style_prefix + "TFrame"
        label_style = settings_style_prefix + "TLabel"
        button_style = settings_style_prefix + "TButton"
        checkbutton_style = settings_style_prefix + "TCheckbutton"
        labelframe_style = settings_style_prefix + "TLabelframe"

        if parent.dark_mode.get():
            self.configure(bg="#333333")
            style.configure(frame_style, background="#333333")
            style.configure(label_style, background="#333333", foreground="white")
            style.configure(button_style, background="#555555", foreground="white")
            style.map(button_style, background=[('active', '#666666')])
            style.configure(checkbutton_style, background="#333333", foreground="white", indicatorcolor="#555555")
            style.map(checkbutton_style, indicatorcolor=[('selected', "#bbbbbb")])
            style.configure(labelframe_style, background="#333333", foreground="white", bordercolor="#555555")
            style.configure(labelframe_style + ".Label", background="#333333", foreground="white") # Etichetta del LabelFrame
            # Entry e Spinbox usano il fieldbackground globale, che è già impostato in HLSQueueApp._apply_theme
            # Se si vuole un fieldbackground specifico per SettingsDialog, impostarlo qui
            # style.configure(settings_style_prefix + "TEntry", fieldbackground="#2b2b2b", foreground="white")
            # style.configure(settings_style_prefix + "TSpinbox", fieldbackground="#2b2b2b", foreground="white")
        else:
            self.configure(bg="#f0f0f0")
            style.configure(frame_style, background="#f0f0f0")
            style.configure(label_style, background="#f0f0f0", foreground="black")
            style.configure(button_style, background="#e0e0e0", foreground="black")
            style.map(button_style, background=[('active', '#d0d0d0')])
            style.configure(checkbutton_style, background="#f0f0f0", foreground="black") # indicatorcolor di default
            style.configure(labelframe_style, background="#f0f0f0", foreground="black")
            style.configure(labelframe_style + ".Label", background="#f0f0f0", foreground="black")
        
        # Crea il frame principale
        main_frame = ttk.Frame(self, padding=10, style=frame_style)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # VLC Path
        ttk.Label(main_frame, text="Percorso VLC:", style=label_style).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vlc_path_var = tk.StringVar(value=self.config_data.get("vlc_path", DEFAULT_VLC_PATH))
        vlc_entry = ttk.Entry(main_frame, textvariable=self.vlc_path_var, width=40) # style=settings_style_prefix + "TEntry"
        vlc_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5)
        ttk.Button(main_frame, text="Sfoglia", command=lambda: self._browse_file(self.vlc_path_var), style=button_style).grid(row=0, column=2)
        
        # Browser Path
        ttk.Label(main_frame, text="Percorso Browser:", style=label_style).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.browser_path_var = tk.StringVar(value=self.config_data.get("browser_path", DEFAULT_BRAVE_PATH))
        browser_entry = ttk.Entry(main_frame, textvariable=self.browser_path_var, width=40) # style=settings_style_prefix + "TEntry"
        browser_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5)
        ttk.Button(main_frame, text="Sfoglia", command=lambda: self._browse_file(self.browser_path_var), style=button_style).grid(row=1, column=2)
        
        # Timeout
        ttk.Label(main_frame, text="Timeout caricamento (sec):", style=label_style).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.IntVar(value=self.config_data.get("timeout", 20))
        timeout_entry = ttk.Spinbox(main_frame, from_=5, to=120, increment=5, textvariable=self.timeout_var, width=5) # style=settings_style_prefix + "TSpinbox"
        timeout_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Cronologia
        ttk.Label(main_frame, text="Mantieni cronologia (giorni):", style=label_style).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.history_days_var = tk.IntVar(value=self.config_data.get("history_days", 30))
        history_entry = ttk.Spinbox(main_frame, from_=0, to=365, increment=1, textvariable=self.history_days_var, width=5) # style=settings_style_prefix + "TSpinbox"
        history_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Opzioni avanzate
        advanced_frame = ttk.LabelFrame(main_frame, text="Opzioni avanzate", style=labelframe_style)
        advanced_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        
        # Auto avvio VLC
        self.auto_start_var = tk.BooleanVar(value=self.config_data.get("auto_start_vlc", True))
        ttk.Checkbutton(advanced_frame, text="Avvia/riutilizza automaticamente VLC", variable=self.auto_start_var, style=checkbutton_style).pack(anchor=tk.W, pady=2, padx=5)
        
        # Preferisci index-v1
        self.prefer_index_var = tk.BooleanVar(value=self.config_data.get("prefer_index", True))
        ttk.Checkbutton(advanced_frame, text="Preferisci stream index-v1 / variant", variable=self.prefer_index_var, style=checkbutton_style).pack(anchor=tk.W, pady=2, padx=5)
        
        # Log dettagliato
        self.verbose_log_var = tk.BooleanVar(value=self.config_data.get("verbose_log", False))
        ttk.Checkbutton(advanced_frame, text="Log dettagliato nella status bar", variable=self.verbose_log_var, style=checkbutton_style).pack(anchor=tk.W, pady=2, padx=5)
        
        # Pulsanti
        button_frame = ttk.Frame(self, style=frame_style)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Salva", command=self._save, style=button_style).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.destroy, style=button_style).pack(side=tk.RIGHT, padx=5)
        
        # Rendi la finestra modale
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self) # Assicura che il flusso si fermi qui
        
    def _browse_file(self, string_var):
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if path:
            string_var.set(path)
            
    def _save(self):
        self.result = {
            "vlc_path": self.vlc_path_var.get(),
            "browser_path": self.browser_path_var.get(),
            "timeout": self.timeout_var.get(),
            "history_days": self.history_days_var.get(),
            "auto_start_vlc": self.auto_start_var.get(),
            "prefer_index": self.prefer_index_var.get(),
            "verbose_log": self.verbose_log_var.get()
        }
        self.destroy()

class HLSQueueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HLS Stream Queue Pro")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Carica configurazione
        self.config_file = os.path.join(os.path.expanduser("~"), ".hls_queue_config.json")
        self.app_config = self._load_config() # Rinominato per evitare collisione con il metodo config() dei widget
        
        # Cronologia
        self.history_file = os.path.join(os.path.expanduser("~"), ".hls_queue_history.json")
        self.history = self._load_history()
        
        # Tema (variabile creata, ma applicazione del tema spostata dopo la UI)
        self.dark_mode = tk.BooleanVar(value=self.app_config.get("dark_mode", False))
        
        # Setup UI
        self._create_menu()
        self._create_main_ui() # self.text_area e altri widget vengono creati qui
        
        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
                
        self.status_var = tk.StringVar(value="Pronto")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, padding=(5, 2))
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, mode="determinate", length=200)

        # APPLICA IL TEMA QUI, DOPO CHE TUTTI I WIDGET PRINCIPALI SONO STATI CREATI
        self._apply_theme() 
        
        # Prepara Selenium (inizializzato solo quando serve)
        self.driver = None
        self.streams_found = [] # Lista di URL stringa
        
    def _create_menu(self):
        self.menubar = tk.Menu(self)
        
        # Menu File
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Nuovo", command=self._new_session, accelerator="Ctrl+N")
        file_menu.add_command(label="Apri...", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Salva lista URL...", command=self._save_url_list_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.bind_all("<Control-n>", lambda event: self._new_session())
        self.bind_all("<Control-o>", lambda event: self.load_file())
        self.bind_all("<Control-s>", lambda event: self._save_url_list_file())
        
        # Menu Strumenti
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="Processa e Metti in Coda", command=self.process_and_queue, accelerator="F5")
        tools_menu.add_command(label="Processa Senza Accodare", command=lambda: self.process_and_queue(queue=False), accelerator="Shift+F5")
        tools_menu.add_separator()
        tools_menu.add_command(label="Pulisci Lista URL", command=lambda: self.text_area.delete('1.0', tk.END))
        tools_menu.add_command(label="Pulisci Risultati Stream", command=self._clear_results)
        tools_menu.add_separator()
        tools_menu.add_command(label="Mostra Cronologia", command=self._show_history, accelerator="Ctrl+H")
        self.menubar.add_cascade(label="Strumenti", menu=tools_menu)
        self.bind_all("<F5>", lambda event: self.process_and_queue())
        self.bind_all("<Shift-F5>", lambda event: self.process_and_queue(queue=False))
        self.bind_all("<Control-h>", lambda event: self._show_history())

        # Menu Impostazioni
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        settings_menu.add_checkbutton(label="Modalità Scura", variable=self.dark_mode, command=self._toggle_theme)
        settings_menu.add_separator()
        settings_menu.add_command(label="Impostazioni...", command=self._open_settings)
        self.menubar.add_cascade(label="Impostazioni", menu=settings_menu)
        
        # Menu Aiuto
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Istruzioni", command=self._show_help, accelerator="F1")
        help_menu.add_command(label="Info", command=self._show_about)
        self.menubar.add_cascade(label="Aiuto", menu=help_menu)
        self.bind_all("<F1>", lambda event: self._show_help())
        
        self.configure(menu=self.menubar) # CORREZIONE APPLICATA QUI
        
    def _create_main_ui(self):
        # Frame principale con padding
        main_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="URLs da processare (uno per riga)")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text area con scroll
        self.text_area = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aggiungi menu contestuale al text area
        self._add_text_context_menu()
        
        # Bottoni principali
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="🗁 Carica da file", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Da appunti", command=self._paste_from_clipboard).pack(side=tk.LEFT, padx=5)
        self.process_button = ttk.Button(btn_frame, 
                   text="▶ Processa e Metti in Coda", 
                   command=self.process_and_queue)
        self.process_button.pack(side=tk.RIGHT, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Stream HLS trovati")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview per visualizzare i risultati
        columns = ("url", "tipo", "qualità", "origine")
        self.result_tree = ttk.Treeview(output_frame, columns=columns, show="headings", height=6)
        
        # Definisci intestazioni
        self.result_tree.heading("url", text="URL Stream")
        self.result_tree.heading("tipo", text="Tipo")
        self.result_tree.heading("qualità", text="Qualità")
        self.result_tree.heading("origine", text="Origine")
        
        # Definisci larghezze colonne
        self.result_tree.column("url", width=350, anchor="w")
        self.result_tree.column("tipo", width=80, anchor="center") 
        self.result_tree.column("qualità", width=80, anchor="center")
        self.result_tree.column("origine", width=100, anchor="center")
        
        # Scrollbar per il treeview
        result_scroll_y = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        result_scroll_x = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=result_scroll_y.set, xscrollcommand=result_scroll_x.set)
        
        # Pack treeview and scrollbar
        result_scroll_y.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=(5,0)) # pady per allineare con xbar
        result_scroll_x.pack(side=tk.BOTTOM, fill=tk.X, padx=(5,0), pady=(0,5)) # padx per allineare con ybar
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=(5,0)) # pady bottom per xbar
        
        # Aggiungi menu contestuale al treeview
        self._add_tree_context_menu()
        # Doppioclick per aprire in VLC
        self.result_tree.bind("<Double-1>", lambda event: self._send_to_vlc())

    def _add_text_context_menu(self):
        text_context_menu = tk.Menu(self.text_area, tearoff=0)
        text_context_menu.add_command(label="Taglia", command=lambda: self._text_cut(), accelerator="Ctrl+X")
        text_context_menu.add_command(label="Copia", command=lambda: self._text_copy(), accelerator="Ctrl+C")
        text_context_menu.add_command(label="Incolla", command=lambda: self._text_paste(), accelerator="Ctrl+V")
        text_context_menu.add_separator()
        text_context_menu.add_command(label="Seleziona tutto", command=lambda: self.text_area.tag_add(tk.SEL, "1.0", tk.END), accelerator="Ctrl+A")
        
        def show_text_context_menu(event):
            # Abilita/disabilita opzioni basate sulla selezione
            try:
                self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                text_context_menu.entryconfigure("Taglia", state=tk.NORMAL)
                text_context_menu.entryconfigure("Copia", state=tk.NORMAL)
            except tk.TclError:
                text_context_menu.entryconfigure("Taglia", state=tk.DISABLED)
                text_context_menu.entryconfigure("Copia", state=tk.DISABLED)
            
            try:
                self.clipboard_get()
                text_context_menu.entryconfigure("Incolla", state=tk.NORMAL)
            except tk.TclError:
                text_context_menu.entryconfigure("Incolla", state=tk.DISABLED)

            text_context_menu.tk_popup(event.x_root, event.y_root)
            
        self.text_area.bind("<Button-3>", show_text_context_menu)
        # Binding per scorciatoie da tastiera standard
        self.text_area.bind("<<Cut>>", lambda e: self._text_cut())
        self.text_area.bind("<<Copy>>", lambda e: self._text_copy())
        self.text_area.bind("<<Paste>>", lambda e: self._text_paste())

    def _add_tree_context_menu(self):
        tree_context_menu = tk.Menu(self.result_tree, tearoff=0)
        tree_context_menu.add_command(label="Copia URL Stream", command=self._copy_selected_url)
        tree_context_menu.add_command(label="Copia tutti gli URL trovati", command=self._copy_all_found_urls)
        tree_context_menu.add_separator()
        tree_context_menu.add_command(label="Apri selezionato/i in VLC", command=lambda: self._send_to_vlc())
        tree_context_menu.add_command(label="Apri selezionato nel browser", command=self._open_in_browser)
        tree_context_menu.add_separator()
        tree_context_menu.add_command(label="Rimuovi selezionato/i dalla lista", command=self._remove_selected_from_tree)

        def show_tree_context_menu(event):
            iid = self.result_tree.identify_row(event.y)
            if iid: # Se si clicca su un item, selezionalo (se non già parte di una multiselezione)
                if not self.result_tree.selection() or iid not in self.result_tree.selection():
                     self.result_tree.selection_set(iid) # Questo cambia la selezione al singolo item. Per multiselect, gestire diversamente.

            # Abilita/disabilita opzioni in base alla selezione
            if self.result_tree.selection():
                tree_context_menu.entryconfigure("Copia URL Stream", state=tk.NORMAL)
                tree_context_menu.entryconfigure("Apri selezionato/i in VLC", state=tk.NORMAL)
                tree_context_menu.entryconfigure("Apri selezionato nel browser", state=tk.NORMAL if len(self.result_tree.selection()) == 1 else tk.DISABLED)
                tree_context_menu.entryconfigure("Rimuovi selezionato/i dalla lista", state=tk.NORMAL)
            else:
                tree_context_menu.entryconfigure("Copia URL Stream", state=tk.DISABLED)
                tree_context_menu.entryconfigure("Apri selezionato/i in VLC", state=tk.DISABLED)
                tree_context_menu.entryconfigure("Apri selezionato nel browser", state=tk.DISABLED)
                tree_context_menu.entryconfigure("Rimuovi selezionato/i dalla lista", state=tk.DISABLED)
            
            tree_context_menu.entryconfigure("Copia tutti gli URL trovati", state=tk.NORMAL if self.streams_found else tk.DISABLED)
            
            tree_context_menu.tk_popup(event.x_root, event.y_root)
                
        self.result_tree.bind("<Button-3>", show_tree_context_menu)
        
    def _text_cut(self):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                self.clipboard_clear()
                text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_append(text)
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass # Nessuna selezione
    
    def _text_copy(self):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                self.clipboard_clear()
                text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_append(text)
        except tk.TclError:
            pass # Nessuna selezione
    
    def _text_paste(self):
        try:
            text_to_paste = self.clipboard_get()
            if self.text_area.tag_ranges(tk.SEL): # Se c'è testo selezionato, sostituiscilo
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, text_to_paste)
        except tk.TclError:
            pass # Appunti vuoti o formato non testuale
            
    def _copy_selected_url(self):
        selected_items = self.result_tree.selection()
        if selected_items:
            urls = [self.result_tree.item(item)['values'][0] for item in selected_items]
            self.clipboard_clear()
            self.clipboard_append("\n".join(urls))
            self.status_var.set(f"{len(urls)} URL copiato/i negli appunti.")
    
    def _copy_all_found_urls(self):
        if self.streams_found:
            self.clipboard_clear()
            self.clipboard_append("\n".join(self.streams_found))
            self.status_var.set(f"Tutti i {len(self.streams_found)} URL trovati sono stati copiati.")
        else:
            self.status_var.set("Nessun URL trovato da copiare.")

    def _remove_selected_from_tree(self):
        selected_items = self.result_tree.selection()
        if not selected_items:
            return
        
        urls_to_remove_from_tree = set()
        for item_id in selected_items:
            url = self.result_tree.item(item_id, 'values')[0]
            urls_to_remove_from_tree.add(url)
            self.result_tree.delete(item_id)
        
        # Rimuovi anche da self.streams_found per consistenza
        self.streams_found = [url for url in self.streams_found if url not in urls_to_remove_from_tree]
        self.status_var.set(f"{len(selected_items)} stream rimosso/i dalla lista.")

    def _send_to_vlc(self, urls_to_send=None):
        if urls_to_send is None:
            selected_items = self.result_tree.selection()
            if not selected_items:
                self.status_var.set("Nessun stream selezionato da inviare a VLC.")
                if self.app_config.get("verbose_log", False): # Solo se log verboso
                    messagebox.showwarning("Selezione Vuota", "Nessuno stream selezionato nel pannello dei risultati.", parent=self)
                return
            
            urls_to_send = [self.result_tree.item(item)['values'][0] for item in selected_items]
            
        if urls_to_send:
            try:
                vlc_path = self.app_config.get("vlc_path", DEFAULT_VLC_PATH)
                if not vlc_path or not os.path.exists(vlc_path) or not os.path.isfile(vlc_path):
                    messagebox.showerror("Errore VLC", f"Percorso VLC non valido o file non trovato: {vlc_path}\nVerifica nelle impostazioni.", parent=self)
                    return

                cmd = [vlc_path]
                # Opzione per accodare o sostituire la playlist corrente
                # Per ora, usiamo sempre --playlist-enqueue se auto_start_vlc è attivo o se si invia manualmente
                cmd.append("--playlist-enqueue") 
                cmd.extend(urls_to_send)

                subprocess.Popen(cmd) # Usa Popen per non bloccare l'UI
                self.status_var.set(f"{len(urls_to_send)} stream inviato/i a VLC.")
            except FileNotFoundError: # Se il path è valido ma l'eseguibile non è trovato al momento dell'esecuzione
                messagebox.showerror("Errore VLC", f"VLC non trovato al percorso specificato: {vlc_path}\nAssicurati che il percorso sia corretto e che VLC sia installato.", parent=self)
            except Exception as e:
                messagebox.showerror("Errore VLC", f"Impossibile avviare o comunicare con VLC: {e}", parent=self)
                
    def _open_in_browser(self):
        selected_items = self.result_tree.selection()
        if len(selected_items) == 1: # Permetti solo apertura singola nel browser
            url = self.result_tree.item(selected_items[0])['values'][0]
            try:
                webbrowser.open_new_tab(url)
                self.status_var.set(f"Apertura di {url[:60]}... nel browser.")
            except Exception as e:
                messagebox.showerror("Errore Browser", f"Impossibile aprire l'URL nel browser: {e}", parent=self)
        elif len(selected_items) > 1:
            messagebox.showinfo("Info", "Per favore, seleziona un solo stream da aprire nel browser.", parent=self)
        else: # Nessuna selezione
             self.status_var.set("Nessuno stream selezionato da aprire nel browser.")


    def _paste_from_clipboard(self):
        try:
            text_to_paste = self.clipboard_get()
            if text_to_paste:
                current_text = self.text_area.get("1.0", tk.END).strip()
                if current_text: # Se c'è già testo, aggiungi una nuova riga prima di incollare
                    self.text_area.insert(tk.END, "\n" + text_to_paste)
                else:
                    self.text_area.insert(tk.END, text_to_paste)
                self.status_var.set("Testo incollato dagli appunti.")
        except tk.TclError:
            self.status_var.set("Nessun testo valido negli appunti.")
            
    def _new_session(self):
        confirm = True
        if self.text_area.get("1.0", tk.END).strip() or self.result_tree.get_children():
            confirm = messagebox.askyesno("Conferma Nuova Sessione", "Vuoi pulire la lista URL corrente e i risultati degli stream trovati?", parent=self)
        
        if confirm:
            self.text_area.delete("1.0", tk.END)
            self._clear_results()
            self.status_var.set("Nuova sessione. Lista URL e risultati puliti.")
            
    def _save_url_list_file(self): # Rinominato per chiarezza
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Salva lista URL come..."
        )
        if path:
            try:
                content = self.text_area.get("1.0", tk.END) # Salva esattamente ciò che c'è, incluse righe vuote se l'utente le ha messe
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_var.set(f"Lista URL salvata in: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Errore Salvataggio File", f"Impossibile salvare il file: {e}", parent=self)
            
    def _clear_results(self):
        if self.result_tree.get_children(): # Pulisci solo se ci sono item
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
        self.streams_found = [] # Svuota la lista interna
        self.status_var.set("Risultati degli stream puliti.")
    
    def _open_settings(self):
        # Passa una copia del dizionario di configurazione per evitare modifiche dirette
        # se il dialogo viene annullato, anche se SettingsDialog non dovrebbe modificarlo direttamente.
        current_config_copy = self.app_config.copy()
        dialog = SettingsDialog(self, current_config_copy) # Aspetta la chiusura nella __init__ del dialogo
        
        if dialog.result: # dialog.result contiene le nuove impostazioni salvate
            self.app_config.update(dialog.result)
            self._save_app_config() # Rinominato per coerenza
            self.status_var.set("Impostazioni salvate.")
            # Qui potresti dover riapplicare alcune impostazioni se necessario,
            # es. se il timeout del driver è cambiato, il prossimo driver lo userà.
            # Il tema è già gestito da _toggle_theme.
            
    def _toggle_theme(self):
        # La variabile self.dark_mode (BooleanVar) è già aggiornata dal Checkbutton del menu
        self._apply_theme() # Applica il nuovo tema a tutti i widget
        self.app_config["dark_mode"] = self.dark_mode.get() # Aggiorna il dizionario di config
        self._save_app_config() # Salva la configurazione aggiornata
        
    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam") # Base theme
        
        is_dark = self.dark_mode.get()

        # Colori base
        bg_main = "#333333" if is_dark else "#f0f0f0"
        fg_main = "white" if is_dark else "black"
        bg_widget = "#2b2b2b" if is_dark else "white" # Sfondo per text area, treeview, entry
        fg_widget = "white" if is_dark else "black"
        insert_bg_widget = "white" if is_dark else "black" # Cursore
        
        selected_bg = "#4a6984" if is_dark else "#0078d7" # Selezione in treeview/listbox
        selected_fg = "white" # Testo della selezione

        # Finestra principale
        self.configure(bg=bg_main)

        # Stili ttk globali
        style.configure(".", background=bg_main, foreground=fg_main, fieldbackground=bg_widget, lightcolor=bg_main, darkcolor=fg_main)
        style.map(".", foreground=[('disabled', "#777777" if is_dark else "#999999")])
        
        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main, foreground=fg_main)
        style.configure("TLabelframe", background=bg_main, foreground=fg_main, bordercolor="#555555" if is_dark else "#c0c0c0")
        style.configure("TLabelframe.Label", background=bg_main, foreground=fg_main)

        # Bottoni ttk
        btn_bg = "#555555" if is_dark else "#e0e0e0"
        btn_fg = fg_main
        btn_active_bg = "#666666" if is_dark else "#d0d0d0"
        style.configure("TButton", background=btn_bg, foreground=btn_fg, borderwidth=1)
        style.map("TButton",
                  background=[('active', btn_active_bg), ('disabled', "#444444" if is_dark else "#cccccc")],
                  foreground=[('disabled', "#888888" if is_dark else "#aaaaaa")])

        # Checkbutton ttk
        style.configure("TCheckbutton", background=bg_main, foreground=fg_main, indicatorcolor=bg_widget if is_dark else "#cccccc")
        style.map("TCheckbutton", indicatorcolor=[('selected', selected_bg), ('active', selected_bg)])
        
        # Scrollbar ttk
        style.configure("TScrollbar", troughcolor=bg_main, background=btn_bg) # Sfondo della freccia/slider
        style.map("TScrollbar", background=[('active', btn_active_bg)])


        # ProgressBar ttk
        style.configure("Horizontal.TProgressbar", background=selected_bg, troughcolor=bg_widget)


        # Configurazione widget Tk standard (non ttk)
        if hasattr(self, 'text_area') and self.text_area:
            self.text_area.configure(bg=bg_widget, fg=fg_widget, insertbackground=insert_bg_widget,
                                     selectbackground=selected_bg, selectforeground=selected_fg,
                                     undo=True, autoseparators=True, maxundo=-1) # Configura colori selezione

        # Configurazione Treeview (ttk)
        if hasattr(self, 'result_tree') and self.result_tree:
            style.configure("Treeview", background=bg_widget, foreground=fg_widget, fieldbackground=bg_widget, rowheight=25)
            style.map("Treeview", background=[('selected', selected_bg)], foreground=[('selected', selected_fg)])
            style.configure("Treeview.Heading", background=btn_bg, foreground=fg_main, relief=tk.FLAT) # Intestazioni
            style.map("Treeview.Heading", background=[('active', btn_active_bg)])

        # Menu bar (solo colori di base, Tk non tematizza completamente i menu su tutti i OS)
        if hasattr(self, 'menubar') and self.menubar:
            active_bg_menu = selected_bg
            active_fg_menu = selected_fg
            
            self.menubar.configure(bg=bg_main, fg=fg_main, activebackground=active_bg_menu, activeforeground=active_fg_menu)
            for i in range(self.menubar.index(tk.END) + 1):
                try:
                    menu_cascade = self.menubar.entrycget(i, "menu")
                    if menu_cascade:
                        # Questo è il nome del menu a cascata (es. '!menu', '!menu2')
                        # Dobbiamo ottenere l'oggetto menu effettivo
                        actual_menu = self.nametowidget(menu_cascade)
                        actual_menu.configure(bg=bg_main, fg=fg_main, activebackground=active_bg_menu, activeforeground=active_fg_menu,
                                              selectcolor=fg_main if is_dark else selected_fg) # Colore del segno di spunta/radio
                        # Stile per i separatori, se possibile (spesso non tematizzabile)
                        # for j in range(actual_menu.index(tk.END) + 1):
                        #     if actual_menu.type(j) == "separator":
                        #         actual_menu.entryconfigure(j, background="#FF0000") # Esempio, potrebbe non funzionare
                except tk.TclError:
                    continue # Se l'entry non è un menu a cascata o dà errore

    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Apri lista URL da file"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert(tk.END, data)
                self.status_var.set(f"Caricato file: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Errore Lettura File", f"Impossibile leggere il file: {e}", parent=self)
            
    def process_and_queue(self, queue=True):
        raw_text = self.text_area.get('1.0', tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Nessun Input", "Inserisci almeno un URL da processare.", parent=self)
            return
            
        # Estrai URL validi, ignorando righe vuote o commenti (es. #)
        links = []
        for line in raw_text.splitlines():
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#") and (stripped_line.startswith("http://") or stripped_line.startswith("https://")):
                links.append(stripped_line)

        if not links:
            messagebox.showwarning("Nessun URL Valido", "Nessun URL valido trovato nella lista.\nAssicurati che gli URL inizino con http:// o https:// e non siano commentati.", parent=self)
            return

        self._clear_results() # Pulisci risultati precedenti prima di iniziare
        
        self.progress_bar.pack(side=tk.RIGHT, padx=10, pady=2)
        self.progress_var.set(0)
        self.process_button.config(state=tk.DISABLED) # Disabilita bottone durante il processo
        
        self.status_var.set(f"Avvio processamento di {len(links)} URL...")
        # Esegui il processamento in un thread separato per non bloccare l'UI
        threading.Thread(target=self._process_links_thread, args=(links, queue), daemon=True).start()

    def _init_driver(self):
        # Questo metodo viene chiamato dal thread di processamento
        if self.driver is not None: # Se un driver esiste già, chiudilo prima
            try:
                self.driver.quit()
            except Exception: pass
            self.driver = None

        try:
            chrome_options = Options()
            browser_path = self.app_config.get("browser_path", DEFAULT_BRAVE_PATH)
            if browser_path and os.path.exists(browser_path) and os.path.isfile(browser_path):
                chrome_options.binary_location = browser_path
            else:
                # Non impostare binary_location se non valido, webdriver_manager proverà a trovarlo
                # Potrebbe essere utile un messaggio nella status_var se il path non è valido
                self.status_var.set("Percorso browser non valido o non impostato, uso Chrome/Brave di default.")


            chrome_options.add_argument('--headless=new') # Nuova modalità headless raccomandata
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--log-level=3') # Sopprime output console non critici
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") # Esempio User Agent

            logging_prefs = {'performance': 'ALL', 'browser': 'INFO'} # Cattura log di performance e browser
            chrome_options.set_capability('goog:loggingPrefs', logging_prefs)
            
            try:
                # Preferisci webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e_wdm:
                self.status_var.set(f"Webdriver-manager fallito: {str(e_wdm)[:100]}. Provo ChromeDriver locale.")
                try:
                    # Fallback a ChromeDriver nel PATH o stessa cartella
                    self.driver = webdriver.Chrome(options=chrome_options)
                except WebDriverException as e_local_wd:
                    # Entrambi i metodi falliti
                    full_error_msg = f"Errore avvio driver Chrome (WDM e locale):\n WDM: {str(e_wdm)}\n Locale: {str(e_local_wd)}"
                    # Poiché siamo in un thread, non possiamo usare messagebox direttamente
                    # Invia messaggio alla UI tramite coda o self.after se necessario
                    self.status_var.set("Errore critico avvio driver Selenium. Controlla i log.")
                    # Registra l'errore completo per il debug
                    print(f"CRITICAL SELENIUM ERROR: {full_error_msg}")
                    self.driver = None # Assicura che sia None
                    return # Esce da _init_driver

            if self.driver:
                self.driver.set_page_load_timeout(self.app_config.get("timeout", 20))
                self.status_var.set("Driver Selenium avviato con successo.")

        except WebDriverException as e:
            self.status_var.set(f"Impossibile avviare il driver: {str(e)[:150]}")
            self.driver = None
        except Exception as e_generic: # Cattura altre eccezioni impreviste
            self.status_var.set(f"Errore imprevisto init driver: {str(e_generic)[:150]}")
            self.driver = None


    def _get_m3u8_from_performance_logs(self, logs):
        # Chiamato dal thread
        found_urls = set() # Usa un set per evitare duplicati iniziali
        for entry in logs:
            try:
                log_message_outer = json.loads(entry['message'])
                log_message_inner = log_message_outer['message']
                
                # Controlla sia richieste che risposte per URL .m3u8
                url_to_check = None
                if log_message_inner.get('method') == 'Network.responseReceived':
                    if 'response' in log_message_inner['params'] and 'url' in log_message_inner['params']['response']:
                        url_to_check = log_message_inner['params']['response']['url']
                elif log_message_inner.get('method') == 'Network.requestWillBeSent':
                    if 'request' in log_message_inner['params'] and 'url' in log_message_inner['params']['request']:
                         url_to_check = log_message_inner['params']['request']['url']
                
                if url_to_check and '.m3u8' in url_to_check:
                    # A volte gli URL hanno parametri query che vogliamo preservare, ma vogliamo URL base unici
                    # Per ora, aggiungiamo l'URL completo se contiene .m3u8
                    found_urls.add(url_to_check)

            except (json.JSONDecodeError, KeyError, TypeError):
                # Ignora errori di parsing dei log o chiavi mancanti
                continue
        return list(found_urls) # Ritorna una lista

    def _process_links_thread(self, links, queue_vlc=True): # Rinominato queue a queue_vlc
        # Questo metodo gira in un thread separato.
        # Aggiornamenti alla UI (status_var, progress_var, result_tree, messagebox)
        # dovrebbero essere fatti tramite self.after() o una coda dedicata.
        # Per semplicità, alcuni aggiornamenti diretti a status_var e progress_var sono mantenuti,
        # ma per result_tree e messagebox è più sicuro usare self.after.

        self._init_driver() # Inizializza o reinizializza il driver

        total_links = len(links)
        
        for i, page_url in enumerate(links):
            # Aggiorna progresso (diretto, generalmente ok per IntVar)
            progress_value = int(((i + 1) / total_links) * 100)
            self.progress_var.set(progress_value)
            
            # Aggiorna status bar (diretto, generalmente ok per StringVar)
            self.status_var.set(f"Elaborazione {i+1}/{total_links}: {page_url[:70]}...")
            
            streams_found_on_this_page = set() # Usa set per evitare duplicati da diverse fonti per la stessa pagina

            # 1. Tentativo con Selenium (se il driver è stato inizializzato correttamente)
            if self.driver:
                try:
                    self.driver.get(page_url)
                    # Attendi un po' per permettere il caricamento di script JS (opzionale, potrebbe essere configurabile)
                    # self.driver.implicitly_wait(self.app_config.get("js_wait_time", 3)) # O time.sleep()
                    
                    # A volte, i log di performance potrebbero non catturare tutto subito.
                    # Un piccolo sleep DOPO il get può aiutare se gli stream sono caricati tardi.
                    # import time
                    # time.sleep(2) # Da testare, potrebbe rallentare molto

                    performance_logs = self.driver.get_log('performance')
                    js_streams = self._get_m3u8_from_performance_logs(performance_logs)
                    for stream_url in js_streams:
                        streams_found_on_this_page.add(stream_url)
                    
                    # A volte, gli stream sono nel sorgente della pagina dopo l'esecuzione JS
                    page_source_after_js = self.driver.page_source
                    regex_matches_after_js = M3U8_REGEX.finditer(page_source_after_js)
                    for match in regex_matches_after_js:
                        streams_found_on_this_page.add(match.group(1))

                    if js_streams or regex_matches_after_js: # Se Selenium ha trovato qualcosa
                         if self.app_config.get("verbose_log", False):
                            self.status_var.set(f"JS/DOM: Trovati {len(streams_found_on_this_page)} candidati per {page_url[:50]}...")
                
                except TimeoutException:
                    self.status_var.set(f"Timeout Selenium caricando: {page_url[:70]}...")
                except WebDriverException as e_wd:
                    self.status_var.set(f"Errore Selenium su {page_url[:50]}: {str(e_wd)[:100]}")
                    if "target crashed" in str(e_wd).lower() or "unable to discover open pages" in str(e_wd).lower():
                        self.status_var.set(f"Driver crashato. Riavvio per il prossimo URL...")
                        if self.driver: self.driver.quit(); self.driver = None
                        self._init_driver() # Tenta riavvio per i link successivi
                except Exception as e_sel:
                    if self.app_config.get("verbose_log", False):
                        self.status_var.set(f"Errore JS generico su {page_url[:50]}: {str(e_sel)[:100]}")

            # 2. Fallback con `requests` per il sorgente statico (sempre, a meno che non si voglia un'opzione per disabilitarlo)
            try:
                import requests # Assicurati che sia importato
                session = requests.Session()
                session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"})
                # Usa un timeout più breve per requests, dato che è un fallback
                response = session.get(page_url, timeout=max(5, self.app_config.get("timeout", 20) // 2))
                
                # Controlla header per redirect a .m3u8 (comune per stream diretti)
                if 'location' in response.headers and '.m3u8' in response.headers['location'].lower():
                    streams_found_on_this_page.add(response.headers['location'])
                if '.m3u8' in response.url.lower(): # Se l'URL finale dopo i redirect è un m3u8
                    streams_found_on_this_page.add(response.url)

                # Cerca nel corpo della risposta
                regex_matches_static = M3U8_REGEX.finditer(response.text)
                for match in regex_matches_static:
                    streams_found_on_this_page.add(match.group(1))
                
                if regex_matches_static and self.app_config.get("verbose_log", False):
                    self.status_var.set(f"Regex Statico: Trovati ulteriori candidati per {page_url[:50]}...")

            except requests.exceptions.RequestException as e_req:
                if self.app_config.get("verbose_log", False):
                    self.status_var.set(f"Errore Requests su {page_url[:50]}: {str(e_req)[:100]}")
            except Exception as e_fallback: # Altri errori nel blocco fallback
                if self.app_config.get("verbose_log", False):
                    self.status_var.set(f"Errore Fallback Regex su {page_url[:50]}: {str(e_fallback)[:100]}")

            # Aggiungi gli stream unici trovati per questa pagina alla lista globale e alla UI
            # Questo deve essere fatto nel thread principale usando self.after
            unique_new_streams_for_ui = []
            for stream_url in streams_found_on_this_page:
                if stream_url not in self.streams_found: # Controlla se è già stato trovato globalmente
                    self.streams_found.append(stream_url) # Aggiungi alla lista globale
                    unique_new_streams_for_ui.append(stream_url)
            
            if unique_new_streams_for_ui:
                self.after(0, self._update_result_tree, unique_new_streams_for_ui, page_url)

            # Aggiungi alla cronologia (può essere fatto direttamente se _add_to_history è thread-safe o usa self.after)
            # Per ora, assumiamo che il salvataggio file sia abbastanza veloce o che piccole race conditions siano accettabili.
            # Altrimenti, anche questo dovrebbe essere delegato al thread principale.
            self.after(0, self._add_to_history, page_url, bool(streams_found_on_this_page))
            
            if not streams_found_on_this_page and self.app_config.get("verbose_log", True): # Se verbose o default
                self.status_var.set(f"Nessun nuovo stream HLS trovato per: {page_url[:70]}...")
        
        # Fine del loop sui link
        if self.driver: # Chiudi il driver se è stato usato
            try:
                self.driver.quit()
            except Exception: pass # Ignora errori durante il quit
            self.driver = None
            
        # Operazioni finali da eseguire nel thread principale
        self.after(0, self._finalize_processing, queue_vlc, len(links))

    def _update_result_tree(self, stream_urls, page_url_origin):
        # Questo metodo viene chiamato da self.after, quindi è nel thread UI
        source_mapping = {"JS Network": "JS/DOM", "Regex Body": "Regex", "HTTP Header": "Header"} # Semplificato

        for stream_url in stream_urls:
            stream_type = "Index-v1" if "index-v1" in stream_url.lower() or "variant" in stream_url.lower() else "Master"
            quality = self._estimate_quality(stream_url)
            
            # Determina l'origine in modo più generico (potrebbe essere migliorato se si traccia l'origine esatta)
            # Per ora, se è arrivato qui, è stato trovato. L'origine precisa è persa se non passata.
            # Per semplicità, marchiamo come "Trovato". L'origine precisa (JS vs Regex) è difficile da tracciare
            # quando si uniscono i risultati di Selenium e Requests per la stessa pagina.
            # La logica in _process_links_thread dovrebbe idealmente passare l'origine.
            # Per ora, usiamo un placeholder.
            origin_display = "Misto" # Placeholder
            
            self.result_tree.insert("", tk.END, values=(stream_url, stream_type, quality, origin_display))
        
        # Auto-scrolla all'ultimo item aggiunto se ci sono molti risultati
        if self.result_tree.get_children():
            last_item = self.result_tree.get_children()[-1]
            self.result_tree.see(last_item)
            self.result_tree.selection_set(last_item) # Seleziona l'ultimo per feedback visivo

    def _finalize_processing(self, queue_vlc, num_links_processed):
        # Questo metodo viene chiamato da self.after, quindi è nel thread UI
        self.progress_bar.pack_forget() # Nascondi la barra di progresso
        self.process_button.config(state=tk.NORMAL) # Riabilita bottone

        final_status = ""
        if self.streams_found:
            final_status = f"Processo completato per {num_links_processed} URL. Trovati {len(self.streams_found)} stream totali."
            if queue_vlc and self.app_config.get("auto_start_vlc", True):
                selected_streams_for_vlc = self._select_best_streams_for_vlc() # Metodo specifico per VLC
                if selected_streams_for_vlc:
                    self._send_to_vlc(selected_streams_for_vlc) # Invia a VLC i migliori
                    final_status += f" {len(selected_streams_for_vlc)} stream inviato/i a VLC."
                else:
                    final_status += " Nessuno stream selezionato per l'invio automatico a VLC secondo i criteri."
                    messagebox.showinfo("Nessuno Stream per VLC", "Nessuno degli stream HLS trovati corrisponde ai criteri per l'invio automatico a VLC (es. preferenza index-v1).", parent=self)
            elif queue_vlc and not self.app_config.get("auto_start_vlc", True):
                 final_status += " Auto-invio a VLC disabilitato nelle impostazioni."
        else: # self.streams_found è vuoto
            final_status = f"Processo completato per {num_links_processed} URL. Nessun flusso HLS trovato."
            messagebox.showinfo("Nessun Risultato", "Nessun flusso HLS trovato dopo aver processato tutti i link.", parent=self)

        self.status_var.set(final_status)


    def _estimate_quality(self, stream_url):
        """Stima la qualità basandosi sull'URL dello stream."""
        s_url = stream_url.lower()
        # Pattern più specifici per risoluzioni comuni
        quality_patterns = {
            "4320p": "4320p", "2160p": "2160p", "1440p": "1440p",
            "1080p": "1080p", "720p": "720p", "576p": "576p", "540p": "540p",
            "480p": "480p", "360p": "360p", "240p": "240p", "144p": "144p"
        }
        for q_str, q_val in quality_patterns.items():
            if q_str in s_url or f"/{q_str[:-1]}/" in s_url or f"_{q_str[:-1]}_" in s_url: # es. /1080/ o _1080_
                return q_val
        
        # Pattern generico per numeri seguiti da 'p' o che sembrano risoluzioni verticali
        match = re.search(r'[/\-_](\d{3,4})[pP]?[/\-_.]', s_url) # es. /720p/, -1080.m3u8
        if match:
            num = match.group(1)
            if num in ["1080", "720", "480", "360", "240", "1440", "2160"]: # Validazione parziale
                return f"{num}p"

        return "N/D" # Non determinata

    def _select_best_streams_for_vlc(self):
        """Seleziona gli stream migliori da inviare a VLC basati sulle preferenze."""
        if not self.streams_found:
            return []
            
        candidate_streams = list(self.streams_found) # Lavora su una copia

        # 1. Preferenza per stream "index-v1" o "variant" (spesso master playlist)
        if self.app_config.get("prefer_index", True):
            preferred_streams = [
                u for u in candidate_streams 
                if "index-v1" in u.lower() or "variant" in u.lower() or "master.m3u8" in u.lower()
            ]
            if preferred_streams: # Se troviamo stream preferiti, usiamo solo quelli
                # Potremmo ulteriormente filtrare per qualità qui se volessimo,
                # ma VLC gestisce bene le master playlist.
                # Rimuovi duplicati esatti mantenendo l'ordine
                unique_preferred = []
                for url in preferred_streams:
                    if url not in unique_preferred:
                        unique_preferred.append(url)
                return unique_preferred # Restituisci questi stream preferiti
        
        # 2. Se nessun stream preferito trovato (o opzione disattivata),
        #    considera tutti gli stream. Potremmo voler evitare di inviare stream di qualità troppo bassa
        #    o multipli stream dalla stessa pagina/dominio se non sono master.
        #    Per ora, un approccio semplice è restituire tutti gli stream unici trovati
        #    se non ci sono preferiti o se la preferenza index è disattivata.
        #    Questa logica potrebbe essere espansa (es. non inviare stream < 480p se ci sono alternative).
        
        # Rimuovi duplicati esatti da tutti gli stream trovati, mantenendo l'ordine
        unique_all_streams = []
        for url in self.streams_found: # Usa la lista originale self.streams_found
            if url not in unique_all_streams:
                unique_all_streams.append(url)
        
        return unique_all_streams # Fallback a tutti gli stream unici
    
    def _add_to_history(self, url, found_stream_on_page):
        # Questo metodo è ora chiamato da self.after(), quindi è nel thread UI.
        timestamp = datetime.now().isoformat()
        
        # Rimuovi vecchie entry dello stesso URL per mantenere solo la più recente
        self.history = [entry for entry in self.history if entry.get("url") != url]
        self.history.append({"url": url, "timestamp": timestamp, "found_stream": found_stream_on_page})
        
        # Limita la lunghezza della cronologia
        max_days = self.app_config.get("history_days", 30)
        if max_days > 0:
            cutoff_datetime = datetime.now() - timedelta(days=max_days)
            self.history = [
                entry for entry in self.history 
                if datetime.fromisoformat(entry.get("timestamp", "1970-01-01T00:00:00")) >= cutoff_datetime # Fallback per entry vecchie senza timestamp
            ]
        elif max_days == 0: # 0 giorni significa nessuna cronologia persistente
            self.history = [h for h in self.history if h["url"] == url] # Mantieni solo l'entry corrente se 0 giorni

        # Ordina la cronologia dalla più recente alla più vecchia
        self.history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        self._save_history()
    
    def _show_history(self):
        """Mostra la finestra della cronologia"""
        history_window = tk.Toplevel(self)
        history_window.title("Cronologia Elaborazione URL")
        history_window.geometry("750x500")
        history_window.transient(self)
        history_window.grab_set()

        is_dark = self.dark_mode.get()
        bg_color = "#333333" if is_dark else "#f0f0f0"
        tree_bg = "#2b2b2b" if is_dark else "white"
        tree_fg = "white" if is_dark else "black"
        selected_bg = "#4a6984" if is_dark else "#0078d7"
        selected_fg = "white"
            
        history_window.configure(bg=bg_color)
            
        main_frame = ttk.Frame(history_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("data", "ora", "url", "status")
        history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="extended")
        
        history_tree.heading("data", text="Data")
        history_tree.heading("ora", text="Ora")
        history_tree.heading("url", text="URL Processato")
        history_tree.heading("status", text="Stream?")
        
        history_tree.column("data", width=100, anchor="w", stretch=False)
        history_tree.column("ora", width=80, anchor="w", stretch=False)
        history_tree.column("url", width=430, anchor="w") # Lascia che questa si espanda
        history_tree.column("status", width=70, anchor="center", stretch=False)

        hist_style = ttk.Style(history_window) # Usa una nuova istanza di Style per la finestra di dialogo se necessario
                                               # o assicurati che gli stili globali siano applicati.
        hist_style.configure("History.Treeview", background=tree_bg, foreground=tree_fg, fieldbackground=tree_bg, rowheight=22)
        hist_style.map("History.Treeview", background=[('selected', selected_bg)], foreground=[('selected', selected_fg)])
        hist_style.configure("History.Treeview.Heading", background="#555555" if is_dark else "#e0e0e0", 
                             foreground=tree_fg if is_dark else "black") # Usa colori consisteni con TButton
        history_tree.configure(style="History.Treeview")

        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=history_tree.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=history_tree.xview)
        history_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,0)) # pady per xbar
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, pady=(0,0))
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Popola con cronologia (già ordinata)
        for entry in self.history: 
            dt_obj = datetime.fromisoformat(entry.get("timestamp", "1970-01-01T00:00:00"))
            date_str = dt_obj.strftime("%d/%m/%Y")
            time_str = dt_obj.strftime("%H:%M:%S")
            status_char = "✔️" if entry.get("found_stream", False) else "❌"
            history_tree.insert("", tk.END, values=(date_str, time_str, entry.get("url","N/D"), status_char))
            
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(fill=tk.X, pady=(10,10), padx=10)
        
        def use_selected_action():
            selected_items = history_tree.selection()
            if selected_items:
                urls_to_add = [history_tree.item(item)['values'][2] for item in selected_items]
                
                current_text_in_main_area = self.text_area.get("1.0", tk.END).strip()
                text_block_to_add = "\n".join(urls_to_add)
                
                if current_text_in_main_area:
                    self.text_area.insert(tk.END, "\n" + text_block_to_add)
                else:
                    self.text_area.insert(tk.END, text_block_to_add)
                
                self.status_var.set(f"{len(urls_to_add)} URL aggiunto/i dalla cronologia.")
                history_window.destroy()
        
        def clear_history_entries_action():
            if messagebox.askyesno("Conferma Cancellazione", "Vuoi davvero cancellare tutta la cronologia?", parent=history_window):
                self.history = []
                self._save_history()
                for item_in_tree in history_tree.get_children(): # Pulisci il treeview corrente
                    history_tree.delete(item_in_tree)
                self.status_var.set("Cronologia cancellata.")
        
        ttk.Button(btn_frame, text="Usa Selezionato/i", command=use_selected_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Pulisci Tutta la Cronologia", command=clear_history_entries_action).pack(side=tk.RIGHT, padx=5)
        
        history_window.wait_window() # Rendi la finestra modale


    def _show_help(self):
        """Mostra finestra di aiuto"""
        help_text = """
# HLS Stream Queue Pro - Istruzioni

Questo programma ti permette di estrarre automaticamente i flussi HLS (M3U8) da una lista di pagine web e metterli in coda su VLC (o visualizzarli).

## Uso base:
1.  **Inserisci URL:** Digita o incolla gli URL delle pagine web (uno per riga) nel campo "URLs da processare".
    - Puoi caricare una lista da un file di testo (`Ctrl+O` o pulsante "Carica da file").
    - Puoi incollare dagli appunti (pulsante "Da appunti" o `Ctrl+V` nel campo).
2.  **Processa:**
    - Clicca su "**▶ Processa e Metti in Coda**" (`F5`) per avviare l'analisi.
        - Se "Avvia/riutilizza automaticamente VLC" è attivo nelle impostazioni, gli stream migliori trovati verranno inviati a VLC.
        - Altrimenti, gli stream verranno solo elencati nel pannello "Stream HLS trovati".
    - Usa "**Processa Senza Accodare**" (Menu Strumenti, `Shift+F5`) per trovare gli stream senza inviarli a VLC, indipendentemente dalle impostazioni.
3.  **Risultati:** Gli stream trovati appaiono nel pannello "Stream HLS trovati".
    - Seleziona uno o più stream e usa il menu contestuale (tasto destro) per:
        - **Copia URL Stream:** Copia l'URL dello/degli stream selezionato/i.
        - **Copia tutti gli URL trovati:** Copia tutti gli stream listati.
        - **Apri selezionato/i in VLC:** Invia gli stream selezionati a VLC. (Anche doppio click su un item).
        - **Apri selezionato nel browser:** Apre un singolo stream selezionato nel browser predefinito.
        - **Rimuovi selezionato/i dalla lista:** Elimina gli stream dalla visualizzazione corrente.

## Funzionalità Principali:
-   **Gestione File URL:**
    - "Nuovo" (`Ctrl+N`): Pulisce l'area URL e i risultati.
    - "Salva lista URL..." (`Ctrl+S`): Salva gli URL attualmente nel campo di testo in un file.
-   **Pulizia:**
    - "Pulisci Lista URL" (Menu Strumenti): Cancella gli URL dal campo di testo.
    - "Pulisci Risultati Stream" (Menu Strumenti): Cancella gli stream dal pannello dei risultati.
-   **Cronologia:**
    - "Mostra Cronologia" (`Ctrl+H`): Visualizza gli URL processati in passato. Puoi selezionare URL dalla cronologia per riutilizzarli. La cronologia indica se per un URL erano stati trovati stream (✔️/❌).
-   **Tema:**
    - "Modalità Scura" (Menu Impostazioni): Alterna tra tema chiaro e scuro. L'impostazione è salvata.

## Impostazioni (Menu Impostazioni > Impostazioni...):
-   **Percorso VLC:** Specifica il file eseguibile (.exe) di VLC Media Player.
-   **Percorso Browser:** Specifica il file eseguibile (.exe) di un browser basato su Chromium (Chrome, Brave, Edge) usato da Selenium per l'analisi JS. Se lasciato vuoto, tenta di usare il default.
-   **Timeout caricamento (sec):** Tempo massimo (in secondi) di attesa per il caricamento di una pagina da parte di Selenium e `requests`.
-   **Mantieni cronologia (giorni):** Per quanti giorni conservare la cronologia. `0` per non conservarla tra le sessioni (verrà pulita alla chiusura).
-   **Avvia/riutilizza automaticamente VLC:** Se attivo, gli stream migliori vengono inviati a VLC dopo il processamento quando si usa il comando principale "Processa e Metti in Coda".
-   **Preferisci stream index-v1 / variant:** Se attivo, quando si inviano stream a VLC, dà priorità a stream che sembrano playlist master (contenenti "index-v1", "variant", "master.m3u8").
-   **Log dettagliato nella status bar:** Mostra più informazioni tecniche/errori nella barra di stato, utile per diagnosi.

## Note Tecniche:
-   Lo script usa **Selenium** con un browser headless (invisibile) per analizzare le pagine che caricano stream HLS tramite JavaScript. Questo include l'ispezione del traffico di rete e del DOM dopo l'esecuzione JS.
-   Se Selenium fallisce o non trova stream, o come metodo complementare, viene effettuato un tentativo di fallback usando la libreria **`requests`** per scaricare il sorgente HTML statico della pagina e cercare URL `.m3u8` tramite espressioni regolari (Regex). Vengono controllati anche gli header HTTP per eventuali redirect a stream.
-   La colonna "Origine" nei risultati è un placeholder; l'estrazione combina metodi.
-   Assicurati che ChromeDriver (se non usi webdriver-manager) sia compatibile con la versione del tuo browser e sia nel PATH di sistema o nella cartella dell'applicazione. Webdriver-manager tenta di gestire questo automaticamente.

Versione: 2.1.0
        """
        
        help_window = tk.Toplevel(self)
        help_window.title("Istruzioni - HLS Stream Queue Pro")
        help_window.geometry("750x650")
        help_window.transient(self)
        help_window.grab_set()
        
        is_dark = self.dark_mode.get()
        bg_color = "#333333" if is_dark else "#f0f0f0"
        text_bg = "#2b2b2b" if is_dark else "white"
        text_fg = "white" if is_dark else "black"
            
        help_window.configure(bg=bg_color)
            
        text_frame = ttk.Frame(help_window, padding=(0,0,0,5)) # Frame per contenere testo e scrollbar
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,0))

        help_text_widget = scrolledtext.ScrolledText( # Rinominato per evitare conflitto nome
            text_frame, 
            wrap=tk.WORD, 
            bg=text_bg, 
            fg=text_fg,
            padx=10, pady=10,
            font=("Segoe UI", 10),
            selectbackground= ("#4a6984" if is_dark else "#0078d7"), # Colori selezione
            selectforeground="white",
            spacing1=3, # Spazio prima di un paragrafo
            spacing3=3  # Spazio dopo un paragrafo
        )
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        
        help_text_widget.insert(tk.END, help_text.strip())
        help_text_widget.configure(state="disabled")
        
        close_btn_frame = ttk.Frame(help_window)
        close_btn_frame.pack(fill=tk.X, padx=10, pady=(5,10)) # Padding bilanciato
        ttk.Button(close_btn_frame, text="Chiudi", command=help_window.destroy).pack(side=tk.RIGHT)
        
        help_window.wait_window()

    def _show_about(self):
        """Mostra finestra informazioni"""
        about_window = tk.Toplevel(self)
        about_window.title("Informazioni su HLS Stream Queue Pro")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        about_window.transient(self)
        about_window.grab_set()
        
        is_dark = self.dark_mode.get()
        bg_color = "#333333" if is_dark else "#f0f0f0"
        fg_color = "white" if is_dark else "black" # Per i Label principali se non usano lo stile ttk
            
        about_window.configure(bg=bg_color)
        
        main_frame = ttk.Frame(about_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="HLS Stream Queue Pro", font=("Segoe UI", 20, "bold")).pack(pady=(0, 15))
        ttk.Label(main_frame, text="Versione 2.1.0").pack(pady=(0, 25))
        
        desc_text = "Strumento avanzato per l'estrazione, la gestione e la riproduzione di flussi HLS (M3U8) da pagine web, con supporto per analisi dinamica (JavaScript) e statica."
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=420, justify=tk.CENTER, font=("Segoe UI", 10))
        desc_label.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Caratteristiche principali:", font=("Segoe UI", 10, "underline")).pack(pady=(10,5))
        features_text = "- Estrazione HLS da sorgenti JS e statiche\n- Accodamento a VLC Media Player\n- Interfaccia utente personalizzabile (tema scuro)\n- Gestione della cronologia e impostazioni persistenti"
        ttk.Label(main_frame, text=features_text, justify=tk.LEFT, font=("Segoe UI", 9)).pack(pady=(0,20))

        ttk.Label(main_frame, text="Sviluppato con Python e Tkinter.", font=("Segoe UI", 9, "italic")).pack(pady=(10, 5))
        ttk.Label(main_frame, text="© 2024 - Un Progetto AI.", font=("Segoe UI", 9)).pack(pady=(0, 15))
        
        ttk.Button(main_frame, text="Chiudi", command=about_window.destroy, style="Accent.TButton" if is_dark else "TButton").pack(pady=(10, 0))
        if is_dark: # Esempio di stile specifico per un bottone se necessario
            s = ttk.Style(about_window)
            s.configure("Accent.TButton", background="#0078D7", foreground="white")
            s.map("Accent.TButton", background=[('active',"#005FA3")])

        about_window.wait_window()
            
    def _load_config(self):
        """Carica configurazione da file JSON.
        Se il file non esiste o è corrotto, ne crea uno con i valori predefiniti.
        """
        default_config = {
            "vlc_path": DEFAULT_VLC_PATH,
            "browser_path": DEFAULT_BRAVE_PATH,
            "timeout": 30, # Aumentato leggermente il default
            "dark_mode": False,
            "history_days": 30,
            "auto_start_vlc": True,
            "prefer_index": True,
            "verbose_log": False
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Unisci con i default per assicurare che tutte le chiavi esistano e per aggiungere nuove chiavi default
                # se il file di config è di una versione precedente. Le impostazioni utente esistenti vengono mantenute.
                config = {**default_config, **loaded_config}
                # Se nuove chiavi sono state aggiunte a default_config e non erano in loaded_config,
                # salva la config aggiornata per persistere queste nuove chiavi con i loro valori default.
                if config != loaded_config: # Controlla se la config è cambiata dopo l'unione
                    self._save_app_config(config) # Passa la config unita da salvare
                return config
            except (json.JSONDecodeError, TypeError) as e: # Errore di parsing o tipo
                print(f"File di configurazione corrotto ({e}), verrà sovrascritto con i predefiniti.")
                # Opzionale: backup del file corrotto
                try:
                    os.replace(self.config_file, self.config_file + f".corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}")
                except OSError: pass
                self._save_app_config(default_config) # Salva i default
                return default_config
        else: # File non esiste
            print("File di configurazione non trovato, ne verrà creato uno con i valori predefiniti.")
            self._save_app_config(default_config) # Crea file con default
            return default_config
        
    def _save_app_config(self, config_to_save=None):
        """Salva il dizionario di configurazione fornito (o self.app_config) su file JSON."""
        data_to_save = config_to_save if config_to_save is not None else self.app_config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4) # indent=4 per leggibilità
        except Exception as e:
            # Evita messagebox qui per non bloccare in caso di problemi all'avvio/chiusura
            print(f"ERRORE CRITICO: Impossibile salvare la configurazione in {self.config_file}: {e}")
            # Potrebbe essere utile uno status bar message qui, ma print è più sicuro.
            
    def _load_history(self):
        """Carica cronologia da file JSON.
        Se il file non esiste o è corrotto, ritorna una lista vuota.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                if isinstance(history_data, list):
                    # Opzionale: validare la struttura di ogni entry della cronologia
                    valid_history = []
                    for entry in history_data:
                        if isinstance(entry, dict) and "url" in entry and "timestamp" in entry:
                            valid_history.append(entry)
                        # else: print(f"Ignorata entry cronologia non valida: {entry}")
                    return valid_history
                else: # Se il file non contiene una lista
                    print("File cronologia non contiene una lista valida, la cronologia sarà vuota.")
                    return [] 
            except (json.JSONDecodeError, TypeError) as e:
                print(f"File cronologia corrotto ({e}), la cronologia sarà vuota.")
                # Opzionale: backup del file corrotto
                try:
                    os.replace(self.history_file, self.history_file + f".corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}")
                except OSError: pass
                return []
        return [] # File non esiste
        
    def _save_history(self):
        """Salva la cronologia corrente (self.history) su file JSON."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4) # indent=4 per leggibilità
        except Exception as e:
            print(f"ERRORE: Impossibile salvare la cronologia in {self.history_file}: {e}")

    def quit(self):
        # Pulisci risorse prima di chiudere
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception:
                pass # Ignora errori durante il quit
        
        # Salva configurazione e cronologia una ultima volta (opzionale, potrebbero essere già aggiornate)
        # self._save_app_config()
        # self._save_history()

        super().quit() # Chiama il quit della classe base tk.Tk


if __name__ == '__main__':
    # È una buona pratica assicurarsi che le directory per i file di configurazione/dati esistano,
    # specialmente se non sono direttamente nella home dell'utente ma in sottocartelle come .config/appname/
    # In questo caso, i file sono direttamente in os.path.expanduser("~"), quindi la directory esiste.
    
    # Per una migliore gestione degli errori all'avvio, specialmente con Selenium/WebDriver:
    try:
        app = HLSQueueApp()
        # Gestisci la chiusura della finestra (pulsante X)
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.mainloop()
    except Exception as main_exception:
        # Fallback per errori critici non gestiti che impediscono l'avvio dell'UI
        print(f"Errore critico all'avvio dell'applicazione: {main_exception}")
        # Potresti voler mostrare un semplice messagebox di errore se Tkinter è ancora utilizzabile
        try:
            root_err = tk.Tk()
            root_err.withdraw() # Nascondi la finestra principale di errore
            messagebox.showerror("Errore Avvio Critico", 
                                 f"Impossibile avviare HLS Stream Queue Pro:\n{main_exception}\n\n"
                                 "Controlla la console per maggiori dettagli. "
                                 "Potrebbe essere un problema con l'installazione di Python, Tkinter, "
                                 "o dipendenze mancanti (es. Chrome/WebDriver).")
            root_err.destroy()
        except Exception: # Se anche Tkinter fallisce
            pass # L'errore è già stato stampato sulla console