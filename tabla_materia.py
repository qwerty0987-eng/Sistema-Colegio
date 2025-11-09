import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from temas import aplicar_tema
from funciones_compartidas import ejecutar_sql, limpiar_vars, centrar_ventana
import unicodedata

class App_registro_materia:
    def __init__(self, root):
        self.root=aplicar_tema(root)
        self.root.title("REGISTRO DE MATERIAS")
        centrar_ventana(self.root, 1800, 480)
        self.root.resizable(False, False)
        self.vars={c: tk.StringVar() for c in ["ID Materia", "Nombre", "Área", "Aula", "Capacidad", "Estado", "Turno"]}
        self.crear_interfaz()
        self.cargar_aulas()
        self.cargar_turnos()

    def crear_interfaz(self):
        marco=ttkb.Labelframe(self.root, text="GESTIÓN DE MATERIAS", bootstyle="primary")
        marco.pack(padx=20, pady=20, fill="both", expand=True)

        # Formulario
        form=ttkb.Frame(marco); form.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        campos=list(self.vars.keys())
        for i, c in enumerate(campos):
            ttkb.Label(form, text=f"{c}:", anchor="center").grid(row=i, column=0, padx=6, pady=6, sticky="e")
            if c=="Aula":
                self.combo_aula=ttkb.Combobox(form, textvariable=self.vars[c], width=28, state="readonly")
                self.combo_aula.bind("<<ComboboxSelected>>", self.actualizar_datos_aula)
                self.combo_aula.grid(row=i, column=1, padx=6, pady=6, sticky="w")
            elif c=="Turno":
                self.combo_turno=ttkb.Combobox(form, textvariable=self.vars[c], width=28, state="readonly")
                self.combo_turno.grid(row=i, column=1, padx=6, pady=6, sticky="w")
            else:
                ttkb.Entry(form, textvariable=self.vars[c], bootstyle="dark", justify="center", width=28).grid(
                    row=i, column=1, padx=6, pady=6, sticky="w")

        btns=ttkb.Frame(form); btns.grid(row=len(campos), column=0, columnspan=2, pady=10)
        for i, (txt, sty, cmd) in enumerate([
            ("Agregar", "success", self.agregar),
            ("Actualizar", "warning", self.actualizar),
            ("Eliminar", "danger", self.eliminar),
            ("Limpiar", "light", self.limpiar)]):
            ttkb.Button(btns, text=txt, bootstyle=f"{sty}-outline", width=14, command=cmd).grid(row=0, column=i, padx=5)

        bus=ttkb.Frame(form); bus.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)
        ttkb.Label(bus, text="Buscar por:").pack(side="left", padx=5)
        self.col_busqueda = ttkb.Combobox(bus, state="readonly", width=18, bootstyle="dark",
                                          values=["ID Materia", "Nombre", "Área", "Aula", "Estado", "Turno"])
        self.col_busqueda.pack(side="left", padx=5); self.col_busqueda.current(0)
        ttkb.Label(bus, text="Valor:").pack(side="left", padx=5)
        self.buscar_var=tk.StringVar()
        ttkb.Entry(bus, textvariable=self.buscar_var, width=25, bootstyle="dark").pack(side="left", padx=5)
        ttkb.Button(bus, text="Buscar", bootstyle="info-outline", command=self.buscar).pack(side="left", padx=5)
        ttkb.Button(bus, text="Mostrar todo", bootstyle="success-outline", command=self.mostrar).pack(side="left", padx=5)

        tabla_frame=ttkb.Frame(marco); tabla_frame.grid(row=0, column=1, rowspan=12, padx=10, pady=10, sticky="nsew")
        cols=("ID Materia", "Nombre", "Área", "Aula", "Capacidad", "Estado", "Turno")
        self.tabla=ttkb.Treeview(tabla_frame, columns=cols, show="headings", bootstyle="dark")
        for c in cols:
            self.tabla.heading(c, text=c, anchor="center")
            self.tabla.column(c, anchor="center", width=150)
        vsb=ttkb.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=vsb.set); vsb.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<ButtonRelease-1>", self.seleccionar)

        marco.grid_columnconfigure(1, weight=1)
        marco.grid_rowconfigure(0, weight=1)

    def cargar_aulas(self):
        filas=ejecutar_sql("SELECT id_aula, capacidad, estado FROM aula ORDER BY id_aula;", fetch=True)
        valores=[f"{r[0]} - Cap:{r[1]} - {r[2]}" for r in (filas or [])]
        self.combo_aula["values"]=valores

    def cargar_turnos(self):
        filas=ejecutar_sql("SELECT DISTINCT turno FROM horario WHERE turno IS NOT NULL;", fetch=True)
        turnos=[r[0] for r in (filas or [])] or ["Mañana", "Tarde", "Noche"]
        self.combo_turno["values"] = turnos

    def mostrar(self):
        filas=ejecutar_sql("""SELECT m.id_materia, m.nombre_materia, m.area,
                   COALESCE(a.id_aula::text, 'Sin Aula'),
                   COALESCE(a.capacidad::text, '-'),
                   COALESCE(a.estado, '-'),
                   COALESCE(h.turno, '-')
            FROM materia m
            LEFT JOIN materia_aula ma ON m.id_materia = ma.id_materia
            LEFT JOIN aula a ON ma.id_aula = a.id_aula
            LEFT JOIN horario h ON a.id_aula = h.id_aula
            ORDER BY m.id_materia;""", fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)

    def generar_codigo_materia(self, nombre):
        if not nombre: return None
        texto=unicodedata.normalize('NFKD', nombre).upper()
        prefijo=''.join(c for c in texto if c.isalpha())[:3]
        n=1
        while True:
            codigo=f"{prefijo}-{str(n).zfill(2)}"
            if not ejecutar_sql("SELECT 1 FROM materia WHERE id_materia=%s;", (codigo,), fetch=True):
                return codigo
            n+=1

    def agregar(self):
        nombre=self.vars["Nombre"].get().strip()
        area=self.vars["Área"].get().strip()
        aula_info=self.vars["Aula"].get().strip()
        turno=self.vars["Turno"].get().strip()
        if not nombre:
            return messagebox.showwarning("Advertencia", "Ingrese el nombre de la materia.")

        tipo_id=ejecutar_sql("SELECT data_type FROM information_schema.columns WHERE table_name='materia' AND column_name='id_materia';", fetch=True)
        tipo=tipo_id[0][0] if tipo_id else "text"

        if "char" in tipo or "text" in tipo:
            id_materia = self.generar_codigo_materia(nombre)
            if not id_materia: return
            ejecutar_sql("INSERT INTO materia (id_materia, nombre_materia, area) VALUES (%s,%s,%s);", (id_materia, nombre, area), commit=True)
        else:
            id_materia=ejecutar_sql("INSERT INTO materia (nombre_materia, area) VALUES (%s,%s) RETURNING id_materia;", (nombre, area), fetch=True, commit=True)[0][0]

        if aula_info:
            id_aula=aula_info.split(" - ")[0]
            ejecutar_sql("DELETE FROM materia_aula WHERE id_materia=%s;", (id_materia,), commit=True)
            ejecutar_sql("INSERT INTO materia_aula (id_materia, id_aula) VALUES (%s,%s);", (id_materia, id_aula), commit=True)
            ejecutar_sql("UPDATE horario SET turno=%s WHERE id_aula=%s;", (turno, id_aula), commit=True)

        messagebox.showinfo("Éxito", f"Materia '{nombre}' registrada (ID: {id_materia}).", parent=self.root)
        self.mostrar(); self.limpiar()

    def actualizar(self):
        id_materia=self.vars["ID Materia"].get().strip()
        if not id_materia:
            return messagebox.showwarning("Advertencia", "Seleccione una materia.")
        
        nombre=self.vars["Nombre"].get().strip()
        area=self.vars["Área"].get().strip()
        aula_info=self.vars["Aula"].get().strip()
        turno=self.vars["Turno"].get().strip()

        ejecutar_sql("UPDATE materia SET nombre_materia=%s, area=%s WHERE id_materia=%s;", (nombre, area, id_materia), commit=True)

        if aula_info:
            id_aula=aula_info.split(" - ")[0]
            ejecutar_sql("DELETE FROM materia_aula WHERE id_materia=%s;", (id_materia,), commit=True)
            ejecutar_sql("INSERT INTO materia_aula (id_materia, id_aula) VALUES (%s,%s);", (id_materia, id_aula), commit=True)
            ejecutar_sql("UPDATE horario SET turno=%s WHERE id_aula=%s;", (turno, id_aula), commit=True)

        messagebox.showinfo("Éxito", "Materia actualizada.", parent=self.root)
        self.mostrar()

    def actualizar_datos_aula(self, e=None):
        info=self.vars["Aula"].get().strip()
        if not info: return
        id_aula=info.split(" - ")[0]
        fila=ejecutar_sql("SELECT capacidad, estado FROM aula WHERE id_aula=%s;", (id_aula,), fetch=True)
        if fila:
            self.vars["Capacidad"].set(str(fila[0][0]))
            self.vars["Estado"].set(fila[0][1])

    def eliminar(self):
        id_materia=self.vars["ID Materia"].get().strip()
        if not id_materia or not messagebox.askyesno("Confirmar", f"¿Eliminar materia ID {id_materia}?"): return

        ejecutar_sql("DELETE FROM docente WHERE id_materia=%s;", (id_materia,), commit=True)
        ejecutar_sql("DELETE FROM estudiante_materia WHERE id_materia=%s;", (id_materia,), commit=True)
        ejecutar_sql("DELETE FROM materia_aula WHERE id_materia=%s;", (id_materia,), commit=True)
        ejecutar_sql("DELETE FROM materia WHERE id_materia=%s;", (id_materia,), commit=True)

        messagebox.showinfo("Éxito", "Materia eliminada con todas sus relaciones.", parent=self.root)
        self.mostrar(); self.limpiar()

    def limpiar(self):
        limpiar_vars(self.vars)
        self.buscar_var.set("")
        self.cargar_aulas()
        self.cargar_turnos()

    def seleccionar(self, e):
        sel=self.tabla.selection()
        if not sel: return
        valores=self.tabla.item(sel, "values")
        for k, v in zip(self.vars.keys(), valores):
            self.vars[k].set(v)

    def buscar(self):
        texto=self.buscar_var.get().strip()
        col=self.col_busqueda.get()
        if not texto:
            return messagebox.showwarning("Búsqueda", "Ingrese texto.", parent=self.root)

        map_col={
            "ID Materia": "m.id_materia", "Nombre": "m.nombre_materia", "Área": "m.area",
            "Aula": "a.id_aula::text", "Estado": "a.estado", "Turno": "h.turno"
        }
        filas=ejecutar_sql(f"""
            SELECT m.id_materia, m.nombre_materia, m.area,
                   COALESCE(a.id_aula::text, 'Sin Aula'),
                   COALESCE(a.capacidad::text, '-'),
                   COALESCE(a.estado, '-'),
                   COALESCE(h.turno, '-')
            FROM materia m
            LEFT JOIN materia_aula ma ON m.id_materia=ma.id_materia
            LEFT JOIN aula a ON ma.id_aula=a.id_aula
            LEFT JOIN horario h ON a.id_aula=h.id_aula
            WHERE unaccent({map_col.get(col, 'm.nombre_materia')}) ILIKE unaccent(%s)
            ORDER BY m.nombre_materia;""", (f"%{texto}%",), fetch=True)

        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)
        if not filas:
            messagebox.showinfo("Sin resultados", f"No se encontró nada en '{col}' con '{texto}'.", parent=self.root)

if __name__=="__main__":
    root=ttkb.Window(themename="darkly")
    App_registro_materia(root)
    root.mainloop()