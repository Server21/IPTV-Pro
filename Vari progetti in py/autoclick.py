import pyautogui
import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
import time
import pygetwindow as gw
import keyboard
from pynput import mouse

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto Clicker")

        self.is_running = Event()
        self.click_thread = None

        # Creazione delle etichette
        self.start_label = tk.Label(master, text="F1: Start")
        self.start_label.pack()

        self.stop_label = tk.Label(master, text="F2: Stop")
        self.stop_label.pack()

        # Creazione dei campi di inserimento delle coordinate
        self.x_entry_label = tk.Label(master, text="X:")
        self.x_entry_label.pack()
        self.x_entry = tk.Entry(master)
        self.x_entry.pack()

        self.y_entry_label = tk.Label(master, text="Y:")
        self.y_entry_label.pack()
        self.y_entry = tk.Entry(master)
        self.y_entry.pack()

        # Etichetta per visualizzare le coordinate del mouse
        self.coord_label = tk.Label(master, text="Mouse Position: (0, 0)")
        self.coord_label.pack()

        # Imposta le hotkeys per F1 e F2
        keyboard.add_hotkey('f1', self.start_clicking)
        keyboard.add_hotkey('f2', self.stop_clicking)

        # Avvia il thread di aggiornamento delle coordinate del mouse
        self.coord_thread = Thread(target=self.update_coordinates)
        self.coord_thread.daemon = True
        self.coord_thread.start()

        # Imposta l'ascoltatore per il clic con la rotella del mouse
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def start_clicking(self):
        if not self.is_running.is_set():
            self.is_running.set()
            if self.click_thread is None or not self.click_thread.is_alive():
                self.click_thread = Thread(target=self.auto_click)
                self.click_thread.start()

    def stop_clicking(self):
        self.is_running.clear()
        # Non è necessario chiamare join() qui
        # Aggiungi una pausa per dare tempo al thread di terminare
        time.sleep(0.5)

    def auto_click(self):
        while self.is_running.is_set():
            try:
                # Clicca alla posizione specificata dall'utente
                x = int(self.x_entry.get())
                y = int(self.y_entry.get())
                # Ottieni la finestra attiva
                active_window = gw.getActiveWindow()
                if active_window:
                    active_window.activate()  # Attiva la finestra
                    # Esegue il clic alle coordinate
                    pyautogui.click(x, y)
                time.sleep(0.1)  # Intervallo tra i clic
            except ValueError:
                messagebox.showerror("Error", "Invalid X or Y coordinate.")
                self.stop_clicking()
                break
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while clicking: {str(e)}")
                self.stop_clicking()
                break

    def update_coordinates(self):
        while True:
            x, y = pyautogui.position()
            self.coord_label.config(text=f"Mouse Position: ({x}, {y})")
            time.sleep(0.1)  # Aggiorna la posizione ogni 0.1 secondi

    def on_mouse_click(self, x, y, button, pressed):
        if button == mouse.Button.middle and pressed:
            # Aggiorna i campi di inserimento con le coordinate correnti
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(x))
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(y))

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
