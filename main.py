from db import postgresql_connection, postgresql_connection_tonery
from gui import GUI
from logic import on_close


if __name__ == "__main__":
    baza, zasoby, conn, komentarze = postgresql_connection() #### / postgresql_connction()
    app = GUI(baza, zasoby, komentarze)
    app.protocol("WM_DELETE_WINDOW", lambda: on_close(app, conn))
    app.mainloop()