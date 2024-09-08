import tkinter as tk
from tkinter import filedialog, scrolledtext
from googletrans import Translator

class TextTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traduttore di Testi")

        # Layout
        self.label = tk.Label(root, text="Seleziona un file di testo:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Seleziona File", command=self.load_file)
        self.select_button.pack(pady=5)

        self.translate_button = tk.Button(root, text="Traduci", command=self.translate_file, state=tk.DISABLED)
        self.translate_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Salva Tradotto", command=self.save_translated_file, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Courier New", 10))
        self.text_area.pack(pady=10)

        self.status = tk.Label(root, text="")
        self.status.pack(pady=10)

        self.file_path = None
        self.translated_content = None
        self.translator = Translator()

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
            self.status.config(text=f"File caricato: {self.file_path}")
            self.translate_button.config(state=tk.NORMAL)

    def translate_file(self):
        if not self.file_path:
            self.status.config(text="Nessun file selezionato!")
            return

        content = self.text_area.get(1.0, tk.END)
        translated_lines = []
        
        in_string = False
        buffer = []

        for line in content.splitlines(True):
            new_line = ""
            i = 0
            while i < len(line):
                if line[i] == '"':
                    if in_string:
                        new_line += '"'
                        in_string = False
                        buffer.append(line[i])
                        # Translate buffer content
                        translated_text = self.translator.translate("".join(buffer[1:-1]), src='en', dest='it').text
                        new_line += translated_text
                        buffer = []
                    else:
                        if buffer:
                            new_line += "".join(buffer)
                            buffer = []
                        new_line += '"'
                        in_string = True
                    i += 1
                else:
                    if in_string:
                        buffer.append(line[i])
                    else:
                        new_line += line[i]
                    i += 1
            
            # Append any remaining buffer
            if buffer:
                new_line += "".join(buffer)
            translated_lines.append(new_line)
        
        self.translated_content = ''.join(translated_lines)

        # Update the text area with translated content
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.translated_content)
        self.status.config(text="Traduzione completata!")
        self.save_button.config(state=tk.NORMAL)

    def save_translated_file(self):
        if not self.translated_content:
            self.status.config(text="Nessuna traduzione da salvare!")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(self.translated_content)
            self.status.config(text=f"File tradotto salvato: {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTranslatorApp(root)
    root.mainloop()
