import tkinter as tk
from tkinter import messagebox

class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gioco dell'impiccato")
        self.root.geometry("800x500")
        self.root.configure(bg='#f0f8ff')

        self.parola_da_indovinare = ""
        self.lettere_indovinate = []
        self.tentativi_rimasti = 6

        # Creazione dei widget
        self.create_widgets()

    def create_widgets(self):
        # Titolo del gioco
        self.title_label = tk.Label(self.root, text="Gioco dell'impiccato", font=("Arial", 24, "bold"), bg='#f0f8ff')
        self.title_label.pack(pady=10)

        # Sezione di inserimento della parola
        self.word_entry_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.word_entry_frame.pack(pady=10)
        self.word_label = tk.Label(self.word_entry_frame, text="Inserisci una parola:", font=("Arial", 14), bg='#f0f8ff')
        self.word_label.pack(side=tk.LEFT)
        self.word_input = tk.Entry(self.word_entry_frame, show='*', font=("Arial", 14))
        self.word_input.pack(side=tk.LEFT, padx=10)
        self.submit_word_btn = tk.Button(self.word_entry_frame, text="Inizia il gioco", font=("Arial", 14), command=self.start_game, bg='#4caf50', fg='#fff')
        self.submit_word_btn.pack(side=tk.LEFT)

        # Visualizzazione della parola
        self.word_display = tk.Label(self.root, text="", font=("Arial", 28, "bold"), bg='#fff', width=20)
        self.word_display.pack(pady=20)

        # Sezione per indovinare
        self.guess_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.guess_frame.pack(pady=10)
        self.guess_label = tk.Label(self.guess_frame, text="Inserisci una lettera o la parola intera:", font=("Arial", 14), bg='#f0f8ff')
        self.guess_label.pack(side=tk.LEFT)
        self.guess_input = tk.Entry(self.guess_frame, font=("Arial", 14))
        self.guess_input.pack(side=tk.LEFT, padx=10)
        self.submit_btn = tk.Button(self.guess_frame, text="Indovina", font=("Arial", 14), command=self.check_guess, bg='#4caf50', fg='#fff')
        self.submit_btn.pack(side=tk.LEFT)

        # Visualizzazione del risultato
        self.result_label = tk.Label(self.root, text="", font=("Arial", 20, "bold"), fg='#e74c3c', bg='#f0f8ff')
        self.result_label.pack(pady=10)

        # Pulsante per ricominciare
        self.reset_btn = tk.Button(self.root, text="Ricomincia", font=("Arial", 14), command=self.reset_game, bg='#e74c3c', fg='#fff')
        self.reset_btn.pack(pady=10)

    def start_game(self):
        self.parola_da_indovinare = self.word_input.get().upper()
        if self.parola_da_indovinare.isalpha() and len(self.parola_da_indovinare) > 0:
            self.lettere_indovinate = ['_' for _ in self.parola_da_indovinare]
            self.display_word()
            self.word_entry_frame.pack_forget()
        else:
            messagebox.showerror("Errore", "Inserisci una parola valida (almeno un carattere).")

    def display_word(self):
        self.word_display.config(text=' '.join(self.lettere_indovinate))

    def check_guess(self):
        guess = self.guess_input.get().upper()
        self.guess_input.delete(0, tk.END)

        if len(guess) > 1:  # L'utente ha inserito la parola intera
            if guess == self.parola_da_indovinare:
                self.lettere_indovinate = list(self.parola_da_indovinare)
                self.display_word()
                self.result_label.config(text="Complimenti! Hai indovinato la parola!", fg='#2ecc71')
                self.disable_guessing()
            else:
                self.tentativi_rimasti -= 2
                self.update_game_status()
        else:  # L'utente ha inserito una singola lettera
            lettera_trovata = False
            for i, lettera in enumerate(self.parola_da_indovinare):
                if lettera == guess:
                    self.lettere_indovinate[i] = guess
                    lettera_trovata = True

            self.display_word()
            if not lettera_trovata:
                self.tentativi_rimasti -= 1

            self.update_game_status()

    def update_game_status(self):
        if ''.join(self.lettere_indovinate) == self.parola_da_indovinare:
            self.result_label.config(text="Complimenti! Hai indovinato la parola!", fg='#2ecc71')
            self.disable_guessing()
        elif self.tentativi_rimasti <= 0:
            self.result_label.config(text=f"Mi dispiace, hai esaurito i tentativi. La parola era: {self.parola_da_indovinare}", fg='#e74c3c')
            self.disable_guessing()
        else:
            self.result_label.config(text=f"Tentativi rimasti: {self.tentativi_rimasti}")

    def disable_guessing(self):
        self.guess_input.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)

    def reset_game(self):
        self.parola_da_indovinare = ''
        self.lettere_indovinate = []
        self.tentativi_rimasti = 6
        self.word_entry_frame.pack(pady=10)
        self.word_input.delete(0, tk.END)
        self.guess_input.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.word_display.config(text='')
        self.result_label.config(text='')

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()
