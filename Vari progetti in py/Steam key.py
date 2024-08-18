import random
import string
import tkinter as tk
from tkinter import simpledialog, messagebox

affirmatives = ["y", "Y", "yes", "Yes", "yeah", "Yeah", "yup", "Yup"]
negatives = ["n", "N", "no", "No", "nope", "Nope", "nah", "Nah"]

def gen_key():
    try:
        key_amount = int(simpledialog.askstring("Input", "Amount of keys [integer] (default: 1):") or "1")
    except ValueError:
        key_amount = 1

    keys = []
    for _ in range(key_amount):
        chars = string.ascii_uppercase + string.digits
        key = '-'.join(''.join(random.choice(chars) for _ in range(5)) for _ in range(3))
        keys.append(key)

    keys_output = '\n'.join(keys)
    text_box.config(state=tk.NORMAL)
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, keys_output)
    text_box.config(state=tk.DISABLED)

    is_saved = simpledialog.askstring("Save", "Would you like to save the key(s) [yes/no] (default: no)?") or "no"

    if is_saved.lower() in affirmatives:
        save_name = simpledialog.askstring("Save", "Where would you like to save them [filename] (default: keys.txt)?") or "keys"
        try:
            with open(f"{save_name}.txt", 'w') as f:
                for key in keys:
                    f.write(f"{key}\n")
            messagebox.showinfo("Saved", f"Keys saved to {save_name}.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the file: {e}")
    elif is_saved.lower() in negatives:
        messagebox.showinfo("Info", "Skipping the saving part.")

def generate_more_keys():
    gen_key()

def quit_program():
    root.destroy()

root = tk.Tk()
root.title("Key Generator")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

generate_button = tk.Button(frame, text="Generate Keys", command=generate_more_keys)
generate_button.pack(pady=5)

text_box = tk.Text(frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
text_box.pack(pady=5)

quit_button = tk.Button(frame, text="Quit", command=quit_program)
quit_button.pack(pady=5)

root.mainloop()
