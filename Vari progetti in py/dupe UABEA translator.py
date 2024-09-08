import tkinter as tk
from tkinter import filedialog, scrolledtext, Menu
from googletrans import Translator

class TextTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traduttore di Testi")

        # Stile della finestra principale
        self.root.configure(bg="#2E3B4E")
        self.root.geometry("800x600")

        # Font
        font_label = ("Helvetica", 12, "bold")
        font_button = ("Helvetica", 10, "bold")
        font_text_area = ("Consolas", 10)

        # Colori
        bg_color = "#2E3B4E"
        fg_color = "#FFFFFF"
        button_color = "#3A475C"
        button_hover_color = "#4C5C72"

        # Layout
        self.label = tk.Label(root, text="Seleziona un file di testo:", font=font_label, bg=bg_color, fg=fg_color)
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Seleziona File", font=font_button, bg=button_color, fg=fg_color,
                                       activebackground=button_hover_color, command=self.load_file)
        self.select_button.pack(pady=5)

        self.translate_button = tk.Button(root, text="Traduci", font=font_button, bg=button_color, fg=fg_color,
                                          activebackground=button_hover_color, command=self.translate_file, state=tk.DISABLED)
        self.translate_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Salva Traduzione", font=font_button, bg=button_color, fg=fg_color,
                                     activebackground=button_hover_color, command=self.save_translated_file, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=font_text_area, bg="#1C2733", fg=fg_color,
                                                   insertbackground=fg_color)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        self.status = tk.Label(root, text="", font=font_label, bg=bg_color, fg=fg_color)
        self.status.pack(pady=10)

        self.file_path = None
        self.translated_content = None
        self.translator = Translator()

        # Aggiungi menu contestuale per copia, taglia, incolla
        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = Menu(self.root, tearoff=0, bg="#1C2733", fg="#FFFFFF", font=("Helvetica", 10))
        self.context_menu.add_command(label="Taglia", command=self.cut_text)
        self.context_menu.add_command(label="Copia", command=self.copy_text)
        self.context_menu.add_command(label="Incolla", command=self.paste_text)

        self.text_area.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")

    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")

    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
            self.status.config(text=f"File caricato: {self.file_path}")
            self.translate_button.config(state=tk.NORMAL)
            self.adjust_text_area(content)

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
                        buffer.append('"')
                        in_string = False
                        # Translate buffer content
                        original_text = "".join(buffer[1:-1])  # Rimuovi gli apici per tradurre il testo
                        translated_text = self.translator.translate(original_text, src='en', dest='it').text
                        new_line += f'"{translated_text}"'  # Aggiungi il testo tradotto con gli apici
                        buffer = []
                    else:
                        if buffer:
                            new_line += "".join(buffer)
                            buffer = []
                        buffer.append('"')
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

        # Update the text area with translated content, allowing user to edit
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.translated_content)
        self.status.config(text="Traduzione completata! Puoi modificare il testo e salvarlo.")
        self.save_button.config(state=tk.NORMAL)
        self.adjust_text_area(self.translated_content)

    def adjust_text_area(self, content):
        lines = content.splitlines()
        max_line_length = max(len(line) for line in lines) if lines else 1
        self.text_area.config(width=max_line_length, height=len(lines))

    def save_translated_file(self):
        # Get the content from the text area (including any user edits)
        self.translated_content = self.text_area.get(1.0, tk.END)

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(self.translated_content)
            self.status.config(text=f"File tradotto e modificato salvato: {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTranslatorApp(root)
    root.mainloop()
