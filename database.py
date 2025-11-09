import psycopg2
from tkinter import messagebox

def coneccion():
    try:
        return psycopg2.connect(
            host="localhost", database="bd_proyecto",
            user="postgres", password="123"
        )
    except Exception as e:
        try: messagebox.showerror("Error de conexión", str(e))
        except: print("Error de conexión:", e)
        return None