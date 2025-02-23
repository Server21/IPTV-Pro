import time
import subprocess
import sys

def pause(seconds):
    time.sleep(seconds)

def install_requirements():
    print("\nInstallazione dei requisiti in corso...\n")
    subprocess.run("npm i -g nativefier", shell=True)
    print("Tutti i requisiti sono installati.")
    pause(2)

def check_requirements():
    print("\nVerifica dei requisiti...\n")
    print("Se i requisiti sono installati, dovrebbe comparire il numero di versione (es. 8.0.7)")
    pause(2)
    subprocess.run("nativefier -v", shell=True)
    print("\nOperazione completata.")
    pause(2)

def convert_website():
    print("\nNota: Tutti gli URL devono includere il protocollo (https/http) e un dominio (.com, .co.uk, .io, ecc.)")
    print("Se non viene specificato il protocollo, l'applicazione userà https di default.")
    url = input("Inserisci un URL: ").strip()
    flash = input("Il sito richiede Flash? (y/n): ").strip().lower()

    if flash == 'y':
        print("\nConversione del sito con supporto Flash...\n")
        subprocess.run(f"nativefier --flash {url}", shell=True)
    elif flash == 'n':
        print("\nConversione del sito...\n")
        subprocess.run(f"nativefier {url}", shell=True)
    else:
        print("Scelta non valida per il supporto Flash.")
        return

    print("\nOperazione completata.")
    while True:
        another = input("Vuoi convertire un altro URL o uscire? (y per convertire / n per uscire): ").strip().lower()
        if another == 'y':
            convert_website()  # richiama la conversione
            break
        elif another == 'n':
            sys.exit(0)
        else:
            print(f"'{another}' non è una scelta valida.")
            pause(2)
            print("Riprova.")

def main_menu():
    while True:
        print("\nSeleziona un'opzione:")
        print("1. Converti sito web")
        print("2. Installa requisiti")
        print("3. Controlla requisiti")
        print("4. Esci")
        choice = input("Inserisci il numero dell'opzione desiderata: ").strip()

        if choice == '1':
            convert_website()
        elif choice == '2':
            install_requirements()
        elif choice == '3':
            check_requirements()
        elif choice == '4':
            print("\nArrivederci.")
            pause(2)
            sys.exit(0)
        else:
            print(f"'{choice}' non è valido.")
            pause(2)
            print("Riprova.")

def main():
    print("Hi, there")
    pause(3)
    main_menu()

if __name__ == "__main__":
    main()
