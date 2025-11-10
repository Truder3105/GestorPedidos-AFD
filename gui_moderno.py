import customtkinter as ctk
from tkinter import messagebox
from inventory import Inventory
from storage import Storage
from afd import pedido_afd_definicion
from logger import info, error
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import uuid
import os


# --- Configuración de tema ---
ctk.set_appearance_mode("dark")  # "light" o "dark"
ctk.set_default_color_theme("blue")


class GestorPedidosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor de Pedidos - AFD Interactivo")
        self.geometry("1100x700")
        self.resizable(False, False)

        # --- Inicializaciones ---
        self.storage = Storage()
        self.inventory = Inventory()
        self.afd = pedido_afd_definicion()

        # --- Layout general ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Panel lateral ---
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(self.sidebar, text="Menú Principal", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, pady=(20, 10), padx=10
        )

        self._boton(self.sidebar, "🏠 Inicio", self.mostrar_inicio, 1)
        self._boton(self.sidebar, "➕ Nuevo Pedido", self.crear_pedido, 2)
        self._boton(self.sidebar, "📦 Inventario", self.mostrar_inventario, 3)
        self._boton(self.sidebar, "📜 Pedidos", self.mostrar_pedidos, 4)
        self._boton(self.sidebar, "⚙️ Eventos", self.mostrar_eventos, 5)
        self._boton(self.sidebar, "📊 Estadísticas", self.mostrar_estadisticas, 6)
        self._boton(self.sidebar, "🧩 Ver AFD", self.mostrar_afd, 7)

        ctk.CTkButton(self.sidebar, text="🚪 Salir", fg_color="red", command=self.destroy).grid(
            row=9, column=0, pady=30, padx=20
        )

        # --- Panel principal ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.mostrar_inicio()

    def _boton(self, parent, texto, comando, fila):
        """Crea un botón lateral estándar"""
        btn = ctk.CTkButton(parent, text=texto, width=180, command=comando)
        btn.grid(row=fila, column=0, pady=10, padx=20)

    def limpiar(self):
        """Limpia el contenido del panel principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # -------------------------------------------------------------------------
    # Pantalla de inicio
    # -------------------------------------------------------------------------
    def mostrar_inicio(self):
        self.limpiar()
        ctk.CTkLabel(
            self.main_frame,
            text="Bienvenido al Gestor de Pedidos\nSistema basado en Autómatas Finitos Deterministas",
            font=ctk.CTkFont(size=22, weight="bold"),
            justify="center",
        ).pack(expand=True)

    # -------------------------------------------------------------------------
    # Crear pedido
    # -------------------------------------------------------------------------
    def crear_pedido(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="Registrar nuevo pedido", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=20
        )

        sku_entry = ctk.CTkEntry(self.main_frame, placeholder_text="SKU del producto")
        sku_entry.pack(pady=5)
        qty_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Cantidad")
        qty_entry.pack(pady=5)

        def registrar():
            sku = sku_entry.get().strip()
            if not sku or not qty_entry.get().isdigit():
                messagebox.showerror("Error", "Datos inválidos.")
                return

            qty = int(qty_entry.get())
            order_id = str(uuid.uuid4())
            self.storage.save_order(order_id, sku, qty, ["crear"], "NUEVO")
            info(f"Pedido creado: {order_id} ({sku}, {qty})")

            messagebox.showinfo("Éxito", f"Pedido {order_id[:8]} creado correctamente.")
            self.mostrar_pedidos()

        ctk.CTkButton(self.main_frame, text="Registrar Pedido", command=registrar).pack(pady=10)

    # -------------------------------------------------------------------------
    # Inventario
    # -------------------------------------------------------------------------
    def mostrar_inventario(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="Inventario actual", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        data = self.inventory.list_all()

        def refrescar():
            self.mostrar_inventario()

        ctk.CTkButton(self.main_frame, text="🔄 Refrescar", command=refrescar).pack(pady=5)

        if not data:
            ctk.CTkLabel(self.main_frame, text="No hay productos en inventario.").pack(pady=20)
            return

        for sku, qty in data.items():
            ctk.CTkLabel(self.main_frame, text=f"{sku} — {qty} unidades").pack(anchor="w", padx=30)

    # -------------------------------------------------------------------------
    # Pedidos
    # -------------------------------------------------------------------------
    def mostrar_pedidos(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="Pedidos registrados", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        entry_buscar = ctk.CTkEntry(self.main_frame, placeholder_text="Buscar por ID o SKU")
        entry_buscar.pack(pady=5)

        pedidos = self.storage.list_orders()

        def refrescar():
            self.mostrar_pedidos()

        def filtrar():
            criterio = entry_buscar.get().strip().lower()
            for widget in frame_pedidos.winfo_children():
                widget.destroy()
            for ped in pedidos:
                if criterio in ped["id"].lower() or criterio in ped["sku"].lower():
                    txt = f"🆔 {ped['id'][:8]} | SKU={ped['sku']} | Cant={ped['qty']} | Estado={ped['state']}"
                    ctk.CTkLabel(frame_pedidos, text=txt, anchor="w").pack(pady=3, padx=20, anchor="w")

        ctk.CTkButton(self.main_frame, text="🔍 Buscar", command=filtrar).pack(pady=5)
        ctk.CTkButton(self.main_frame, text="🔄 Refrescar", command=refrescar).pack(pady=5)

        frame_pedidos = ctk.CTkFrame(self.main_frame)
        frame_pedidos.pack(fill="both", expand=True, pady=10)

        if not pedidos:
            ctk.CTkLabel(frame_pedidos, text="No hay pedidos registrados.").pack(pady=20)
            return

        for ped in pedidos:
            txt = f"🆔 {ped['id'][:8]} | SKU={ped['sku']} | Cant={ped['qty']} | Estado={ped['state']}"
            ctk.CTkLabel(frame_pedidos, text=txt, anchor="w").pack(pady=3, padx=20, anchor="w")

    # -------------------------------------------------------------------------
    # Aplicar eventos
    # -------------------------------------------------------------------------
    def mostrar_eventos(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="Aplicar evento a pedido", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        id_entry = ctk.CTkEntry(self.main_frame, placeholder_text="ID del pedido")
        id_entry.pack(pady=5)

        evento_entry = ctk.CTkComboBox(
            self.main_frame, values=["pagar", "preparar", "enviar", "entregar", "devolver", "anular"]
        )
        evento_entry.pack(pady=5)

        def aplicar():
            order_id = id_entry.get().strip()
            evento = evento_entry.get().strip()

            rec = self.storage.get_order(order_id)
            if not rec:
                messagebox.showerror("Error", "Pedido no encontrado.")
                return

            events = rec["events"][:]
            events.append(evento)
            valido, estado_final, traza = self.afd.procesar_eventos(events, context={"allow_return": True})

            if not valido:
                error(f"Transición inválida en pedido {order_id}. Traza: {traza}")
                messagebox.showerror("Error", f"Evento '{evento}' no válido en estado actual.")
                return

            self.storage.save_order(order_id, rec["sku"], rec["qty"], events, estado_final)
            info(f"Evento '{evento}' aplicado a {order_id}, nuevo estado {estado_final}")
            messagebox.showinfo("OK", f"Pedido actualizado a estado: {estado_final}")
            self.mostrar_pedidos()

        ctk.CTkButton(self.main_frame, text="Aplicar evento", command=aplicar).pack(pady=15)

    # -------------------------------------------------------------------------
    # Estadísticas con gráficos
    # -------------------------------------------------------------------------
    def mostrar_estadisticas(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="📊 Estadísticas de Pedidos", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        pedidos = self.storage.list_orders()
        estados = {}
        for ped in pedidos:
            estado = ped["state"] or "N/A"
            estados[estado] = estados.get(estado, 0) + 1

        if not pedidos:
            ctk.CTkLabel(self.main_frame, text="No hay datos para mostrar.").pack(pady=20)
            return

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(estados.values(), labels=estados.keys(), autopct="%1.1f%%", startangle=140)
        ax.set_title("Distribución de Estados de Pedidos")

        canvas = FigureCanvasTkAgg(fig, master=self.main_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # -------------------------------------------------------------------------
    # Mostrar diagrama del AFD
    # -------------------------------------------------------------------------
    def mostrar_afd(self):
        self.limpiar()
        ctk.CTkLabel(self.main_frame, text="Autómata Finito Determinista", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        afd_path = "afd_pedidos.png"
        if not os.path.exists(afd_path):
            ctk.CTkLabel(self.main_frame, text="⚠️ No se encontró el archivo del AFD.").pack(pady=20)
            return

        img = Image.open(afd_path)
        img = img.resize((800, 500))
        photo = ImageTk.PhotoImage(img)
        label_img = ctk.CTkLabel(self.main_frame, image=photo, text="")
        label_img.image = photo
        label_img.pack(pady=10)


if __name__ == "__main__":
    app = GestorPedidosApp()
    app.mainloop()
