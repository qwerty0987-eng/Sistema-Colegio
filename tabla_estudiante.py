import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from temas import aplicar_tema
from funciones_compartidas import ejecutar_sql, limpiar_vars, centrar_ventana

class App_registro_estudiante:
    def __init__(self, root):
        self.root=aplicar_tema(root)
        self.root.title("REGISTRO DE ESTUDIANTES")
        centrar_ventana(self.root, 1720, 400)
        self.vars={c: tk.StringVar() for c in ["CI", "Nombre", "Ap. Paterno", "Ap. Materno", "Rude", "Grado", "CI Padre"]}
        self.materia_var = tk.StringVar()
        self.crear_interfaz()
        self.cargar_materias()

    def crear_interfaz(self):
        marco=ttkb.Labelframe(self.root, text="REGISTRO DE ESTUDIANTES", bootstyle="primary")
        marco.pack(padx=10, pady=10, fill="both", expand=True)

        form=ttkb.Frame(marco); form.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        campos=list(self.vars.keys())
        for i, c in enumerate(campos):
            r, col=i//2, i%2
            ttkb.Label(form, text=f"{c}:", anchor="center").grid(row=r, column=col*2, padx=4, pady=4, sticky="e")
            ttkb.Entry(form, textvariable=self.vars[c], bootstyle="dark", justify="center", width=22).grid(row=r, column=col*2+1, padx=4, pady=4, sticky="w")

        ttkb.Label(form, text="Seleccionar Materia:", anchor="center").grid(row=4, column=0, padx=4, pady=6, sticky="e")
        self.combo_materia=ttkb.Combobox(form, textvariable=self.materia_var, width=25, state="readonly")
        self.combo_materia.grid(row=4, column=1, padx=4, pady=6, sticky="w")
        ttkb.Label(form, text="Materias Asignadas:", anchor="center").grid(row=4, column=2, padx=4, pady=6, sticky="ne")
        self.lista_materias=tk.Listbox(form, width=30, height=5, exportselection=False)
        self.lista_materias.grid(row=4, column=3, padx=4, pady=6, sticky="w")

        btns=ttkb.Frame(form); btns.grid(row=6, column=0, columnspan=4, pady=8)
        for i, (txt, sty, cmd) in enumerate([
            ("Agregar/Asignar", "success", self.agregar),
            ("Actualizar", "warning", self.actualizar),
            ("Eliminar", "danger", self.eliminar),
            ("Limpiar", "light", self.limpiar)]):
            ttkb.Button(btns, text=txt, bootstyle=f"{sty}-outline", width=14, command=cmd).grid(row=0, column=i, padx=3)

        bus=ttkb.Frame(form); bus.grid(row=7, column=0, columnspan=4, pady=6)
        ttkb.Label(bus, text="Buscar por:").pack(side="left", padx=3)
        cols=["RUDE", "CI", "Nombres", "Ap. Paterno", "Ap. Materno", "Grado", "Materia", "CI Padre"]
        self.col_busqueda=ttkb.Combobox(bus, state="readonly", width=14, bootstyle="dark", values=cols)
        self.col_busqueda.pack(side="left", padx=3); self.col_busqueda.current(0)
        ttkb.Label(bus, text="Valor:").pack(side="left", padx=3)
        self.buscar_var=tk.StringVar()
        ttkb.Entry(bus, textvariable=self.buscar_var, width=20, bootstyle="dark").pack(side="left", padx=3)
        ttkb.Button(bus, text="Buscar", bootstyle="info-outline", width=9, command=self.buscar).pack(side="left", padx=3)
        ttkb.Button(bus, text="Mostrar todo", bootstyle="success-outline", width=11, command=self.mostrar).pack(side="left", padx=3)

        tabla_frame=ttkb.Frame(marco); tabla_frame.grid(row=0, column=1, rowspan=10, padx=6, pady=5, sticky="nsew")
        cols_tabla=("CI", "Nombre", "Ap. Paterno", "Ap. Materno", "Rude", "Grado", "Materias", "CI Padre")
        self.tabla=ttkb.Treeview(tabla_frame, columns=cols_tabla, show="headings", bootstyle="dark")

        for c in cols_tabla: self.tabla.heading(c, text=c, anchor="center"); self.tabla.column(c, anchor="center", width=120)

        vsb=ttkb.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=vsb.set); vsb.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<ButtonRelease-1>", self.seleccionar)

    def cargar_materias(self):
        rows=ejecutar_sql("SELECT id_materia, nombre_materia FROM materia ORDER BY nombre_materia;", fetch=True)
        if rows:
            self.materias_map={f"{r[0]} - {r[1]}": r[0] for r in rows}
            self.combo_materia["values"] = list(self.materias_map.keys())

    def mostrar(self):
        filas=ejecutar_sql("""
            SELECT e.ci, e.nombres, e.ap_paterno, e.ap_materno, e.rude, e.grado,
                   COALESCE(string_agg(m.nombre_materia, ', '), 'Sin Materia'),
                   COALESCE(p.ci::text, 'Sin Padre')
            FROM estudiante e
            LEFT JOIN estudiante_materia em ON e.id_estudiante = em.id_estudiante
            LEFT JOIN materia m ON em.id_materia = m.id_materia
            LEFT JOIN padre p ON e.id_padre = p.id_padre
            GROUP BY e.ci, e.nombres, e.ap_paterno, e.ap_materno, e.rude, e.grado, p.ci
            ORDER BY e.ci ASC;""", fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)

    def agregar(self):
        rude=self.vars["Rude"].get().strip()
        if not rude:
            return messagebox.showwarning("Advertencia", "RUDE es obligatorio.")

        ci=self.vars["CI"].get().strip()
        nombre=self.vars["Nombre"].get().strip()
        ci_padre=self.vars["CI Padre"].get().strip()
        grado=self.vars["Grado"].get().strip()
        materia_sel=self.materia_var.get()
        est=ejecutar_sql("SELECT id_estudiante, id_padre FROM estudiante WHERE rude=%s;", (rude,), fetch=True)
        if not est:
            if not all([ci, nombre, ci_padre, grado]):
                return messagebox.showwarning("Advertencia", "Para nuevo estudiante: complete CI, Nombre, CI Padre y Grado.")
            padre=ejecutar_sql("SELECT id_padre FROM padre WHERE ci=%s;", (ci_padre,), fetch=True)
            if not padre: return messagebox.showerror("Error", f"Padre CI {ci_padre} no existe.")
            id_est=ejecutar_sql("""
                INSERT INTO estudiante (ci, nombres, ap_paterno, ap_materno, rude, grado, id_padre)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id_estudiante;
            """, (ci, nombre, self.vars["Ap. Paterno"].get().strip(), self.vars["Ap. Materno"].get().strip(), rude, grado, padre[0][0]), fetch=True, commit=True)[0][0]
            msg="Estudiante creado"
        else:
            id_est=est[0][0]
            msg="Estudiante encontrado"
        if materia_sel:
            id_m=self.materias_map.get(materia_sel)
            if id_m and not ejecutar_sql("SELECT 1 FROM estudiante_materia WHERE id_estudiante=%s AND id_materia=%s;", (id_est, id_m), fetch=True):
                ejecutar_sql("INSERT INTO estudiante_materia (id_estudiante, id_materia) VALUES (%s,%s);", (id_est, id_m), commit=True)
                msg+=f" → materia {materia_sel.split(' - ')[1]} asignada"
            else:
                msg+=" (materia ya asignada)"

        messagebox.showinfo("Éxito", f"{msg}.", parent=self.root)
        self.mostrar(); self.limpiar()

    def actualizar(self):
        rude=self.vars["Rude"].get().strip()
        if not rude: return messagebox.showwarning("Advertencia", "Seleccione por RUDE.")
        est=ejecutar_sql("SELECT id_estudiante FROM estudiante WHERE rude=%s;", (rude,), fetch=True)
        if not est: return messagebox.showerror("Error", "Estudiante no encontrado.")
        
        vals={k: self.vars[k].get().strip() for k in self.vars}
        if not all([vals["CI"], vals["Nombre"], vals["Grado"], vals["CI Padre"]]):
            return messagebox.showwarning("Advertencia", "Complete CI, Nombre, Grado y CI Padre.")
        
        padre=ejecutar_sql("SELECT id_padre FROM padre WHERE ci=%s;", (vals["CI Padre"],), fetch=True)
        if not padre: return messagebox.showerror("Error", f"Padre CI {vals['CI Padre']} no existe.")
        
        ejecutar_sql("""
            UPDATE estudiante SET ci=%s, nombres=%s, ap_paterno=%s, ap_materno=%s, grado=%s, id_padre=%s
            WHERE id_estudiante=%s;
        """, (vals["CI"], vals["Nombre"], vals["Ap. Paterno"], vals["Ap. Materno"], vals["Grado"], padre[0][0], est[0][0]), commit=True)
        
        mat=self.materia_var.get()
        if mat:
            id_m=self.materias_map[mat]
            ejecutar_sql("DELETE FROM estudiante_materia WHERE id_estudiante=%s;", (est[0][0],), commit=True)
            ejecutar_sql("INSERT INTO estudiante_materia (id_estudiante, id_materia) VALUES (%s,%s);", (est[0][0], id_m), commit=True)
        
        messagebox.showinfo("Éxito", "Estudiante actualizado.")
        self.mostrar(); self.limpiar()

    def eliminar(self):
        rude=self.vars["Rude"].get().strip()
        if not rude or not messagebox.askyesno("Confirmar", f"¿Eliminar RUDE {rude}?"): return
        est=ejecutar_sql("SELECT id_estudiante FROM estudiante WHERE rude=%s;", (rude,), fetch=True)
        if not est: return messagebox.showerror("Error", "No existe.")
        ejecutar_sql("DELETE FROM estudiante_materia WHERE id_estudiante=%s;", (est[0][0],), commit=True)
        ejecutar_sql("DELETE FROM estudiante WHERE id_estudiante=%s;", (est[0][0],), commit=True)
        messagebox.showinfo("Éxito", "Eliminado."); self.mostrar(); self.limpiar()

    def seleccionar(self, e):
        sel=self.tabla.selection()
        if not sel: return
        valores=self.tabla.item(sel, "values")
        
        campos=["CI", "Nombre", "Ap. Paterno", "Ap. Materno", "Rude", "Grado"]
        for i, campo in enumerate(campos):
            self.vars[campo].set(valores[i])
        self.vars["CI Padre"].set(valores[7])
        self.lista_materias.delete(0, tk.END)
        materias=valores[6]
        if materias and materias!="Sin Materia":
            for m in materias.split(", "):
                self.lista_materias.insert(tk.END, m)
        if materias and "," not in materias and materias != "Sin Materia":
            for opt in self.combo_materia["values"]:
                if opt.endswith(materias):
                    self.materia_var.set(opt)
                    break

    def limpiar(self):
        limpiar_vars(self.vars)
        self.materia_var.set("")
        self.lista_materias.delete(0, tk.END)

    def buscar(self):
        texto, col = self.buscar_var.get().strip(), self.col_busqueda.get()
        if not texto: return messagebox.showwarning("Búsqueda", "Ingrese texto.")
        map_col={
            "RUDE": "e.rude", "CI": "e.ci::text", "Nombres": "e.nombres",
            "Ap. Paterno": "e.ap_paterno", "Ap. Materno": "e.ap_materno",
            "Grado": "e.grado", "Materia": "m.nombre_materia", "CI Padre": "p.ci::text"}
        filas=ejecutar_sql(f"""
            SELECT e.ci, e.nombres, e.ap_paterno, e.ap_materno, e.rude, e.grado,
                   COALESCE(string_agg(m.nombre_materia, ', '), 'Sin Materia'),
                   COALESCE(p.ci::text, 'Sin Padre')
            FROM estudiante e
            LEFT JOIN estudiante_materia em ON e.id_estudiante=em.id_estudiante
            LEFT JOIN materia m ON em.id_materia=m.id_materia
            LEFT JOIN padre p ON e.id_padre=p.id_padre
            WHERE unaccent({map_col.get(col, 'e.nombres')}) ILIKE unaccent(%s)
            GROUP BY e.ci, e.nombres, e.ap_paterno, e.ap_materno, e.rude, e.grado, p.ci
            ORDER BY e.nombres;""", (f"%{texto}%",), fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)

if __name__=="__main__":
    root=ttkb.Window(themename="darkly")
    App_registro_estudiante(root)
    root.mainloop()