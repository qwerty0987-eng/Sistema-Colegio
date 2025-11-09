import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from funciones_compartidas import ejecutar_sql, limpiar_vars, centrar_ventana
from temas import aplicar_tema

class App_registro_padre:
    def __init__(self, root):
        self.root=aplicar_tema(root)
        self.root.title("REGISTRO DE PADRES")
        centrar_ventana(self.root, 1808, 475)
        self.vars={c: tk.StringVar() for c in ["CI", "Nombres", "Ap. Paterno", "Ap. Materno", "Dirección", "Celular", "RUDE Estudiante"]}
        self.crear_interfaz()

    def crear_interfaz(self):
        marco=ttkb.Labelframe(self.root, text="REGISTRO DE PADRES", bootstyle="primary")
        marco.pack(padx=20, pady=20, fill="both", expand=True)
        form=ttkb.Frame(marco); form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        for i, c in enumerate(self.vars):
            ttkb.Label(form, text=f"{c}:", anchor="center").grid(row=i, column=0, padx=6, pady=6, sticky="e")
            ttkb.Entry(form, textvariable=self.vars[c], bootstyle="dark", justify="center", width=30).grid(row=i, column=1, padx=6, pady=6, sticky="w")
        btns=ttkb.Frame(form); btns.grid(row=len(self.vars), column=0, columnspan=2, pady=10)
        for i, (t, s, cmd) in enumerate([("Agregar","success",self.agregar), ("Actualizar","warning",self.actualizar), ("Eliminar","danger",self.eliminar), ("Limpiar","light",self.limpiar)]):
            ttkb.Button(btns, text=t, bootstyle=f"{s}-outline", width=13, command=cmd).grid(row=0, column=i, padx=5)
        bus=ttkb.Frame(form); bus.grid(row=len(self.vars)+1, column=0, columnspan=2, pady=10)
        ttkb.Label(bus, text="Buscar por:").pack(side="left", padx=5)
        self.col=ttkb.Combobox(bus, state="readonly", width=18, bootstyle="dark", values=list(self.vars.keys())); self.col.pack(side="left", padx=5); self.col.current(0)
        ttkb.Label(bus, text="Valor:").pack(side="left", padx=5)
        self.buscar_var=tk.StringVar()
        ttkb.Entry(bus, textvariable=self.buscar_var, width=25, bootstyle="dark").pack(side="left", padx=5)
        ttkb.Button(bus, text="Buscar", bootstyle="info-outline", command=self.buscar).pack(side="left", padx=5)
        ttkb.Button(bus, text="Mostrar todo", bootstyle="success-outline", command=self.mostrar).pack(side="left", padx=5)
        tabla_frame=ttkb.Frame(marco); tabla_frame.grid(row=0, column=1, rowspan=12, padx=10, pady=10, sticky="nsew")
        cols=tuple(self.vars.keys())
        self.tabla=ttkb.Treeview(tabla_frame, columns=cols, show="headings", bootstyle="dark")
        for c in cols: self.tabla.heading(c, text=c, anchor="center"); self.tabla.column(c, anchor="center", width=150)
        vsb=ttkb.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview); self.tabla.configure(yscroll=vsb.set); vsb.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True); self.tabla.bind("<ButtonRelease-1>", self.seleccionar)

    def mostrar(self):
        filas=ejecutar_sql("""SELECT p.ci, p.nombres, p.ap_paterno, p.ap_materno, p.direccion, p.celular, 
                                COALESCE(e.rude::text, 'Sin RUDE') FROM padre p 
                                LEFT JOIN estudiante e ON p.id_padre=e.id_padre ORDER BY p.ci;""", fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)

    def agregar(self):
        v={k: self.vars[k].get().strip() for k in self.vars}
        if not v["CI"] or not v["Nombres"]:
            return messagebox.showwarning("Faltan datos", "CI y Nombres son obligatorios.")

        if ejecutar_sql("SELECT 1 FROM padre WHERE ci=%s;", (v["CI"],), fetch=True):
            return messagebox.showerror("Error", f"El CI {v['CI']} ya existe en la base de datos.")
        try:
            id_padre=ejecutar_sql("""
                INSERT INTO padre (ci, nombres, ap_paterno, ap_materno, direccion, celular)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_padre;
            """, (v["CI"], v["Nombres"], v["Ap. Paterno"], v["Ap. Materno"], v["Dirección"], v["Celular"]), fetch=True, commit=True)[0][0]
            if v["RUDE Estudiante"]:
                est=ejecutar_sql("SELECT 1 FROM estudiante WHERE rude=%s;", (v["RUDE Estudiante"],), fetch=True)
                if est:
                    ejecutar_sql("UPDATE estudiante SET id_padre=%s WHERE rude=%s;", (id_padre, v["RUDE Estudiante"]), commit=True)
                else:
                    messagebox.showwarning("Advertencia", f"RUDE {v['RUDE Estudiante']} no existe. Padre creado sin asignar.")
            messagebox.showinfo("Éxito", f"Padre CI {v['CI']} agregado correctamente.")
            self.mostrar(); self.limpiar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")

    def actualizar(self):
        ci=self.vars["CI"].get().strip()
        if not ci: return messagebox.showwarning("Advertencia", "Indique CI.")
        v={k: self.vars[k].get().strip() for k in self.vars}

        # Verificar que el nuevo CI no exista (si cambió)
        if v["CI"]!=ci:
            if ejecutar_sql("SELECT 1 FROM padre WHERE ci=%s;", (v["CI"],), fetch=True):
                return messagebox.showerror("Error", f"El CI {v['CI']} ya está en uso.")
        try:
            ejecutar_sql("""
                UPDATE padre SET ci=%s, nombres=%s, ap_paterno=%s, ap_materno=%s, direccion=%s, celular=%s WHERE ci=%s;
            """, (v["CI"], v["Nombres"], v["Ap. Paterno"], v["Ap. Materno"], v["Dirección"], v["Celular"], ci), commit=True)
            messagebox.showinfo("Éxito", "Padre actualizado.")
            self.mostrar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
    def eliminar(self):
        ci=self.vars["CI"].get().strip()
        if not ci or not messagebox.askyesno("Confirmar", f"¿Eliminar padre CI {ci}?"): return
        try:
            ejecutar_sql("""
                UPDATE estudiante SET id_padre = NULL 
                WHERE id_padre = (SELECT id_padre FROM padre WHERE ci=%s);
            """, (ci,), commit=True)
            result=ejecutar_sql("DELETE FROM padre WHERE ci=%s RETURNING id_padre;", (ci,), fetch=True, commit=True)
            if not result:
                return messagebox.showerror("Error", "No se encontró el padre.")
            messagebox.showinfo("Éxito", f"Padre CI {ci} eliminado correctamente.")
            self.mostrar()
            self.limpiar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def seleccionar(self, e):
        sel=self.tabla.selection(); 
        if not sel: return
        for i, k in enumerate(self.vars.keys()): self.vars[k].set(self.tabla.item(sel, "values")[i])
        self.vars["RUDE Estudiante"].set("")

    def limpiar(self): limpiar_vars(self.vars); self.buscar_var.set("")

    def buscar(self):
        texto, col=self.buscar_var.get().strip(), self.col.get()
        if not texto: return messagebox.showwarning("Búsqueda", "Ingrese texto.")
        map_col={k: f"p.{k.lower().replace(' ', '_')}::text" if k != "RUDE Estudiante" else "e.rude" for k in self.vars}
        filas=ejecutar_sql(f"SELECT p.ci, p.nombres, p.ap_paterno, p.ap_materno, p.direccion, p.celular, COALESCE(e.rude, 'Sin RUDE') FROM padre p LEFT JOIN estudiante e ON p.id_padre=e.id_padre WHERE unaccent({map_col[col]}) ILIKE unaccent(%s) ORDER BY p.nombres;", (f"%{texto}%",), fetch=True)
        self.tabla.delete(*self.tabla.get_children())
        for f in filas or []: self.tabla.insert("", "end", values=f)

if __name__=="__main__":
    root=ttkb.Window(themename="darkly")
    App_registro_padre(root)
    root.mainloop()