import tkinter as tk
from tkinter import ttk, messagebox
import math
from backend import ejecutar_algoritmo_genetico, AREA_MAXIMA
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# Catálogo inicial
CATALOGO_INICIAL = [
    {"id": 1, "nombre": "Mini nevera", "ancho": 0.5, "largo": 0.5, "ganancia": 40, "stock": 20},
    {"id": 2, "nombre": 'Televisor 32"', "ancho": 0.35, "largo": 0.32, "ganancia": 60, "stock": 6},
    {"id": 3, "nombre": "Lavadora", "ancho": 0.6, "largo": 0.6, "ganancia": 90, "stock": 3},
    {"id": 4, "nombre": "Microondas", "ancho": 0.45, "largo": 0.35, "ganancia": 25, "stock": 8},
    {"id": 5, "nombre": "Aire acondicionado", "ancho": 0.6, "largo": 0.45, "ganancia": 110, "stock": 2},
    {"id": 6, "nombre": "Licuadora", "ancho": 0.2, "largo": 0.2, "ganancia": 8, "stock": 10},
    {"id": 7, "nombre": "Nevera grande", "ancho": 0.8, "largo": 0.75, "ganancia": 220, "stock": 2},
    {"id": 8, "nombre": "Horno eléctrico", "ancho": 0.6, "largo": 0.6, "ganancia": 65, "stock": 3},
    {"id": 9, "nombre": "Aspiradora", "ancho": 0.35, "largo": 0.25, "ganancia": 28, "stock": 6},
    {"id": 10, "nombre": "Plancha", "ancho": 0.25, "largo": 0.15, "ganancia": 10, "stock": 12},
    {"id": 11, "nombre": "Cocina a gas", "ancho": 0.9, "largo": 0.55, "ganancia": 130, "stock": 2},
    {"id": 12, "nombre": "Extractor cocina", "ancho": 0.5, "largo": 0.35, "ganancia": 45, "stock": 4},
]


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimización GA - Área 50 m²")
        self.root.geometry("1400x760")

        self.catalogo = [dict(x) for x in CATALOGO_INICIAL]
        self._crear_ui()

    # -------------------------------------------------------------------------
    def _crear_ui(self):
        left = tk.Frame(self.root)
        left.pack(side="left", fill="y", padx=8, pady=8)

        tk.Label(left, text="Catálogo (seleccione y edite):", font=("Arial", 12, "bold")).pack(anchor="w")

        cols = ("Sel", "ID", "Nombre", "Área (m²)", "Ganancia", "Stock")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c, w in zip(cols, [40, 40, 180, 80, 80, 60]):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center" if c != "Nombre" else "w")
        self.tree.pack(side="left", padx=4, pady=4, fill="y")

        for art in self.catalogo:
            area = art["ancho"] * art["largo"]
            self.tree.insert("", "end", iid=str(art["id"]),
                             values=("✔️", art["id"], art["nombre"], f"{area:.3f}", art["ganancia"], art["stock"]))

        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_edicion)

        edit = tk.Frame(left)
        edit.pack(fill="x", pady=8)
        tk.Label(edit, text="Editar artículo seleccionado:").grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(edit, text="Ganancia:").grid(row=1, column=0)
        self.e_gan = tk.Entry(edit, width=8)
        self.e_gan.grid(row=1, column=1, padx=4)
        tk.Label(edit, text="Stock:").grid(row=1, column=2)
        self.e_stock = tk.Entry(edit, width=6)
        self.e_stock.grid(row=1, column=3, padx=4)

        tk.Button(edit, text="Aplicar", command=self.aplicar_edicion).grid(row=2, column=0, padx=4, pady=8, sticky="ew")
        tk.Button(edit, text="Marcar/Demarcar", command=self.marcar_fila).grid(row=2, column=1, padx=4, pady=8, sticky="ew")
        tk.Button(edit, text="Añadir artículo", command=self.abrir_agregar).grid(row=2, column=2, padx=4, pady=8, sticky="ew")
        tk.Button(edit, text="Eliminar", command=self.eliminar_seleccion).grid(row=2, column=3, padx=4, pady=8, sticky="ew")

        # --------- PANEL DERECHO ----------
        right = tk.Frame(self.root)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        params = tk.LabelFrame(right, text="Parámetros GA", padx=8, pady=8)
        params.pack(fill="x", pady=6)

        tk.Label(params, text="Población:").grid(row=0, column=0, sticky="e")
        self.v_pob = tk.Entry(params, width=8)
        self.v_pob.insert(0, "60")
        self.v_pob.grid(row=0, column=1, padx=6)
        tk.Label(params, text="Generaciones:").grid(row=0, column=2, sticky="e")
        self.v_gen = tk.Entry(params, width=8)
        self.v_gen.insert(0, "40")
        self.v_gen.grid(row=0, column=3, padx=6)

        tk.Label(params, text="Pc (cruce):").grid(row=1, column=0, sticky="e")
        self.v_pc = tk.Entry(params, width=8)
        self.v_pc.insert(0, "0.8")
        self.v_pc.grid(row=1, column=1, padx=6)
        tk.Label(params, text="Pm (mut):").grid(row=1, column=2, sticky="e")
        self.v_pm = tk.Entry(params, width=8)
        self.v_pm.insert(0, "0.1")
        self.v_pm.grid(row=1, column=3, padx=6)

        tk.Label(params, text="Selección:").grid(row=2, column=0, sticky="e")
        self.sel_var = tk.StringVar(value="torneo")
        ttk.Combobox(params, textvariable=self.sel_var, values=["torneo", "ruleta"], width=10).grid(row=2, column=1, padx=6)
        self.var_elit = tk.BooleanVar(value=True)
        tk.Checkbutton(params, text="Elitismo", variable=self.var_elit).grid(row=2, column=2, columnspan=2)

        tk.Button(params, text="Ejecutar GA", bg="#4CAF50", fg="white", command=self.ejecutar_ga).grid(
            row=3, column=0, columnspan=4, pady=8
        )

        vis_frame = tk.Frame(right)
        vis_frame.pack(fill="both", expand=True)

        canvas_frame = tk.LabelFrame(vis_frame, text="Distribución 2D", padx=4, pady=4)
        canvas_frame.pack(side="left", fill="both", expand=True, pady=6)

        self.canvas_size = 640
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack(side="left", padx=6, pady=6, expand=True, fill="both")

        self.frame_grafica = tk.LabelFrame(vis_frame, text="Convergencia del Fitness", padx=8, pady=8)
        self.frame_grafica.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        side_info = tk.Frame(canvas_frame)
        side_info.pack(side="left", fill="y", padx=6)
        self.lbl_area = tk.Label(side_info, text="Área ocupada: 0.0% (0.00 / 50.00 m²)")
        self.lbl_area.pack(pady=6)
        self.canvas_bar = tk.Canvas(side_info, width=200, height=20, bg="#eee")
        self.canvas_bar.pack(pady=6)
        self.tree_res = ttk.Treeview(side_info, columns=("cant", "area", "gan", "total"), show="headings", height=12)
        for c, w in zip(["cant", "area", "gan", "total"], [50, 80, 80, 80]):
            self.tree_res.heading(c, text=c.capitalize())
            self.tree_res.column(c, width=w, anchor="center")
        self.tree_res.pack(pady=6)

    # -------------------------------------------------------------------------
    # === Métodos de edición y manejo del catálogo ===
    def cargar_datos_edicion(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.e_gan.delete(0, tk.END)
        self.e_stock.delete(0, tk.END)
        self.e_gan.insert(0, vals[4])
        self.e_stock.insert(0, vals[5])

    def aplicar_edicion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un artículo para editar.")
            return
        try:
            gan = float(self.e_gan.get())
            stock = int(self.e_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return

        iid = sel[0]
        vals = list(self.tree.item(iid, "values"))
        vals[4] = gan
        vals[5] = stock
        self.tree.item(iid, values=vals)
        for art in self.catalogo:
            if art["id"] == int(vals[1]):
                art["ganancia"] = gan
                art["stock"] = stock
                break
        messagebox.showinfo("Éxito", "Artículo actualizado correctamente.")

    def marcar_fila(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una fila.")
            return
        iid = sel[0]
        vals = list(self.tree.item(iid, "values"))
        vals[0] = "✔️" if vals[0] != "✔️" else ""
        self.tree.item(iid, values=vals)

    def abrir_agregar(self):
        win = tk.Toplevel(self.root)
        win.title("Agregar nuevo artículo")
        labels = ["Nombre", "Ancho (m)", "Largo (m)", "Ganancia", "Stock"]
        entries = []
        for i, lab in enumerate(labels):
            tk.Label(win, text=lab + ":").grid(row=i, column=0, padx=4, pady=4)
            e = tk.Entry(win)
            e.grid(row=i, column=1, padx=4, pady=4)
            entries.append(e)

        def agregar():
            try:
                nombre = entries[0].get()
                ancho = float(entries[1].get())
                largo = float(entries[2].get())
                gan = float(entries[3].get())
                stock = int(entries[4].get())
            except ValueError:
                messagebox.showerror("Error", "Verifique los valores ingresados.")
                return
            nuevo_id = max(a["id"] for a in self.catalogo) + 1
            self.catalogo.append({"id": nuevo_id, "nombre": nombre, "ancho": ancho, "largo": largo,
                                  "ganancia": gan, "stock": stock})
            area = ancho * largo
            self.tree.insert("", "end", iid=str(nuevo_id),
                             values=("✔️", nuevo_id, nombre, f"{area:.3f}", gan, stock))
            win.destroy()

        tk.Button(win, text="Agregar", command=agregar, bg="#4CAF50", fg="white").grid(row=len(labels), column=0, columnspan=2, pady=6)

    def eliminar_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una fila para eliminar.")
            return
        iid = sel[0]
        id_art = int(self.tree.item(iid, "values")[1])
        self.tree.delete(iid)
        self.catalogo = [a for a in self.catalogo if a["id"] != id_art]
        messagebox.showinfo("Eliminado", "Artículo eliminado del catálogo.")

    # -------------------------------------------------------------------------
    # === Ejecución del algoritmo y visualización ===
    def mostrar_grafica_fitness(self, historial):
        """Muestra la gráfica de fitness en una ventana emergente."""
        if not historial:
            messagebox.showinfo("Sin datos", "No hay historial disponible para graficar.")
            return

        generaciones = list(range(1, len(historial) + 1))
        fitness = historial

        # Crear la figura independiente
        plt.figure(figsize=(8, 5))
        plt.plot(generaciones, fitness, marker="o", color="blue", label="Mejor fitness")
        plt.title("Evolución del Mejor Fitness", fontsize=12, fontweight="bold")
        plt.xlabel("Generación", fontsize=10)
        plt.ylabel("Fitness (Ganancia)", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        # Mostrar en ventana emergente
        plt.show()

    def ejecutar_ga(self):
        catalogo_backend = self.construir_catalogo_para_backend()
        if not catalogo_backend:
            messagebox.showwarning("Aviso", "Marca al menos un artículo para incluir.")
            return
        try:
            params = {
                "catalogo": catalogo_backend,
                "tam_poblacion": int(self.v_pob.get()),
                "generaciones": int(self.v_gen.get()),
                "pc": float(self.v_pc.get()),
                "pm": float(self.v_pm.get()),
                "seleccion": self.sel_var.get(),
                "elitismo": bool(self.var_elit.get()),
                "torneo_k": 3,
            }
        except Exception as e:
            messagebox.showerror("Error", f"Parámetros inválidos: {e}")
            return

        resultado = ejecutar_algoritmo_genetico(params)
        placements = resultado.get("placements", [])
        detalle = resultado.get("detalle", [])
        mejor_area = resultado.get("mejor_area", 0.0)
        mejor_gan = resultado.get("mejor_ganancia", 0.0)
        historial = resultado.get("historial", [])

        self.pintar_distribucion(placements)
        self.mostrar_grafica_fitness(historial)

        self.tree_res.delete(*self.tree_res.get_children())
        total_gan, total_area = 0.0, 0.0
        for d in detalle:
            if d.get("cantidad", 0) > 0:
                self.tree_res.insert("", "end", values=(d["cantidad"], f"{d['area_unit']:.3f}", d["ganancia_unit"], d["total"]))
            total_gan += d["total"]
            total_area += d["cantidad"] * d["area_unit"]

        porcentaje = (total_area / AREA_MAXIMA) * 100 if AREA_MAXIMA > 0 else 0
        porcentaje = min(100.0, porcentaje)
        self.lbl_area.config(text=f"Área ocupada: {porcentaje:.1f}% ({total_area:.2f} / {AREA_MAXIMA:.2f} m²)")
        self.canvas_bar.delete("all")
        ancho = int(min(1.0, total_area / AREA_MAXIMA) * 180)
        self.canvas_bar.create_rectangle(0, 0, ancho, 20, fill="steelblue")

        messagebox.showinfo("Resultado", f"Ganancia total: {mejor_gan:.2f} | Área total: {mejor_area:.2f} m²")

    # -------------------------------------------------------------------------
    def construir_catalogo_para_backend(self):
        catalogo_final = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            if vals[0] != "✔️":
                continue
            id_int = int(vals[1])
            nombre = vals[2]
            area = float(vals[3])
            gan = float(vals[4])
            stock = int(vals[5])
            match = next((a for a in self.catalogo if a.get("id") == id_int), None)
            ancho = match.get("ancho", math.sqrt(area))
            largo = match.get("largo", area / ancho if ancho else math.sqrt(area))
            catalogo_final.append({"nombre": nombre, "ancho": ancho, "largo": largo, "ganancia": gan, "stock": stock})
        return catalogo_final

    # -------------------------------------------------------------------------
    def pintar_distribucion(self, placements):
        import hashlib
        self.canvas.delete("all")
        lado_plano_m = math.sqrt(AREA_MAXIMA)
        margin_px = 20
        draw_size = self.canvas_size - 2 * margin_px
        scale = draw_size / lado_plano_m

        for p in placements:
            x, y = p.get("x", 0), p.get("y", 0)
            ancho, largo = p.get("ancho", 0), p.get("largo", 0)
            x_px = margin_px + x * scale
            y_px = margin_px + y * scale
            w_px = ancho * scale
            h_px = largo * scale

            h = int(hashlib.md5(p["nombre"].encode()).hexdigest(), 16)
            color = f"#{(100 + h % 130):02x}{(100 + (h >> 8) % 130):02x}{(100 + (h >> 16) % 130):02x}"
            if not p.get("incluido", True):
                color = "#E6B0AA"
            self.canvas.create_rectangle(x_px, y_px, x_px + w_px, y_px + h_px, fill=color, outline="black", width=1.2)
            self.canvas.create_text(x_px + w_px/2, y_px + h_px/2, text=p["nombre"], font=("Arial", 8, "bold"), fill="black")

        self.canvas.create_rectangle(margin_px, margin_px, margin_px + draw_size, margin_px + draw_size,
                                     outline="red", width=3, dash=(5, 3))
        self.canvas.create_text(margin_px + draw_size/2, margin_px - 10, text="Límite de 50 m²", fill="red", font=("Arial", 10, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

