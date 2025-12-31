import tkinter as tk
from tkinter import ttk
from logic import dodaj_produkty, dodaj_kilka_sztuk, usun_produkt_z_zasobow, usun_kilka_sztuk, \
    wprowadz_do_baza_i_zasoby, import_do_bazy_guzik, import_to_baza_clean
from utils import czysc_mniej_0, dataframe_to_pdf, dodaj_komentarz
from tkinter import messagebox
from datetime import datetime









class GUI(tk.Tk):
    def __init__(self, baza, zasoby, komentarze):
        super().__init__()
        self.baza = baza
        self.zasoby = zasoby
        self.komentarze = komentarze
        print(self.komentarze)
        self.title("Zasoby")
        self.geometry("1380x820")
        self.configure(bg="#ffffff")

        ############ Okienko z mozliwoscia wyoboru
        # Stylizacja Treeview
        style = ttk.Style()
        style.theme_use("clam")  # styl bez efektów
        style.configure("Treeview",
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        foreground="black",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#ffffff",
                        foreground="black",
                        borderwidth=0)

        # Główna ramka dzieląca okno
        main_frame = tk.Frame(self, bg="#ffffff")
        main_frame.pack(fill="both", expand=True)

        # Margines po lewej stronie
        left_margin = tk.Frame(main_frame, width=400, bg="#f8f8f8")
        left_margin.pack(side="left", fill="y")
        left_margin.pack_propagate(False)  # ❗️Zablokuj rozciąganie

        # Ramka z tabelą po prawej stronie
        tabela_frame = tk.Frame(main_frame, padx=70, pady=70, bg="#ffffff")
        tabela_frame.pack(side="right", fill="both", expand=True)

        # Ramka z wyszukiwanem
        #  Wyszukiwarka nad tabelą
        search_frame = tk.Frame(tabela_frame, bg="#ffffff")
        search_frame.pack(pady=(0, 10), fill="x")

        self.search_var = tk.StringVar()

        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Arial", 14), bg="#ffffff", fg="black",
                                relief="solid", bd=1)
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))

        search_btn = tk.Button(search_frame, text="🔍", font=("Arial", 12),
                               bg="#1e90ff", fg="white", width=4,
                               command=self.szukaj_w_tabeli)
        search_btn.pack(side="left", padx=(0, 10))

        search_entry.bind("<Return>", lambda event: self.szukaj_w_tabeli())

        # Scroll
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Tabela
        self.tree = ttk.Treeview(tabela_frame, columns=list(zasoby.columns), show="headings",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        for col in zasoby.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor="center")

        for _, row in zasoby.iterrows():
            self.tree.insert("", "end", values=list(row))

        self.tree.pack(expand=True, fill="both")

        # Kontener na przyciski – biała ramka przy dolnej krawędzi
        btn_container = tk.Frame(left_margin, bg="#ffffff")
        btn_container.pack(side="bottom", pady=60, padx=40, fill="x", expand=True)

        # Przycisk 1 – Dodaj kilka sztuk
        btn1 = tk.Button(btn_container, text="Dodaj kilka sztuk",
                         font=("Arial", 14, "bold"),
                         bg="#006400", fg="black",
                         height=2, anchor="center", justify="center",
                         command=lambda: [self.okno_dodaj_hurtem()]) # podpiecie funkcji itp.
        btn1.pack(pady=10, padx=0, fill="x")


        # Przycisk 2 – Dodaj produkty #
        btn2 = tk.Button(btn_container, text="Dodaj produkty",
                         font=("Arial", 14, "bold"),
                         bg="#00cc00", fg="black",
                         height=2, anchor="center", justify="center",
                         command=lambda: [self.otworz_okno_skanowania_dodaj()])
        btn2.pack(pady=10, padx=0,fill="x")


        # Przycisk 3 – Usuń produkty
        btn3 = tk.Button(btn_container, text="Usuń produkty",
                         font=("Arial", 14, "bold"),
                         bg="#ff0000", fg="black",
                         height=2, anchor="center", justify="center",
                         command=lambda: [self.otworz_okno_skanowania_usun()]) # Musi byc troche inaczej bedzie trzeba podpiac inne okno
        btn3.pack(pady=10, fill="x")


        # Przycisk 4 – Usuń kilka sztuk
        btn4 = tk.Button(btn_container, text="Usuń kilka sztuk",
                         font=("Arial", 14, "bold"),
                         bg="#B22222", fg="black",
                         height=2, anchor="center", justify="center",
                         command=lambda: [self.okno_usun_hurtem()])
        btn4.pack(pady=10, fill="x")


        # Przycisk 5 – Eksportuj do bazy
        btn5 = tk.Button(btn_container, text="Importuj do bazy",
                         font=("Arial", 14, "bold"),
                         bg="#1e90ff", fg="black",
                         height=2, anchor="center", justify="center",
                         command=self.importuj_do_bazy_mod) # Trzeba zmienic bedzie, napisac funkcja, która import do bazy i przetwarza dane
        btn5.pack(pady=10, fill="x")

        # Przycisk 6 – W prowadz produkt ręcznie
        btn6 = tk.Button(btn_container, text="Wprowadź produkt ręcznie",
                         font=("Arial", 14, "bold"),
                         bg="#87CEEB", fg="black",
                         height=2, anchor="center", justify="center",
                         command=lambda: [self.okno_wprowadz_ręcznie()])
        btn6.pack(pady=10, fill="x")

        # Przycisk 7 – Eksport stan zasobow
        btn7 = tk.Button(btn_container, text="Eksportuj stan zasobów do pdf",
                         font=("Arial", 14, "bold"),
                         bg="lightgrey", fg="black",
                         height=2, anchor="center", justify="center", command=self.to_pdf) # command = "otworzu druk" itp...
        btn7.pack(pady=10, fill="x")

        # Przycisk - Włącza okienko z hisotorią
        btn8 = tk.Button(btn_container, text="Wyświetl historię",
                         font=("Arial", 14, "bold"),
                         bg="purple", fg="black",
                         height=2, anchor="center", justify="center", command=self.otworz_historie)
        btn8.pack(pady=10, fill="x")


    def odswiez_tabele(self):
        # Wyczyść istniejące wiersze
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Wstaw aktualne dane z self.zasoby
        for _, row in self.zasoby.iterrows():
            self.tree.insert("", tk.END, values=list(row))


    def importuj_do_bazy_mod(self):
        imp_produkty = import_do_bazy_guzik() ## czyli on zwraca w pandas   #### wprowadz xlsx
        if type(imp_produkty) == bool:
            print("Nie dodano")
        else:
            ok = import_to_baza_clean(imp_produkty, self.baza)### GENERALNIE DZIAŁA tylko w momenci w ktorym wylaczasz wyskakuje na czerwonow

            if type(ok) == bool:
                print('Błąd w odczcyie pliku.')
                messagebox.showerror("Błąd", "Błąd w odczycie pliku. Zwróć uwagę na jego strukturę.")
                print("❌ Plik nie został zaimportowany do bazy.")

            else:
                self.baza = ok
                # Tu by bylo przyjemnie odswiezyc baze
                print(self.baza)
                messagebox.showinfo("Sukces", "Plik został zaimportowany do bazy. ")
                print("✅ Plik został pomyślnie zaimportowany i dodany do bazy.")
        self.odswiez_tabele()


    def szukaj_w_tabeli(self):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        for _, row in self.zasoby.iterrows():
            if any(query in str(value).lower() for value in row):
                self.tree.insert("", "end", values=list(row))


    # Okienko podpiete pod dodaj kilka sztuk
    def otworz_okno_dodawania_sztuki(self):
        popup = tk.Toplevel(self)
        popup.title("Potwierdzenie")
        popup.geometry("250x120")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)

        # Wymiary okienka
        popup_width = 250
        popup_height = 120

        # Rozmiar ekranu
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        # Pozycja startowa (środek)
        x = int((screen_width / 2) - (popup_width / 2))
        y = int((screen_height / 2) - (popup_height / 2))

        # Ustawienie geometrii
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        popup.grab_set()
        popup.focus_force()

        label = tk.Label(popup, text="Produkt został dodany ✅",
                         font=("Arial", 12), bg="#ffffff", fg="black")
        label.pack(pady=(20, 10))

        ok_btn = tk.Button(popup, text="OK", font=("Arial", 11),
                           bg="#1e90ff", fg="white", width=10,
                           command=popup.destroy)
        ok_btn.pack(pady=(0, 15))
        # Ustawienie fokusu na przycisk OK, żeby Enter działał od razu
        ok_btn.focus_set()

        popup.bind("<Return>", lambda event: ok_btn.invoke())

    # okienko skanowania produktów do dodaj
    def otworz_okno_skanowania_dodaj(self):
        popup = tk.Toplevel(self)
        popup.title("Skanowanie produktów")
        popup.geometry("400x300")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)

        self.zeskanowane_produkty = []

        label = tk.Label(popup, text="Zeskanuj produkty 📦", font=("Arial", 12), bg="#ffffff")
        label.pack(pady=(10, 5))

        entry = tk.Entry(popup, font=("Arial", 12), width=30)
        entry.pack(pady=(0, 10))
        entry.focus_set()

        listbox = tk.Listbox(popup, font=("Arial", 11), width=40, height=8)
        listbox.pack(pady=(0, 10))


        def dodaj_produkt(event=None):
            kod = entry.get().strip()
            if kod:
                self.zeskanowane_produkty.append(kod)
                listbox.insert(tk.END, kod)
                entry.delete(0, tk.END)

        entry.bind("<Return>", dodaj_produkt)


        def zatwierdz():
            popup.destroy()
            ilosc_zeskanowanych = len(self.zeskanowane_produkty)
            self.zasoby, flaga, Kody_nie_baza = dodaj_produkty(self.zeskanowane_produkty, self.baza, self.zasoby)
            self.odswiez_tabele()
            ilosc_kody_nie_w_baza = len(Kody_nie_baza)
            print(f"Zatwierdzono: {self.zeskanowane_produkty}")

            if ilosc_kody_nie_w_baza == 0:
                messagebox.showinfo("Dodano", "Produkt został dodany do zasobów.")
                print("✅ Wszytstkie produkty zostały dodane do zasobów. ")
            #elif ilosc_kody_nie_w_baza > 0 and ilosc_zeskanowanych > ilosc_kody_nie_w_baza:
            elif ilosc_kody_nie_w_baza == ilosc_zeskanowanych:
                messagebox.showerror("Błąd",f"Brak kodów: {", ".join(Kody_nie_baza)} w bazie, dodaj ręcznie lub importuj do bazy.")
                print("❌ Wszytskie wprowadzone produkty nie istnieją w bazie. " )
            else:
                messagebox.showwarning("Informacja", f"Część produktów została pomyślnie dodana do zasobów. Jednak produkty o kodach: {", ".join(Kody_nie_baza)} nie zostały dodane. ")
                print(f"🟠 Część produktów została pomyślnie dodana do zasobów. Jednak produkty o kodach: {", ".join(Kody_nie_baza)} nie zostały dodane. ")
            # Możesz tu przekazać listę dalej, np. do innej funkcji

        zatwierdz_btn = tk.Button(popup, text="Zatwierdź", font=("Arial", 11),
                                  bg="#28a745", fg="white", width=10,
                                  command=zatwierdz)
        zatwierdz_btn.pack(pady=(5, 10))

        zamknij_btn = tk.Button(popup, text="Anuluj", font=("Arial", 11),
                                bg="#ff4d4d", fg="white", width=10,
                                command=popup.destroy)
        zamknij_btn.pack()


    def otworz_okno_skanowania_usun(self):
        popup = tk.Toplevel(self)
        popup.title("Skanowanie produktów")
        popup.geometry("400x300")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)

        self.zeskanowane_produkty = []
        label = tk.Label(popup, text="Zeskanuj produkty 📦", font=("Arial", 12), bg="#ffffff")
        label.pack(pady=(10, 5))

        entry = tk.Entry(popup, font=("Arial", 12), width=30)
        entry.pack(pady=(0, 10))
        entry.focus_set()

        listbox = tk.Listbox(popup, font=("Arial", 11), width=40, height=8)
        listbox.pack(pady=(0, 10))

        # Dodawanie komanetrza do usniętych
        def pokaz_produkt(event):
            selection = listbox.curselection()
            if selection:
                kod = listbox.get(selection[0])

                # Tworzymy nowe okienko
                info_popup = tk.Toplevel(popup)
                info_popup.title("Informacje o produkcie")
                info_popup.geometry("400x300")

                # Label z kodem produktu
                label = tk.Label(info_popup, text=f"Produkt: {kod}", font=("Arial", 12))
                label.pack(pady=10)

                # Pole do wpisania komentarza
                tekst_label = tk.Label(info_popup, text="Dodaj komentarz: ")
                tekst_label.pack()
                komentarz_text = tk.Text(info_popup, width=40, height=8, font=("Arial", 11))
                komentarz_text.pack(pady=5)


                # Funkcja zapisu dodawanie do danych hisotir itp
                def zapisz_komentarz():
                    komentarz = komentarz_text.get("1.0", tk.END).strip()
                    Data_usuniecia = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Nadano komentarz operacji produktem o kodzie {kod} komentarz do produktu: {komentarz}, {Data_usuniecia}.")
                    temp = {
                        "Kod QR" : kod,
                        "Komentarz" : komentarz,
                        "Data usuniecia" : Data_usuniecia
                    }

                    #self.komentarze = funkcja do dodawania koljenej rubryki
                    self.komentarze = dodaj_komentarz(self.komentarze, temp)
                    # messagebox.showinfo("Zapisano", f"Komentarz dodany do {kod}") # chyba nie potrzebna bo trohe modyfikuje
                    info_popup.destroy()

                zapisz_btn = tk.Button(info_popup, text="Zapisz", bg="#28a745", fg="white",
                                       command=zapisz_komentarz)
                zapisz_btn.pack(pady=10)

        listbox.bind("<Double-Button-1>", pokaz_produkt)


        def dodaj_produkt(event=None):
            kod = entry.get().strip()
            if kod:
                self.zeskanowane_produkty.append(kod)
                listbox.insert(tk.END, kod)
                entry.delete(0, tk.END)

        entry.bind("<Return>", dodaj_produkt)


        def zatwierdz():
            popup.destroy()
            self.zasoby, Zle_kody = usun_produkt_z_zasobow(self.zeskanowane_produkty, self.zasoby, self.baza)
            self.zasoby = czysc_mniej_0(self.zasoby)
            ilosc_zeskanowanych = len(self.zeskanowane_produkty)
            ilosc_zle_kody = len(Zle_kody)
            print(f"Zatwierdzono: {", ".join(self.zeskanowane_produkty)}")

            if ilosc_zle_kody == 0:
                messagebox.showinfo("Usunięto", "Produkty zostały pomyślnie usunięte z zasobów.")
                print("✅ Produkty zostały pomyślnie usunięte z zasobów. ")

            elif ilosc_zle_kody == ilosc_zeskanowanych:
                messagebox.showerror("Błąd",f"Brak kodów: {", ".join(Zle_kody)} w zasobach.")
                print(f"❌ Podanych produktów {", ".join(Zle_kody)} nie ma w zasobach.")
            else:
                messagebox.showwarning("Informacja", f" Część produktów została pomyślnie usunięta z zasobów. Jednak produkty o kodach: {", ".join(Zle_kody)} nie istnieją w zasobach. ")
                print(f"🟠 Część produktów została pomyślnie usunięta z zasobów. ")
            self.odswiez_tabele()

            # Możesz tu przekazać listę dalej, np. do innej funkcji
        zatwierdz_btn = tk.Button(popup, text="Zatwierdź", font=("Arial", 11),
                                  bg="#28a745", fg="white", width=10,
                                  command=zatwierdz)
        zatwierdz_btn.pack(pady=(5, 10))

        zamknij_btn = tk.Button(popup, text="Anuluj", font=("Arial", 11),
                                bg="#ff4d4d", fg="white", width=10,
                                command=popup.destroy)
        zamknij_btn.pack()


    # Okno podpięte pood dodaj kilka sztuk
    def okno_dodaj_hurtem(self):
        popup = tk.Toplevel(self)
        popup.title("Dodaj kilka sztuk produktu")
        popup.geometry("500x220")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        kod_label = tk.Label(popup, text="Kod kreskowy:", font=("Arial", 11), bg="#ffffff")
        kod_label.pack(pady=(15, 5))
        kod_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        kod_entry.pack(pady=(0, 10))
        kod_entry.focus_set()
        ilosc_label = tk.Label(popup, text="Ilość:", font=("Arial", 11), bg="#ffffff")
        ilosc_label.pack(pady=(5, 5))
        ilosc_entry = tk.Entry(popup, font=("Arial", 12), width=10)
        ilosc_entry.pack(pady=(0, 10))


        def zatwierdz():
            kod = kod_entry.get().strip()
            ilosc = ilosc_entry.get().strip()
            if kod and ilosc.isdigit() and int(ilosc) > 0:
                self.zeskanowany_produkt = {"kod": kod, "ilosc": int(ilosc)}
                print("Zatwierdzono: ", self.zeskanowany_produkt)
                self.zasoby, flaga = dodaj_kilka_sztuk(kod, self.baza, self.zasoby, int(ilosc))
                self.odswiez_tabele()
                popup.destroy()
                # funkcja patrzy czy jest w bazie i zwraca komunikat
                if flaga:
                    messagebox.showinfo("Dodano kilka sztuk wprowadzonego produktu", "Pomyślnie dodano podaną ilość sztuk wprowadzonego produktu.")
                    print("✅ Dodano kilka sztuk podanego produktu.")
                else:
                    messagebox.showerror("Błąd","Brak podanego produktu w bazie. Wprowadź go ręcznie lub importuj do bazy.")
                    print("❌ Brak podanego produktu w bazie.")
            else:
                messagebox.showerror("Błąd","Wprowadź kod lub ilość w poprawnym formacie.")


        def anuluj():
            self.zeskanowany_produkt = None
            popup.destroy()

        zatwierdz_btn = tk.Button(popup, text="Zatwierdź", font=("Arial", 11),
                                  bg="#28a745", fg="white", width=10,
                                  command=zatwierdz)
        zatwierdz_btn.pack(pady=(5, 5))

        anuluj_btn = tk.Button(popup, text="Anuluj", font=("Arial", 11),
                               bg="#ff4d4d", fg="white", width=10,
                               command=anuluj)
        anuluj_btn.pack()
        # Enter działa
        popup.bind("<Return>", lambda event: zatwierdz())


    def okno_usun_hurtem(self):
        popup = tk.Toplevel(self)
        popup.title("Usuń kilka sztuk danego produktu")
        popup.geometry("500x350")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        kod_label = tk.Label(popup, text="Kod kreskowy:", font=("Arial", 11), bg="#ffffff")
        kod_label.pack(pady=(15, 5))
        kod_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        kod_entry.pack(pady=(0, 10))
        kod_entry.focus_set()
        ilosc_label = tk.Label(popup, text="Ilość:", font=("Arial", 11), bg="#ffffff")
        ilosc_label.pack(pady=(5, 10))
        ilosc_entry = tk.Entry(popup, font=("Arial", 12), width=20)
        ilosc_entry.pack(pady=(5, 10))


        def zatwierdz():
            kod = kod_entry.get().strip()
            ilosc = ilosc_entry.get().strip()
            if kod and ilosc.isdigit() and int(ilosc) > 0: ### Napisac funkcje ktora usuwa hurtowo
                self.zeskanowany_produkt = {"kod": kod, "ilosc": int(ilosc)}

                print("Zatwierdzono: ", self.zeskanowany_produkt)
                self.zasoby, flaga = usun_kilka_sztuk(kod, self.baza, self.zasoby, int(ilosc))
                if flaga:
                    odpowiedz = messagebox.askyesno("", "Czy chcesz dodać komentarz?")
                    if odpowiedz:
                        print("Dodaj komentarz.")
                        # Szkielet okna
                        info_popup = tk.Toplevel(popup)
                        info_popup.title("Informacje o produkcie")
                        info_popup.geometry("400x300")


                        # Label z kodem produktu
                        label = tk.Label(info_popup, text=f"Produkt: {kod}", font=("Arial", 12))
                        label.pack(pady=10)

                        def zapisz_komentarz():
                            komentarz = komentarz_text.get("1.0", tk.END).strip()
                            Data_usuniecia = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(
                                f"Nadano komentarz operacji produktem o kodzie {kod} komentarz do produktu: {komentarz}, {Data_usuniecia}.")
                            temp = {
                                "Kod QR": kod,
                                "Komentarz": komentarz,
                                "Data usuniecia": Data_usuniecia
                            }
                            print(temp)
                            # self.komentarze = funkcja do dodawania koljenej rubryki
                            self.komentarze = dodaj_komentarz(self.komentarze, temp)
                            # messagebox.showinfo("Zapisano", f"Komentarz dodany do {kod}") # chyba nie potrzebna bo trohe modyfikuje
                            info_popup.destroy()


                        # Pole do wpisania komentarza
                        tekst_label = tk.Label(info_popup, text="Dodaj komentarz: ")
                        tekst_label.pack()
                        komentarz_text = tk.Text(info_popup, width=40, height=8, font=("Arial", 11))
                        komentarz_text.pack(pady=5)

                        zapisz_btn = tk.Button(info_popup, text="Zapisz", bg="#28a745", fg="white",
                                               command=zapisz_komentarz)
                        zapisz_btn.pack(pady=10)


                        info_popup.wait_window()
                    else:
                        print("Nie dodano komentarza.")
                        messagebox.showinfo("Usunięto pomyślnie", "Usunięto pomyślnie.")
                    print("✅ Wprowadzona ilość sztuk podanego produktu została odjęta pomyślnie.")
                else:
                    messagebox.showerror("Błąd", "Brak produktu o podanym kodzie kreskowym w zasobach lub bazie.")
                    print("❌ Brak produktu o podanym kodzie kreskowym w zasobach lub bazie.")
                self.odswiez_tabele()
                popup.destroy()
            else:
                print("❌ Błąd: wpisz kod i poprawną ilość")
                messagebox.showerror("Błąd", "Ilość musi być dodatnią liczbą całkowitą")

        def anuluj():
            self.zeskanowany_produkt = None
            popup.destroy()

        zatwierdz_btn = tk.Button(popup, text="Zatwierdź", font=("Arial", 11),
                                  bg="#28a745", fg="white", width=10,
                                  command=zatwierdz)
        zatwierdz_btn.pack(pady=(5, 5))

        anuluj_btn = tk.Button(popup, text="Anuluj", font=("Arial", 11),
                               bg="#ff4d4d", fg="white", width=10,
                               command=anuluj)
        anuluj_btn.pack()
        # Enter działa
        popup.bind("<Return>", lambda event: zatwierdz())


    # Okno podpięte pod guzik wprowadź ręcznie
    def okno_wprowadz_ręcznie(self):
        popup = tk.Toplevel(self)
        popup.title("Wprowadź nowy produkt")
        popup.geometry("350x220")
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        kod_label = tk.Label(popup, text="Kod kreskowy:", font=("Arial", 11), bg="#ffffff")
        kod_label.pack(pady=(15, 5))
        kod_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        kod_entry.pack(pady=(0, 10))
        kod_entry.focus_set()
        ilosc_label = tk.Label(popup, text="Podaj nazwę produktu:", font=("Arial", 11), bg="#ffffff")
        ilosc_label.pack(pady=(15, 5))
        ilosc_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        ilosc_entry.pack(pady=(0, 10))


        def zatwierdz():
            kod = kod_entry.get().strip()
            nazwa = ilosc_entry.get().strip()
            if kod and nazwa and not nazwa.isdigit():
                self.zeskanowany_produkt = {"kod": kod, "nazwa": nazwa}
                self.baza, self.zasoby, komunikat = wprowadz_do_baza_i_zasoby(kod, nazwa, self.baza, self.zasoby)
                self.odswiez_tabele()
                messagebox.showinfo("Wprowadzenie produktu", ", ".join(komunikat))
                print("Zatwierdzono:", self.zeskanowany_produkt)
                print(f"✅ Pomyślnie wprowadzono produkty: {self.zeskanowany_produkt} do bazy i zasobów.")
                popup.destroy()
            else:
                print("❌ Błąd: wpisz kod i poprawną ilość")

        def anuluj():
            self.zeskanowany_produkt = None
            popup.destroy()

        zatwierdz_btn = tk.Button(popup, text="Zatwierdź", font=("Arial", 11),
                                  bg="#28a745", fg="white", width=10,
                                  command=zatwierdz)
        zatwierdz_btn.pack(pady=(5, 5))

        anuluj_btn = tk.Button(popup, text="Anuluj", font=("Arial", 11),
                               bg="#ff4d4d", fg="white", width=10,
                               command=anuluj)
        anuluj_btn.pack()

        # Enter działa
        popup.bind("<Return>", lambda event: zatwierdz())


    def to_pdf(self):
        ok, result = dataframe_to_pdf(self.zasoby, filename="zasoby.pdf")
        if ok:
            messagebox.showinfo("Sukces", f"PDF zapisany: {result}.")
        else:
            messagebox.showerror("Błąd", f"Nie udało się zapisac pdf.")



    def otworz_historie(self):
        #nowe okno
        historia = tk.Toplevel(self)
        historia.title("Historia")
        historia.geometry("800x600")
        historia.configure(bg="#ffffff")
        # naglowek
        naglowek = tk.Label(historia, text="Historia",
                            font=("Segoe UI", 24, "bold"),
                            bg="#ffffff", fg="black")
        naglowek.pack(pady=10)

        #stylizacja
        style = ttk.Style(historia)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        foreground="black",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#ffffff",
                        foreground="black",
                        borderwidth=0)

        # główna ramka (2 kolumny: lewy margines + prawa tabela)
        main_frame = tk.Frame(historia, bg="#ffffff")
        main_frame.pack(fill="both", expand=True)

        # lewy margines
        left_margin = tk.Frame(main_frame, width=0, bg="#f8f8f8")
        left_margin.pack(side="left", fill="y")
        left_margin.pack_propagate(False)

        # prawa część (wyszukiwarka + tabela)
        tabela_frame = tk.Frame(main_frame, padx=70, pady=70, bg="#ffffff")
        tabela_frame.pack(side="right", fill="both", expand=True)

        # --- wyszukiwarka ---
        search_frame = tk.Frame(tabela_frame, bg="#ffffff")
        search_frame.pack(pady=(0, 10), fill="x")

        search_var = tk.StringVar()

        search_entry = tk.Entry(search_frame, textvariable=search_var,
                                font=("Arial", 14), bg="#ffffff", fg="black",
                                relief="solid", bd=1)
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))

        # placeholder na przycisk lupy
        search_btn = tk.Button(search_frame, text="🔍", font=("Arial", 12),
                               bg="#1e90ff", fg="white", width=4)
        search_btn.pack(side="left", padx=(0, 10))

        # --- scrollbar + tabela ---
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        hscroll = ttk.Scrollbar(tabela_frame, orient="horizontal")
        hscroll.pack(side="bottom", fill="x")



        columns = list(self.komentarze.columns)
        tree= ttk.Treeview(tabela_frame, columns=columns, show="headings",
                            yscrollcommand=scrollbar.set, xscrollcommand=hscroll.set)


        scrollbar.config(command=tree.yview)###
        hscroll.config(command=tree.xview) ###

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor="center")

        tree.pack(expand=True, fill="both")

        # funkcje pomocnicze (lokalne)
        def zaladuj_dane(df):
            tree.delete(*tree.get_children())

            if "Data usuniecia" in df.columns:
                df = df.sort_values(by="Data usuniecia", ascending=False)


            for _, row in df.iterrows():
                tree.insert("", "end", values=list(row))

        def szukaj():
            q = search_var.get().strip().lower()
            if not q:
                zaladuj_dane(self.komentarze)
                return
            mask = self.komentarze.apply(
                lambda r: any(q in str(v).lower() for v in r), axis=1
            )
            zaladuj_dane(self.komentarze[mask])

            # popup po dwukliku – pokazuje pełny komentarz (i datę, i kod)



        def on_row_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            values = tree.item(sel[0], "values")
            if not values:
                return

            cols = list(tree["columns"])
            # znajdź indeksy potrzebnych kolumn (tolerancja dla ę/braku ę)
            idx_kod = cols.index("Kod QR") if "Kod QR" in cols else 0
            nazwa_data1 = "Data usunięcia"
            nazwa_data2 = "Data usuniecia"
            idx_data = cols.index(nazwa_data1) if nazwa_data1 in cols else (
                cols.index(nazwa_data2) if nazwa_data2 in cols else None)
            idx_kom = cols.index("Komentarz") if "Komentarz" in cols else None

            kod = values[idx_kod] if idx_kod is not None else ""
            data = values[idx_data] if idx_data is not None else ""
            kom = values[idx_kom] if idx_kom is not None else ""

            popup = tk.Toplevel(historia)
            popup.title("Szczegóły komentarza")
            popup.geometry("520x300")
            popup.configure(bg="#ffffff")

            tk.Label(popup, text=f"Kod QR: {kod}", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w",
                                                                                                     padx=12,
                                                                                                     pady=(12, 4))
            if data:
                tk.Label(popup, text=f"Data: {data}", font=("Segoe UI", 11), bg="#ffffff").pack(anchor="w", padx=12,
                                                                                                pady=(0, 8))

            frame_t = tk.Frame(popup, bg="#ffffff")
            frame_t.pack(fill="both", expand=True, padx=12, pady=8)

            txt = tk.Text(frame_t, wrap="word", font=("Arial", 11))
            txt.pack(side="left", fill="both", expand=True)
            scr = ttk.Scrollbar(frame_t, orient="vertical", command=txt.yview)
            scr.pack(side="right", fill="y")
            txt.configure(yscrollcommand=scr.set)

            txt.insert("1.0", kom if kom else "(brak treści)")
            txt.configure(state="disabled")

            tk.Button(popup, text="Zamknij", command=popup.destroy, bg="#1e90ff", fg="white").pack(pady=10)


        # podpięcia
        search_btn.config(command=szukaj)
        search_entry.bind("<Return>", lambda e: szukaj())
        tree.bind("<Double-1>", on_row_double_click)


        # --- Guzik Zamknij ---
        btn_frame = tk.Frame(historia, bg="#ffffff")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Zamknij",
            command=historia.destroy,
            bg="#1e90ff",
            fg="white",
            font=("Arial", 12),
            width=15
        ).pack()

        zaladuj_dane(self.komentarze)