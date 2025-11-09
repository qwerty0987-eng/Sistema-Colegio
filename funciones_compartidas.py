from database import coneccion
from tkinter import messagebox
import tkinter as tk

def ejecutar_sql(query, params=None, fetch=False, commit=False):
    conn=coneccion()
    if not conn: return None
    try:
        cur=conn.cursor()
        cur.execute(query, params or ())
        result=cur.fetchall() if fetch else (cur.fetchone() if fetch is not False else None)
        if commit: conn.commit()
        return result
    except Exception as e:
        if conn: conn.rollback()
        messagebox.showerror("Error", str(e))
        return None
    finally:
        if conn: conn.close()

def limpiar_vars(vars_dict):
    for v in vars_dict.values(): v.set("")
    return {}

def centrar_ventana(root, w, h):
    root.geometry(f"{w}x{h}")
    root.update_idletasks()
    x=(root.winfo_screenwidth()//2)-(root.winfo_width()//2)
    y=(root.winfo_screenheight()//2)-(root.winfo_height()//2)
    root.geometry(f"+{x}+{y}")
    root.resizable(False, False)