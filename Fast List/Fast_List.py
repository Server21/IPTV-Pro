import tkinter as tk
from tkinter import messagebox, filedialog

# Funzione per generare gli URL
def generate_urls():
    template = input_text.get(1.0, tk.END).strip()
    try:
        start = int(start_entry.get())
        end = int(end_entry.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci valori numerici validi per l'inizio e la fine.")
        return
    
    replace = replace_entry.get()
    output = []

    for i in range(start, end + 1):
        url = template.replace(replace, str(i))
        output.append(url)
    
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, '\n'.join(output))

# Funzione per cancellare l'output
def clear_output():
    output_text.delete(1.0, tk.END)

# Funzione per scaricare il file M3U
def download_m3u():
    output = output_text.get(1.0, tk.END).strip()
    if not output:
        messagebox.showwarning("Avviso", "Nessun URL da salvare.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("File M3U", "*.m3u")])
    if not file_path:
        return

    with open(file_path, 'w') as file:
        file.write(output)
    
    messagebox.showinfo("Successo", "File M3U salvato con successo!")

# Creazione della finestra principale
root = tk.Tk()
root.title("Fast List")

# Imposta l'icona della finestra
root.iconbitmap("icon.ico")

# Frame per i controlli
control_frame = tk.Frame(root, padx=10, pady=10, bg='#34495e')
control_frame.pack(padx=20, pady=20, fill=tk.X)

# Titolo
title_label = tk.Label(control_frame, text="Fast List", font=("Arial", 18), bg='#34495e', fg='#1abc9c')
title_label.pack(pady=10)

# Label per l'input
tk.Label(control_frame, text="Inserisci il Link", bg='#34495e', fg='#ecf0f1').pack(pady=5)

# Text Area per l'input
input_text = tk.Text(control_frame, height=4, width=100, bg='#ecf0f1', fg='#2c3e50', wrap=tk.WORD)
input_text.insert(tk.END, "//www.example.com/item_[x].html")
input_text.pack(padx=10, pady=10)

tk.Label(control_frame, text="Valore Iniziale", bg='#34495e', fg='#ecf0f1').pack(pady=5)
start_entry = tk.Entry(control_frame, width=10)
start_entry.insert(tk.END, "1")
start_entry.pack(pady=5)

tk.Label(control_frame, text="Valore Finale", bg='#34495e', fg='#ecf0f1').pack(pady=5)
end_entry = tk.Entry(control_frame, width=10)
end_entry.insert(tk.END, "9")
end_entry.pack(pady=5)

tk.Label(control_frame, text="Sostituisci il numero con [x]", bg='#34495e', fg='#ecf0f1').pack(pady=5)
replace_entry = tk.Entry(control_frame, width=10)
replace_entry.insert(tk.END, "[x]")
replace_entry.pack(pady=5)

# Frame per i pulsanti
button_frame = tk.Frame(root, padx=10, pady=10, bg='#34495e')
button_frame.pack(pady=10)

# Pulsanti
generate_button = tk.Button(button_frame, text="Generate", command=generate_urls, bg='#1abc9c', fg='#ecf0f1', relief=tk.RAISED, width=15)
generate_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(button_frame, text="Clear", command=clear_output, bg='#e74c3c', fg='#ecf0f1', relief=tk.RAISED, width=15)
clear_button.pack(side=tk.LEFT, padx=5)

download_button = tk.Button(button_frame, text="Download M3U", command=download_m3u, bg='#3498db', fg='#ecf0f1', relief=tk.RAISED, width=15)
download_button.pack(side=tk.LEFT, padx=5)

# Text Area per l'output
output_text = tk.Text(root, height=20, width=100, bg='#ecf0f1', fg='#2c3e50', wrap=tk.WORD)
output_text.pack(padx=20, pady=10)

# Avvia l'interfaccia grafica
root.mainloop()
