import psycopg2
import pandas as pd
from psycopg2.extras import execute_values


# Tworzy DataFrame w pandas i konwertuje tabele z SQL na pandas (Baza)
def baza_sql_read(dane_baza):
    baza = pd.DataFrame(columns=["Kod QR", "Nazwa"])
    for row in dane_baza:
        wiersz = pd.DataFrame([{"Kod QR": row[0], "Nazwa": row[1]}])
        baza = pd.concat([baza, wiersz], ignore_index=True)
    return baza


# Tworzy DataFrame w pandas i konwertuje tabele z SQL na pandas (Zasoby)
def zasoby_sql_read(dane_zasoby):
    zasoby = pd.DataFrame(columns=["Kod QR", "Nazwa", "Ilosc"])
    for row in dane_zasoby:
        wiersz = pd.DataFrame([{"Kod QR": row[0], "Nazwa": row[1], "Ilosc": row[2]}])
        zasoby = pd.concat([zasoby, wiersz], ignore_index=True)
    return zasoby


# Tworzy DataFrame w pandas i konwertuje tabele z SQL na pandas (komentarz)
def komentarze_sql_read(dane_komentarze):
    komentarze = pd.DataFrame(columns=["Kod QR", "Komentarz", "Data usuniecia"])
    for row in dane_komentarze:
        wiersz = pd.DataFrame([{"Kod QR": row[0], "Komentarz": row[1], "Data usuniecia": row[2]}])
        komentarze = pd.concat([komentarze, wiersz], ignore_index=True)
    return komentarze


# na tonery trzeb zrobic alternatywe to samo
def postgresql_connection():
    conn = psycopg2.connect(
        dbname="baza_danych",

        user="postgres",

        password="12345serwermagazyn",

        host="localhost",

        port="5432"
    )

    cur = conn.cursor() # kursor zapytania do SQL

    # Zapytanie do tabeli baza. Prawdpodbnie trzeba bedzie z tego napisac funkcje i uzyc w main
    cur.execute("SELECT * FROM baza;") # egzekwowanie zapytań do SQL
    dane_baza = cur.fetchall()

    # Zapytanie do tabeli zasoby. To samo co powyżej, bedzie trzeba czytac te tuple jako pandasowy DataFrame
    cur.execute("SELECT * FROM zasoby;")
    dane_zasoby = cur.fetchall()

    cur.execute("SELECT * FROM komentarze;")
    dane_komentarze = cur.fetchall()


    # W tym miejscu funkcje: baza_sql_read, zasoby_sql_read
    baza = baza_sql_read(dane_baza)
    zasoby = zasoby_sql_read(dane_zasoby)
    komentarze = komentarze_sql_read(dane_komentarze)


    #coonn. close , cur.close itp tu byly test
    # return baza_sql_read(dane_baza), zasoby_sql_read(dane_zasoby), # mozliwy return zeby zwracal odpowiednio i pozniej to podpiac pod zmienna
    return baza, zasoby, conn, komentarze


# Do edytowania trzeba zrobic tak, azeby czytalo z tonerow
# ZDAJE SIĘ ŻE NALEŻY WZIĄC FUNKCJE TE SAME DO READ NA PANDAS
def postgresql_connection_tonery():
    conn = psycopg2.connect(
        dbname="baza_danych",

        user="postgres",

        password="12345serwermagazyn",

        host="localhost",

        port="5432"
    )

    cur = conn.cursor()  # kursor zapytania do SQL

    # Zapytanie do tabeli baza. Prawdpodbnie trzeba bedzie z tego napisac funkcje i uzyc w main
    cur.execute("SELECT * FROM baza_tonery;")  # egzekwowanie zapytań do SQL
    dane_baza = cur.fetchall()

    # Zapytanie do tabeli zasoby. To samo co powyżej, bedzie trzeba czytac te tuple jako pandasowy DataFrame
    cur.execute("SELECT * FROM zasoby_tonery;")
    dane_zasoby = cur.fetchall()

    cur.execute("SELECT * FROM komentarze_tonery;")
    dane_komentarze = cur.fetchall()

    # W tym miejscu funkcje: baza_sql_read, zasoby_sql_read
    baza = baza_sql_read(dane_baza)
    zasoby = zasoby_sql_read(dane_zasoby)
    komentarze = komentarze_sql_read(dane_komentarze)

    # coonn. close , cur.close itp tu byly test
    # return baza_sql_read(dane_baza), zasoby_sql_read(dane_zasoby), # mozliwy return zeby zwracal odpowiednio i pozniej to podpiac pod zmienna
    return baza, zasoby, conn, komentarze



def zasoby_save(zasoby, cur):
    cur.execute("TRUNCATE TABLE zasoby;")
    values_zasoby = [(row["Kod QR"], row["Nazwa"], row["Ilosc"]) for _, row in zasoby.iterrows()]
    query = """
    INSERT INTO zasoby (kod_qr, nazwa, Ilosc)
    VALUES %s;
    """
    execute_values(cur, query, values_zasoby)
    return "Zasoby zostały zapisane"



def baza_save(baza, cur):
    cur.execute("TRUNCATE TABLE baza;") # usuwa stare
    values_baza = [(row["Kod QR"], row["Nazwa"]) for _, row in baza.iterrows()]
    # Zapytanie SQL
    query = """
    INSERT INTO baza (kod_qr, "Nazwa")
    VALUES %s;
    """
    execute_values(cur, query, values_baza)
    return "Baza zodtała zapisana"


############testy
def komentarze_save(komentarze, cur):
    cur.execute("TRUNCATE TABLE komentarze;")
    values_komentarze = [(row["Kod QR"], row["Komentarz"], row["Data usuniecia"]) for _, row in komentarze.iterrows()]
    query = """
        INSERT INTO komentarze (kod_qr, komentarz, data_usuniecia)
        VALUES %s;
        """
    execute_values(cur, query, values_komentarze)
    return "Komentarze zostały zapisane"
##############


# Save od razu na calość baza i zasoby ################################# usnac komenartze
def save(baza, zasoby, conn, komentarze):
    # Zasoby save
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE zasoby;")
    values_zasoby = [(row["Kod QR"], row["Nazwa"], row["Ilosc"]) for _, row in zasoby.iterrows()]
    query = """
    INSERT INTO zasoby (kod_qr, nazwa, Ilosc)
    VALUES %s;
    """
    execute_values(cur, query, values_zasoby)


    # Baza Save
    cur.execute("TRUNCATE TABLE baza;")  # usuwa stare
    values_baza = [(row["Kod QR"], row["Nazwa"]) for _, row in baza.iterrows()]
    # Zapytanie SQL
    query = """
    INSERT INTO baza (kod_qr, "Nazwa")
    VALUES %s;
    """
    execute_values(cur, query, values_baza)



    # Komentarze save test
    cur.execute("TRUNCATE TABLE komentarze;")
    values_komentarze = [(row["Kod QR"], row["Komentarz"], row["Data usuniecia"]) for _, row in komentarze.iterrows()]
    query = """
    INSERT INTO komentarze (kod_qr, komentarz, data_usuniecia)
    VALUES %s;
    """
    execute_values(cur, query, values_komentarze)



    #Zamkniecie
    conn.commit()
    cur.close()
    conn.close()
    return "Dane zostały zapisane w bazie"



def save_tonery(baza, zasoby, conn, komentarze):
    # Zasoby save
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE zasoby_tonery;")
    values_zasoby = [(row["Kod QR"], row["Nazwa"], row["Ilosc"]) for _, row in zasoby.iterrows()]
    query = """
    INSERT INTO zasoby_tonery (kod_qr, nazwa, Ilosc)
    VALUES %s;
    """
    execute_values(cur, query, values_zasoby)


    # Baza Save
    cur.execute("TRUNCATE TABLE baza_tonery;")  # usuwa stare
    values_baza = [(row["Kod QR"], row["Nazwa"]) for _, row in baza.iterrows()]
    # Zapytanie SQL
    query = """
    INSERT INTO baza_tonery (kod_qr, "Nazwa")
    VALUES %s;
    """
    execute_values(cur, query, values_baza)



    # Komentarze save test
    cur.execute("TRUNCATE TABLE komentarze_tonery;")
    values_komentarze = [(row["Kod QR"], row["Komentarz"], row["Data usuniecia"]) for _, row in komentarze.iterrows()]
    query = """
    INSERT INTO komentarze_tonery (kod_qr, komentarz, data_usuniecia)
    VALUES %s;
    """
    execute_values(cur, query, values_komentarze)



    #Zamkniecie
    conn.commit()
    cur.close()
    conn.close()
    return "Dane zostały zapisane w bazie"


# mozna zastosowac ta sama funkcje bardzie juniwersalnie do tego podejsc
# patrz funkcja wybierz_konektor(save, save_tonery, connect) .... dla przykladu