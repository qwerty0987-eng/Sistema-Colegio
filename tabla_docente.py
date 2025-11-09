import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from funciones_compartidas import ejecutar_sql, limpiar_vars, centrar_ventana
from temas import aplicar_tema

class App_registro_docente:
    def __init__(self, root):
        self.root=aplicar_tema(root)
        self.root.title("REGISTRO DE DOCENTES")
        centrar_ventana(self.root, 1870, 550)
        self.vars={c: tk.StringVar() for c in ["CI", "Nombres", "Ap. Paterno", "Ap. Materno", "Teléfono", "Fecha Ingreso", "Sueldo", "ID Materia"]}
        self.crear_interfaz()
        self.cargar_combo()

    def crear_interfaz(self):
        marco=ttkb.Labelframe(self.root, text="REGISTRO DE DOCENTES", bootstyle="primary")
        marco.pack(padx=20, pady=20, fill="both", expand=True)

        form=ttkb.Frame(marco); form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        campos=list(self.vars.keys())
        for i, c in enumerate(campos):
            ttkb.Label(form, text=f"{c}:", anchor="center").grid(row=i, column=0, padx=6, pady=6, sticky="e")
            if c=="ID Materia":
                self.combo = ttkb.Combobox(form, textvariable=self.vars[c], width=28, state="readonly")
                self.combo.grid(row=i, column=1, padx=6, pady=6, sticky="w")
            else:
                ttkb.Entry(form, textvariable=self.vars[c], bootstyle="dark", justify="center", width=25).grid(
                    row=i, column=1, padx=6, pady=6, sticky="w")

        btns=ttkb.Frame(form); btns.grid(row=8, column=0, columnspan=2, pady=10)
        for i, (txt, sty, cmd) in enumerate([
            ("Agregar", "success", self.agregar),
            ("Actualizar", "warning", self.actualizar),
            ("Eliminar", "danger", self.eliminar),
            ("Limpiar", "light", self.limpiar)
        ]):
            ttkb.Button(btns, text=txt, bootstyle=f"{sty}-outline", width=12, command=cmd).grid(row=0, column=i, padx=5)

        bus=ttkb.Frame(form); bus.grid(row=9, column=0, columnspan=2, pady=10)
        ttkb.Label(bus, text="Buscar por:").pack(side="left", padx=5)
        cols=["CI", "Nombres", "Ap. Paterno", "Ap. Materno", "Teléfono", "Fecha Ingreso", "Sueldo", "ID Materia", "Nombre Materia", "Área"]
        self.col_bus = ttkb.Combobox(bus, state="readonly", width=18, bootstyle="dark", values=cols)
        self.col_bus.pack(side="left", padx=5); self.col_bus.current(0)
        ttkb.Label(bus, text="Valor:").pack(side="left", padx=5)
        self.buscar_var = tk.StringVar()
        ttkb.Entry(bus, textvariable=self.buscar_var, width=25, bootstyle="dark").pack(side="left", padx=5)
        ttkb.Button(bus, text="Buscar", bootstyle="info-outline", command=self.buscar).pack(side="left", padx=5)
        ttkb.Button(bus, text="Mostrar todo", bootstyle="success-outline", command=self.mostrar).pack(side="left", padx=5)

        tabla_frame=ttkb.Frame(marco); tabla_frame.grid(row=0, column=1, rowspan=10, padx=10, pady=10, sticky="nsew")
        cols_tabla=("CI", "Nombres", "Ap. Paterno", "Ap. Materno", "Teléfono", "Ingreso", "Sueldo", "ID Materia", "Área")
        self.tabla=ttkb.Treeview(tabla_frame, columns=cols_tabla, show="headings", bootstyle="dark")

        for c in cols_tabla: self.tabla.heading(c, text=c, anchor="center"); self.tabla.column(c, anchor="center", width=120)

        vsb=ttkb.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=vsb.set); vsb.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<ButtonRelease-1>", self.seleccionar)

    def cargar_combo(self):
        rows=ejecutar_sql("SELECT id_materia, nombre_materia FROM materia ORDER BY id_materia;", fetch=True)
        self.combo["values"]=[f"{r[0]} - {r[1]}" for r in (rows or [])] or ["Sin Materia"]
        if self.combo["values"] and not self.vars["ID Materia"].get():
            self.combo.current(0)

    def mostrar(self):
        filas=ejecutar_sql("""
            SELECT d.ci, d.nombres, d.ap_paterno, d.ap_materno, d.telefono_docente,
                   d.fecha_ingreso, d.sueldo,
                   COALESCE(m.id_materia::text, 'Sin Materia'),
                   COALESCE(m.area, 'Sin Área')
            FROM docente d LEFT JOIN materia m ON d.id_materia=m.id_materia
            ORDER BY d.nombres;""", fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)
        self.cargar_combo()

    def agregar(self):
        v={k: self.vars[k].get().strip() for k in self.vars}
        if not v["CI"] or not v["Nombres"]:
            return messagebox.showwarning("Advertencia", "CI y Nombres son obligatorios.")
        id_mat=None
        if v["ID Materia"] and v["ID Materia"]!="Sin Materia":
            id_mat=v["ID Materia"].split(" - ")[0]
            if not ejecutar_sql("SELECT 1 FROM materia WHERE id_materia=%s;", (id_mat,), fetch=True):
                return messagebox.showerror("Error", f"Materia ID {id_mat} no existe.")
        ejecutar_sql("""INSERT INTO docente (ci, nombres, ap_paterno, ap_materno, telefono_docente, fecha_ingreso, sueldo, id_materia)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", 
            (v["CI"], v["Nombres"], v["Ap. Paterno"], v["Ap. Materno"], v["Teléfono"], v["Fecha Ingreso"], v["Sueldo"], id_mat), commit=True)
        messagebox.showinfo("Éxito", "Docente agregado.")
        self.mostrar(); self.limpiar()

    def actualizar(self):
        ci=self.vars["CI"].get().strip()
        if not ci: return messagebox.showwarning("Advertencia", "Seleccione por CI.")
        v={k: self.vars[k].get().strip() for k in self.vars}
        id_mat=None
        if v["ID Materia"] and v["ID Materia"] != "Sin Materia":
            id_mat=v["ID Materia"].split(" - ")[0]
        ejecutar_sql("""
            UPDATE docente SET nombres=%s, ap_paterno=%s, ap_materno=%s, telefono_docente=%s,
            fecha_ingreso=%s, sueldo=%s, id_materia=%s WHERE ci=%s;
        """, (v["Nombres"], v["Ap. Paterno"], v["Ap. Materno"], v["Teléfono"], v["Fecha Ingreso"], v["Sueldo"], id_mat, ci), commit=True)
        messagebox.showinfo("Éxito", "Docente actualizado.")
        self.mostrar()

    def eliminar(self):
        ci=self.vars["CI"].get().strip()
        if not ci or not messagebox.askyesno("Confirmar", f"¿Eliminar CI {ci}?"): return
        ejecutar_sql("DELETE FROM docente WHERE ci=%s;", (ci,), commit=True)
        messagebox.showinfo("Éxito", "Docente eliminado.")
        self.mostrar(); self.limpiar()

    def seleccionar(self, e):
        sel=self.tabla.selection()
        if not sel: return
        valores=self.tabla.item(sel, "values")
        for i, k in enumerate(self.vars.keys()):
            val=valores[i]
            if k=="ID Materia":
                opt=next((o for o in self.combo["values"] if o.startswith(val)), "")
                self.vars[k].set(opt or "")
            else:
                self.vars[k].set(val)

    def limpiar(self):
        limpiar_vars(self.vars)
        self.cargar_combo()

    def buscar(self):
        texto=self.buscar_var.get().strip()
        col=self.col_bus.get()
        if not texto: return messagebox.showwarning("Búsqueda", "Ingrese texto.")
        map_col={
            "CI": "d.ci::text", "Nombres": "d.nombres", "Ap. Paterno": "d.ap_paterno", "Ap. Materno": "d.ap_materno",
            "Teléfono": "d.telefono_docente", "Fecha Ingreso": "d.fecha_ingreso::text", "Sueldo": "d.sueldo::text",
            "ID Materia": "m.id_materia::text", "Nombre Materia": "m.nombre_materia", "Área": "m.area"}
        filas = ejecutar_sql(f"""
            SELECT d.ci, d.nombres, d.ap_paterno, d.ap_materno, d.telefono_docente,
                   d.fecha_ingreso, d.sueldo, COALESCE(m.id_materia::text, 'Sin'), COALESCE(m.area, 'Sin')
            FROM docente d LEFT JOIN materia m ON d.id_materia=m.id_materia
            WHERE unaccent({map_col.get(col, 'd.nombres')}) ILIKE unaccent(%s)
            ORDER BY d.nombres;
        """, (f"%{texto}%",), fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)
        self.cargar_combo()

if __name__=="__main__":
    root=ttkb.Window(themename="darkly")
    App_registro_docente(root)
    root.mainloop()