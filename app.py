# app.py
import uuid
from afd import pedido_afd_definicion
from inventory import Inventory
from storage import Storage
from typing import List
import argparse
import sys

# inicializaciones (ajustables)
DB_PATH = "data.db"
INVENTORY_DB = "inventory.db"

afd = pedido_afd_definicion()
inv = Inventory(persistence_db=INVENTORY_DB)
storage = Storage(DB_PATH)


def crear_pedido(sku: str, qty: int) -> str:
    order_id = str(uuid.uuid4())
    events: List[str] = ['crear']  # siempre empieza con crear
    state_ok, estado_final, _ = afd.procesar_eventos(events)
    storage.save_order(order_id, sku, qty, events, estado_final if estado_final else "N/A")
    return order_id


def aplicar_evento(order_id: str, evento: str) -> (bool, str):
    rec = storage.get_order(order_id)
    if not rec:
        return False, "Pedido no encontrado"

    events: List[str] = rec['events']
    sku = rec['sku']
    qty = rec['qty']

    # Antes de aplicar 'pagar' o 'preparar' o 'enviar', validar inventario cuando corresponda
    # Aquí consideramos que al preparar se reserva/elimina stock
    # Política: al evento 'preparar' intentamos remover stock
    if evento == 'preparar':
        ok = inv.remove_stock(sku, qty)
        if not ok:
            return False, f"Stock insuficiente para SKU {sku} (qty {qty})"

    events.append(evento)
    valido_final, estado_final, traza = afd.procesar_eventos(events)
    # si la secuencia quedó inválida: revertir actions asociadas (ej: devolver stock si fail)
    if estado_final is None:
        # si falló por falta de transición, revertir si habíamos removido stock
        if evento == 'preparar':
            inv.add_product(sku, qty)  # devolver
        storage.save_order(order_id, sku, qty, events, "INVALIDO")
        return False, f"Transición inválida según AFD. Trazas: {traza}"
    storage.save_order(order_id, sku, qty, events, estado_final)
    return True, f"Evento aplicado. Estado actual: {estado_final}. Trazas: {traza}"


def ver_pedidos():
    rows = storage.list_orders()
    for r in rows:
        print(f"{r['id']} | sku={r['sku']} qty={r['qty']} state={r['state']} events={r['events']} created={r['created_at']}")


def ver_stock():
    all_ = inv.list_all()
    if not all_:
        print("Inventario vacío")
    for sku, qty in all_.items():
        print(f"{sku}: {qty}")


def seed_demo():
    # agregar productos demo
    inv.add_product("SKU-001", 5)
    inv.add_product("SKU-002", 2)
    inv.add_product("SKU-003", 10)
    print("Inventario demo cargado.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="gestor_pedidos")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("seed", help="Cargar inventario demo")
    p_create = sub.add_parser("crear", help="Crear pedido")
    p_create.add_argument("--sku", required=True)
    p_create.add_argument("--qty", type=int, required=True)

    p_event = sub.add_parser("evento", help="Aplicar evento a pedido")
    p_event.add_argument("--id", required=True)
    p_event.add_argument("--evento", required=True, choices=list(afd.Sigma))

    sub.add_parser("listar", help="Listar pedidos")
    sub.add_parser("stock", help="Ver inventario")

    args = parser.parse_args(argv)
    if args.cmd == "seed":
        seed_demo()
    elif args.cmd == "crear":
        oid = crear_pedido(args.sku, args.qty)
        print(f"Pedido creado: {oid}")
    elif args.cmd == "evento":
        ok, msg = aplicar_evento(args.id, args.evento)
        print(msg)
    elif args.cmd == "listar":
        ver_pedidos()
    elif args.cmd == "stock":
        ver_stock()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
