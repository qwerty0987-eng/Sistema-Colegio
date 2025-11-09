import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from funciones_compartidas import centrar_ventana
from tabla_estudiante import App_registro_estudiante
from tabla_materia import App_registro_materia
from tabla_padre import App_registro_padre
from tabla_docente import App_registro_docente

OPCIONES=[("Docentes", App_registro_docente, "info"),
    ("Estudiantes", App_registro_estudiante, "success"),
    ("Materias", App_registro_materia, "light"),
    ("Padres", App_registro_padre, "warning")]
EMOJIS=["👨‍🏫", "🎓", "📘", "👪"]

class InterfazPrincipal:
    def __init__(self, root):
        self.root=root
        self.root.title("Sistema de Registro - Colegio")
        centrar_ventana(self.root, 900, 600)
        self.root.resizable(False, False)
        ttkb.Style("darkly")
        self.root.configure(bg="#0A174E")
        self.logo=None
        try:
            from PIL import Image, ImageTk
            img=Image.open("recursos/logo_colegio_proyecto.png").resize((130, 130), Image.Resampling.LANCZOS)
            self.logo=ImageTk.PhotoImage(img)
        except: pass
        self.crear_bienvenida()
        self.mostrar_bienvenida()

    def header(self, parent, subtitulo="Sistema de Registro Académico"):
        h=ttkb.Frame(parent)
        h.pack(pady=(10, 20))
        if self.logo:
            ttkb.Label(h, image=self.logo).grid(row=0, column=0, rowspan=2, padx=20)
        ttkb.Label(h, text="COLEGIO", font=("Segoe UI", 24, "bold"), foreground="#DAA520").grid(row=0, column=1, sticky="w")
        ttkb.Label(h, text=subtitulo, font=("Segoe UI", 12, "italic"), foreground="#E0E0E0").grid(row=1, column=1, sticky="w")
        return h

    def crear_bienvenida(self):
        f=ttkb.Frame(self.root, padding=25)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        self.frames={"bienvenida": f}
        self.header(f)
        btn=ttkb.Button(f, text="INGRESAR AL SISTEMA", bootstyle="success-outline", width=28, command=self.mostrar_menu)
        btn.place(relx=0.5, rely=0.5, anchor="center")
        n=ttkb.Frame(f)
        n.pack(side="bottom", pady=30)
        ttkb.Label(n, text="Desarrollado por:", font=("Segoe UI", 10, "bold"), foreground="#DAA520").pack()
        for nombre in ["Apaza Mamani Helmer Rudel", "Chavez Mamani Joel Alexis",
                       "Mamani Quispe Miguel Angel", "Tudela Limachi Fabiola Maribel"]:
            ttkb.Label(n, text=f"• {nombre}", font=("Segoe UI", 9), foreground="#E0E0E0").pack(anchor="w", padx=50)

    def crear_menu(self):
        f=ttkb.Frame(self.root, padding=25)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        self.frames["menu"] = f
        self.header(f, "Menú Principal")
        b=ttkb.Frame(f)
        b.pack(pady=30)
        for (texto, modulo, estilo), emoji in zip(OPCIONES, EMOJIS):
            ttkb.Button(
                b, text=f"{emoji} {texto}", width=28,
                bootstyle=f"{estilo}-outline",
                command=lambda m=modulo: self.abrir(m)
            ).pack(pady=8)
        ttkb.Button(f, text="Salir del sistema", bootstyle="danger-outline", width=28,
                    command=self.root.quit).pack(pady=25)

    def mostrar(self, frame):
        [fr.pack_forget() for fr in self.frames.values()]
        self.frames[frame].pack(fill="both", expand=True)

    def mostrar_bienvenida(self): self.mostrar("bienvenida")
    def mostrar_menu(self):
        if "menu" not in self.frames: self.crear_menu()
        self.mostrar("menu")

    def abrir(self, modulo):
        v=tk.Toplevel(self.root)
        v.title(modulo.__name__.replace("App_registro_", ""))
        centrar_ventana(v, 1800, 600)
        v.resizable(False, False)
        v.configure(bg="#0A174E")
        ttkb.Style("darkly")
        modulo(v)
        v.transient(self.root)
        v.lift()
        v.focus_force()
        
        def on_close():
            v.destroy()
            self.root.deiconify()
            self.mostrar_menu()
        v.protocol("WM_DELETE_WINDOW", on_close)

if __name__=="__main__":
    root=ttkb.Window(themename="darkly")
    InterfazPrincipal(root)
    root.mainloop()