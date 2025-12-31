import pandas as pd
from pyexpat.errors import messages

from utils import czy_w_bazie, czy_w_zasobach, zwieksz, zwieksz_ilosc, czysc_0_sztuk, czysc_mniej_0, sprawdz_plik, \
    dodaj_jeseli_nie_ma, dataframe_to_pdf
from db import save, postgresql_connection, postgresql_connection_tonery, save_tonery
from tkinter import filedialog



# Funkcja dodaje wprowadzony nowy produkt do zasobów o ile istnieje już w bazie
def dodaj_z_bazy_do_zasobow(baza, zasoby, kod):
    produkt = baza[baza["Kod QR"] == kod]
    nazwa = produkt.iloc[0]["Nazwa"]
    nowy_wiersz = {
        "Kod QR": kod,
        "Nazwa": nazwa,
        "Ilosc": 1
    }
    zasoby = pd.concat([zasoby, pd.DataFrame([nowy_wiersz])], ignore_index=True)
    return zasoby


# Funkcja odejmuje 1 od ilości danego produktu
def zabierz_z_zasobu(kod, zasoby): #zmniejsza ilosc o 1 nalezy sprawdzic czy ilosc 0 jesli tak to usunia wiersz
    zasoby.loc[zasoby["Kod QR"] == kod, "Ilosc"] -= 1
    nazwa = zasoby.loc[zasoby["Kod QR"] == kod, "Nazwa"].values[0]
    print(f"Zmniejszono ilość {nazwa} o 1.")
    return zasoby


# Funkcja odejmuje ilosc od ilości danego produktu
def zabierz_ilosc_z_zasobu(kod, zasoby, ilosc : int): #zmniejsza ilosc o 1 nalezy sprawdzic czy ilosc 0 jesli tak to usunia wiersz
    zasoby.loc[zasoby["Kod QR"] == kod, "Ilosc"] -= ilosc
    nazwa = zasoby.loc[zasoby["Kod QR"] == kod, "Nazwa"].values[0]
    print(f"Zmniejszono ilość {nazwa} o {ilosc}.")
    return zasoby


# LOGIKA funkcja kluczowa, podpieta pod guzik "dodaj produkt", sprwadza czy sa w bazie; jezel nie to zwraca błąd, jezeli tak to sprwadza czy w zasoabch;
# jezeli w zasobach to dodaje +1 do ilosci, jezeli nie to dodaje do do zasobow
def dodaj_produkty(kody_kreskowe, baza, zasoby):
    Kody_nie_baza = []
    flaga = False
    if isinstance(kody_kreskowe, list):
        for kod in kody_kreskowe:
            if czy_w_bazie(kod, baza):# patrzy czy w bazie
                flaga = True
                if czy_w_zasobach(kod, zasoby): # patrzy czy w zasobach
                    zasoby = zwieksz(kod, zasoby) # zwieksza ilosc prdodukty tam gdzie jest podany kod o 1

                else:
                    zasoby = dodaj_z_bazy_do_zasobow(baza, zasoby, kod) # jezeli znajduje sie kod kreskowy w bazie to dodaje do zasobow

            else:
                print(f"Kodu kreskowego {kod} nie ma w bazie, dodaj go do niej ręcznie lub importuj do bazy.")
                Kody_nie_baza.append(kod)
                flaga = False
    elif isinstance(kody_kreskowe, str):
        if czy_w_bazie(kody_kreskowe, baza):
            flaga = True
            if czy_w_zasobach(kody_kreskowe, zasoby):
                zasoby = zwieksz(kody_kreskowe, zasoby)
            else:
                zasoby = dodaj_z_bazy_do_zasobow(baza, zasoby, kody_kreskowe)
        else:
            print(f"Kodu kreskowego {kody_kreskowe} nie ma w bazie, dodaj go do niej ręcznie lub importuj do bazy.")
            Kody_nie_baza.append(kody_kreskowe)
    else:
        raise TypeError("Niepoprawny kod kreskowy.")

    return zasoby, flaga, Kody_nie_baza


# LOGIKA funkcja kluczowa, podpieta pod guzik "Dodaj kilka sztuk", sprawdza czy jest w bazie jezeli nie to blad, jezeli jest w bazie to sprwadz czy w zasobach, jezeli jest w zasobach to dodaje okreslona ilosc,
# jezeli nie to dodaje do zasobow o okreslonej ilosci
def dodaj_kilka_sztuk(kod, baza, zasoby, ilosc : int):
    flaga = False
    if czy_w_bazie(kod, baza):
        flaga = True
        if czy_w_zasobach(kod, zasoby):
            zasoby = zwieksz_ilosc(kod, zasoby, ilosc)
        else: # Jeeli nie ma w zasobach a jest w bazie to powinno dodawac do zasbow
            zasoby = dodaj_z_bazy_do_zasobow(baza, zasoby, kod)
            zasoby = zwieksz_ilosc(kod, zasoby, ilosc - 1)
    return zasoby, flaga


# LOGIKA funkcja kluczowo, podpieta pod guzik "Usun produkty" usuwa w pisane produkty,
# logika dziala identycznie jak w funkcji dodaj produkty
def usun_produkt_z_zasobow(kody_kreskowe, zasoby, baza):
    Zle_kody = []
    if isinstance(kody_kreskowe, list):
        for kod in kody_kreskowe:
            if czy_w_bazie(kod, baza):
                if czy_w_zasobach(kod, zasoby):
                    zasoby = zabierz_z_zasobu(kod, zasoby)
                else:
                    print(f"Brak produktu o kodzie {kod} w zasobach. ")
                    Zle_kody.append(kod)
            else:
                print(f"Brak produktu o kodzie {kod} w bazie.")
                Zle_kody.append(kod)
    elif isinstance(kody_kreskowe, str):
        if czy_w_bazie(kody_kreskowe, baza):
            if czy_w_zasobach(kody_kreskowe, zasoby):
                zasoby = zabierz_z_zasobu(kody_kreskowe, zasoby)
            else:
                Zle_kody.append(kody_kreskowe)
                print(f"Brak kodu {kody_kreskowe} w zasobach.")
        else:
            Zle_kody.append(kody_kreskowe)
            print(f"Brak kodu {kody_kreskowe} w bazie.")
    else:
        return zasoby, Zle_kody
    return czysc_0_sztuk(zasoby), Zle_kody


# LOGIKA funkcja kluczowa, podpieta pod guzik "usun produkty" logika dziala identycznie jak w dodaj_hurtem
def usun_kilka_sztuk(kod, baza, zasoby, ilosc: int):
    flaga = False

    if not isinstance(ilosc, int) or ilosc <= 0:
        print("Ilość musi byc dodatnią liczbą całkowitą.")
        return zasoby, flaga
    if not czy_w_bazie(kod, baza):
        # print("Brak produktu o podanym kodzie kreskowym w bazie.")
        return zasoby, flaga
    if not czy_w_zasobach(kod, zasoby):
        # print("Brak produktu o podanym kodzie kreskowym w zasobach.")
        return zasoby, flaga

    zasoby = zabierz_ilosc_z_zasobu(kod, zasoby, ilosc)
    flaga = True
    return czysc_mniej_0(zasoby), flaga


#funkcja, ktora dodaje do bazy wiersz z nowym kodem qr i nazwa produktu
def dodaj_do_baza(baza, kod, nazwa):
    nowy_przedmiot = {"Kod QR": str(kod), "Nazwa": str(nazwa)}
    nowa_baza = pd.concat([baza, pd.DataFrame([nowy_przedmiot])], ignore_index=True)
    return nowa_baza


# LOGIKA funkcja do wprowadz ręcznie, czyli funkcja, która wprowadza do bazy i zasobów jednocześnie
def wprowadz_do_baza_i_zasoby(kod, nazwa, baza, zasoby):
    komunikaty = []
    if not czy_w_bazie(kod, baza):
        baza = dodaj_do_baza(baza, kod, nazwa)
        if not czy_w_zasobach(kod, zasoby):
            zasoby = dodaj_z_bazy_do_zasobow(baza, zasoby, kod)
            komunikaty.append("Produkt został dodany do bazy i zasobów.")
        else:
            komunikaty.append("Produkt znajduje się w zasobach.")
    else:
        komunikaty.append("Produkt znajduje się w bazie.")
    return baza, zasoby, komunikaty


# Funkcja podpieta pod guzik importu w gui, inicjuje dzialanie wyszukiwarki plikow, czyta tylko pliki xlsx
def import_do_bazy_guzik():
    filepath = filedialog.askopenfilename(
        title="Wybierz plik do importu",
        filetypes=[("Pliki Excel", "*.xlsx"), ("Pliki CSV", "*.csv"), ("Wszystkie pliki", "*.*")]
    )
    if not filepath:
        return False
    try:
        if filepath.endswith(".xlsx"):
            plik = pd.read_excel(filepath, engine='openpyxl')
            print(plik)
        else:
            raise ValueError("Nieobsługiwany format pliku. ")

        return plik


    except Exception as e:
        print(f"Błąd importu: {e}")
        return False


# Importuje do bazy wyczyszczony plik
def import_to_baza_clean(imp_produkty, baza):
    check = sprawdz_plik(imp_produkty)
    if check:
        baza = dodaj_jeseli_nie_ma(baza, imp_produkty)
        return baza
    print("❌ Nie odpowiedni plik zwróć uwagę na jego strukturę.")
    return False


# Wybierz connector podłaczyc pod glowny
def wybierz_konektor(connect):
    if connect:
        return postgresql_connection()
    return postgresql_connection_tonery()


# Funkcja zamyka aplikacje korzysta z save z db gdzie zapisuje baza i zasoby na serwer lokalny
def on_close(app, conn):
    # Możesz tu dodać np. walidację, komunikaty, logowanie
    komunikat = save(app.baza, app.zasoby, conn, app.komentarze) #### tu donrze umiescicic save_tonery
    print(komunikat)
    app.destroy()


