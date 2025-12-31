import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from pathlib import Path
from datetime import datetime


# Funkcja sprawdza czy wprowadzony kod QR jest w zasoby
def czy_w_zasobach(kod: str, zasoby):
    if kod in zasoby["Kod QR"].values:
        return True
    return False


# Funkcja sprawdza czy wprowadzony kod QR jest w bazie
def czy_w_bazie(kod: str, baza):
    if kod in baza["Kod QR"].values:
        return True
    return False


# Funkcja zwiększa ilość produktu w zasobach o 1
def zwieksz(kod, zasoby):
    zasoby.loc[zasoby["Kod QR"] == kod, "Ilosc"] += 1
    return zasoby


# Funkcja zwieksza o okreslona ilosc danego produktu w zasobach
def zwieksz_ilosc(kod, zasoby, ilosc):
    zasoby.loc[zasoby["Kod QR"] == kod, "Ilosc"] += ilosc
    return zasoby


# Funkcja czyści wszystkie produkty w zasobach, których ilość równa jest 0
def czysc_0_sztuk(zasoby): # czysci tam gdzie sztuki jest po 0 sztuk w zasobach
    zasoby.drop(zasoby[zasoby["Ilosc"] == 0].index, inplace=True)
    return zasoby


# Funkcja czysci tam gdzie jest ilosc mniej niz 0
def czysc_mniej_0(zasoby):
    zasoby.drop(zasoby[zasoby["Ilosc"] <= 0].index, inplace=True)
    return zasoby


# Funkcja czyta plik .xlsx i zamienia w pandasowy DataFrame
def plik_import_read(plik):
    imp_produkty = pd.read_excel(plik)
    return imp_produkty


# Funkcja sprawdza czy podany plik ma poprawna struktura
def sprawdz_plik(imp_produkty):
    komunikaty = []

    # Usunięcie całkowicie pustych wierszy
    imp_produkty.dropna(how='all', inplace=True)

    # Usunięcie wierszy z brakami w którejkolwiek kolumnie
    imp_produkty.dropna(inplace=True)

    # Sprwadzanie czy sa dwie kolumny
    oczekiwane_nazwy_kolumn = ["Kod QR", "Nazwa"]
    if len(imp_produkty.columns) != 2:
        komunikaty = "Nie poprawna ilość wprowadzonych kolumn."
        return False #, komunikaty
    elif list(imp_produkty.columns) != oczekiwane_nazwy_kolumn:
        komunikaty = f"Kolumny wprowadzonego plku nie mają oczekiwanych nazw: {oczekiwane_nazwy_kolumn}."
        return False #, komunikaty
    elif imp_produkty.isnull().values.any():
        komunikaty = "Plik zawiera brakujące dane."
        return False #
    return True #, "Plik nadaje sie do importu"


# Patrzy czy kod juz jest w bazie i jezeli nie ma to dodaje z tych importowanych do bazy.
def dodaj_jeseli_nie_ma(baza, imp_produkty):
    for index, row in imp_produkty.iterrows():
        row["Kod QR"] = str(row["Kod QR"])
        if not czy_w_bazie(str(row["Kod QR"]), baza):
            nowy_wiersz = pd.DataFrame([row.to_dict()])
            baza = pd.concat([baza, nowy_wiersz], ignore_index=True)
    return baza



def dataframe_to_pdf(zasoby, filename="tabela.pdf"):
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        downloads = Path.home() / "Pobrane"
    filepath = downloads / filename

    data = [zasoby.columns.tolist()] + zasoby.values.tolist()
    pdf = SimpleDocTemplate(str(filepath), pagesize=A4)
    table = Table(data)

    style = TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, "black"),
    ])
    table.setStyle(style)

    try:
        pdf.build([table])
        return True, filepath  # ✅ sukces + ścieżka
    except Exception as e:
        return False, str(e)   # ❌ błąd + komunikat




def dodaj_komentarz(komentarze: pd.DataFrame, temp_kom: dict) -> pd.DataFrame:
    df_temp = pd.DataFrame([temp_kom])
    df_temp = df_temp.reindex(columns=komentarze.columns)
    return pd.concat([komentarze, df_temp], ignore_index=True)

