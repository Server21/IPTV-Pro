import threading
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# -----------------------------
# Funzioni di parsing e verifica
# -----------------------------
def parse_playlist_content(content):
    items = []
    lines = [line.strip() for line in content.splitlines()]
    for i, line in enumerate(lines):
        if line.startswith('#EXTINF'):
            parts = line.split(',', 1)
            label = parts[1] if len(parts) > 1 else 'N/A'
            j = i + 1
            while j < len(lines):
                candidate = lines[j]
                if candidate and not candidate.startswith('#') and urlparse(candidate).scheme in ('http', 'https'):
                    items.append((label, candidate))
                    break
                j += 1
    return items


def check_url(url, timeout=10):
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code in (403, 405):
            resp = requests.get(url, timeout=timeout, stream=True)
        return resp.status_code, None
    except Exception as e:
        return None, str(e)

# -----------------------------
# GUI con Tkinter e ttk
# -----------------------------
class LinkCheckerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HLS Link Checker")
        self.geometry("800x600")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Risultati iniziali
        self.results = []

        # Menu Bar
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Apri Playlist...", command=self.load_file, accelerator="Ctrl+O")
        filemenu.add_separator()
        filemenu.add_command(label="Esci", command=self.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)
        self.bind_all("<Control-o>", lambda e: self.load_file())
        self.bind_all("<Control-q>", lambda e: self.quit())

        # URL Entry con contesto
        frm_url = ttk.Frame(self)
        frm_url.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(frm_url, text="Playlist URL (raw):").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(frm_url)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.bind('<Button-3>', self.show_entry_menu)

        # Buttons
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frm_btn, text="Seleziona File .m3u", command=self.load_file).pack(side=tk.LEFT)
        ttk.Button(frm_btn, text="Controlla Link", command=self.start_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_btn, text="Copia Report", command=self.copy_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_btn, text="Esporta Funzionanti", command=self.export_working).pack(side=tk.RIGHT)

        # Progress Bar
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=(0,5))

        # Treeview per risultati
        cols = ('Label', 'URL', 'Status')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Contesto per Entry
        self.entry_menu = tk.Menu(self, tearoff=0)
        self.entry_menu.add_command(label="Taglia", command=lambda: self.url_entry.event_generate('<<Cut>>'))
        self.entry_menu.add_command(label="Copia", command=lambda: self.url_entry.event_generate('<<Copy>>'))
        self.entry_menu.add_command(label="Incolla", command=lambda: self.url_entry.event_generate('<<Paste>>'))

        # Impostazioni
        self.timeout = 10
        self.workers = 5
        self.playlist_content = None

    def show_entry_menu(self, event):
        self.entry_menu.tk_popup(event.x_root, event.y_root)

    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("M3U Playlist", "*.m3u;*.txt"), ("All files", "*")]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.playlist_content = f.read()
                messagebox.showinfo("File caricato", f"Playlist caricata da: {path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile leggere il file: {e}")

    def start_check(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []  # reset dei risultati
        raw_url = self.url_entry.get().strip()
        if raw_url:
            threading.Thread(target=self.fetch_and_check, args=(raw_url,)).start()
        elif self.playlist_content:
            threading.Thread(target=self.run_check, args=(self.playlist_content,)).start()
        else:
            messagebox.showwarning("Avviso", "Inserisci un URL o carica un file .m3u.")

    def fetch_and_check(self, raw_url):
        try:
            resp = requests.get(raw_url, timeout=self.timeout)
            resp.raise_for_status()
            self.run_check(resp.text)
        except Exception as e:
            messagebox.showerror("Errore Download", f"Download fallito: {e}")

    def run_check(self, content):
        items = parse_playlist_content(content)
        total = len(items)
        self.progress['maximum'] = total
        self.progress['value'] = 0

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_map = {executor.submit(check_url, url, self.timeout): (label, url)
                          for label, url in items}
            for future in as_completed(future_map):
                try:
                    label, url = future_map[future]
                    status, err = future.result()
                except Exception as e:
                    label, url, status, err = 'N/A', 'N/A', None, str(e)
                color = 'green' if status and 200 <= status < 400 else 'red'
                statustxt = str(status) if status else "ERR"
                self.tree.insert('', tk.END, values=(label, url, statustxt), tags=(color,))
                self.tree.tag_configure('green', foreground='green')
                self.tree.tag_configure('red', foreground='red')
                self.progress.step(1)
                self.results.append((label, url, status, err))

        self.show_summary()

    def show_summary(self):
        broken = [label for label, url, status, err in self.results if status and not (200 <= status < 400)]
        errors = [label for label, url, status, err in self.results if status is None]
        summary = f"OK: {len(self.results)-len(broken)-len(errors)}, BROKEN: {len(broken)}, ERROR: {len(errors)}"
        messagebox.showinfo("Riepilogo", summary)

    def copy_report(self):
        items = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        text = "\n".join(f"{lbl} -> {url} -> {stat}" for lbl, url, stat in items)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copia Report", "Report copiato negli appunti.")

    def export_working(self):
        working = [(lbl, url, stat) for lbl, url, stat, err in self.results if stat and 200 <= stat < 400]
        if not working:
            messagebox.showwarning("Nessun link", "Non ci sono link funzionanti da esportare.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text files', '*.txt'), ('All files', '*')],
            title='Salva link funzionanti'
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for lbl, url, stat in working:
                        f.write(f"{lbl} -> {url} -> {stat}\n")
                messagebox.showinfo("Esporta Funzionanti", f"Link funzionanti salvati in: {path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Salvataggio fallito: {e}")

    def quit(self):
        self.destroy()

if __name__ == '__main__':
    app = LinkCheckerGUI()
    app.mainloop()
