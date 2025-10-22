# gui_app.py
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from afd import pedido_afd_definicion
from inventory import Inventory
from storage import Storage
import uuid
import os

# Inicialización de módulos existentes
afd = pedido_afd_definicion()
inv = Inventory(persistence_db="inventory.db")
storage = Storage("data.db")


class PedidoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Pedidos - AFD")
        self.root.geometry("1100x600")
        self.root.resizable(False, False)

        self._crear_widgets()

    def _crear_widgets(self):
        # Título principal
        tk.Label(
            self.root,
            text="Gestión de Pedidos en PyME mediante Autómata Finito Determinista (AFD)",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # --- Panel izquierdo (funcionalidad principal) ---
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        # Frame Inventario
        frm_inv = tk.LabelFrame(left_frame, text="Inventario", padx=10, pady=10)
        frm_inv.pack(fill="x", padx=5, pady=5)
        tk.Button(frm_inv, text="Cargar Inventario Demo", command=self.seed_demo).pack(side="left", padx=5)
        tk.Button(frm_inv, text="Ver Inventario", command=self.ver_inventario).pack(side="left", padx=5)

        # Barra de progreso de stock visual
        self.stock_bars = ttk.Treeview(frm_inv, columns=("sku", "qty"), show="headings", height=3)
        self.stock_bars.heading("sku", text="SKU")
        self.stock_bars.heading("qty", text="Cantidad")
        self.stock_bars.pack(fill="x", pady=5)
        self.actualizar_stock()

        # Frame Crear Pedido
        frm_pedido = tk.LabelFrame(left_frame, text="Crear Pedido", padx=10, pady=10)
        frm_pedido.pack(fill="x", padx=5, pady=5)
        tk.Label(frm_pedido, text="SKU:").pack(side="left")
        self.sku_entry = tk.Entry(frm_pedido, width=10)
        self.sku_entry.pack(side="left", padx=5)
        tk.Label(frm_pedido, text="Cantidad:").pack(side="left")
        self.qty_entry = tk.Entry(frm_pedido, width=5)
        self.qty_entry.pack(side="left", padx=5)
        tk.Button(frm_pedido, text="Crear Pedido", command=self.crear_pedido).pack(side="left", padx=10)

        # Frame Aplicar Evento
        frm_evento = tk.LabelFrame(left_frame, text="Aplicar Evento", padx=10, pady=10)
        frm_evento.pack(fill="x", padx=5, pady=5)
        tk.Label(frm_evento, text="ID Pedido:").pack(side="left")
        self.id_entry = tk.Entry(frm_evento, width=40)
        self.id_entry.pack(side="left", padx=5)
        tk.Label(frm_evento, text="Evento:").pack(side="left")
        self.evento_combo = ttk.Combobox(frm_evento, values=list(afd.Sigma), width=12)
        self.evento_combo.pack(side="left", padx=5)
        tk.Button(frm_evento, text="Aplicar Evento", command=self.aplicar_evento).pack(side="left", padx=10)

        # Frame Listado de pedidos
        frm_lista = tk.LabelFrame(left_frame, text="Pedidos Registrados", padx=10, pady=10)
        frm_lista.pack(fill="both", expand=True, padx=5, pady=10)
        self.tree = ttk.Treeview(frm_lista, columns=("sku", "qty", "state", "events"), show="headings")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("qty", text="Cant.")
        self.tree.heading("state", text="Estado")
        self.tree.heading("events", text="Eventos")
        self.tree.pack(fill="both", expand=True)
        tk.Button(frm_lista, text="Actualizar Lista", command=self.actualizar_lista).pack(pady=5)
        self.actualizar_lista()

        # --- Panel derecho (imagen del autómata) ---
        right_frame = tk.Frame(self.root, width=400, padx=10, pady=10)
        right_frame.pack(side="right", fill="y")
        tk.Label(right_frame, text="Diagrama del AFD", font=("Segoe UI", 12, "bold")).pack(pady=5)

        img_path = "afd_pedidos.png"
        if os.path.exists(img_path):
            try:
                self.afd_img = PhotoImage(file=img_path)
                tk.Label(right_frame, image=self.afd_img).pack()
            except Exception as e:
                tk.Label(right_frame, text=f"No se pudo cargar la imagen: {e}", fg="red").pack()
        else:
            tk.Label(right_frame, text="(No se encontró afd_pedidos.png)", fg="gray").pack()

    # --- Funcionalidades ---
    def seed_demo(self):
        inv.add_product("SKU-001", 5)
        inv.add_product("SKU-002", 2)
        inv.add_product("SKU-003", 10)
        self.actualizar_stock()
        messagebox.showinfo("Inventario", "Inventario demo cargado correctamente.")

    def ver_inventario(self):
        stock = inv.list_all()
        if not stock:
            messagebox.showinfo("Inventario", "No hay productos.")
            return
        texto = "\n".join([f"{k}: {v}" for k, v in stock.items()])
        messagebox.showinfo("Inventario", texto)

    def actualizar_stock(self):
        for row in self.stock_bars.get_children():
            self.stock_bars.delete(row)
        for sku, qty in inv.list_all().items():
            self.stock_bars.insert("", "end", values=(sku, qty))

    def crear_pedido(self):
        sku = self.sku_entry.get().strip()
        qty = self.qty_entry.get().strip()
        if not sku or not qty.isdigit():
            messagebox.showerror("Error", "Ingresa SKU y cantidad válida.")
            return
        qty = int(qty)
        order_id = str(uuid.uuid4())
        events = ['crear']
        _, estado_final, _ = afd.procesar_eventos(events)
        storage.save_order(order_id, sku, qty, events, estado_final)
        messagebox.showinfo("Pedido Creado", f"Pedido creado con ID:\n{order_id}")
        self.actualizar_lista()

    def aplicar_evento(self):
        order_id = self.id_entry.get().strip()
        evento = self.evento_combo.get().strip()
        if not order_id or not evento:
            messagebox.showerror("Error", "Debes ingresar un ID y evento.")
            return
        rec = storage.get_order(order_id)
        if not rec:
            messagebox.showerror("Error", "Pedido no encontrado.")
            return
        events = rec["events"]
        sku = rec["sku"]
        qty = rec["qty"]
        if evento == "preparar":
            ok = inv.remove_stock(sku, qty)
            if not ok:
                messagebox.showerror("Error", f"Stock insuficiente para {sku}.")
                return
        events.append(evento)
        valido, estado_final, traza = afd.procesar_eventos(events)
        if estado_final is None:
            messagebox.showerror("Error", "Transición inválida según el AFD.")
            return
        storage.save_order(order_id, sku, qty, events, estado_final)
        self.actualizar_lista()
        self.actualizar_stock()
        messagebox.showinfo("Evento Aplicado", f"Evento '{evento}' aplicado correctamente.\nNuevo estado: {estado_final}")

    def actualizar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in storage.list_orders():
            tag = "normal"
            if r["state"] in {"ENTREGADO", "ANULADO", "DEVUELTO"}:
                tag = "final"
            self.tree.insert("", "end", values=(r["sku"], r["qty"], r["state"], ",".join(r["events"])), tags=(tag,))
        # Colorear estados finales
        self.tree.tag_configure("final", background="#d1ffd1")  # verde claro


if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoGUI(root)
    root.mainloop()
