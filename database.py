import psycopg2
from tkinter import messagebox

def coneccion():
    try:
        return psycopg2.connect(
            host="localhost", database="ingresar_db",
            user="ingresar_usuario", password="ingresar_contraseña")
    except Exception as e:
        try: messagebox.showerror("Error de conexión", str(e))
        except: print("Error de conexión:", e)
        return None