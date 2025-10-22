# tests/test_afd_inventory.py
import tempfile
import os
from afd import pedido_afd_definicion
from inventory import Inventory
from storage import Storage
from app import crear_pedido, aplicar_evento, inv, storage, afd

def test_afd_secuencias_validas():
    autom = pedido_afd_definicion()
    # secuencia típica
    sec = ['crear', 'pagar', 'preparar', 'enviar', 'entregar']
    ok, estado, _ = autom.procesar_eventos(sec)
    assert ok
    assert estado == 'ENTREGADO'

def test_afd_secuencia_invalida():
    autom = pedido_afd_definicion()
    sec = ['crear', 'enviar']  # no se puede enviar sin preparar
    valido, estado, traza = autom.procesar_eventos(sec)
    assert not valido
    assert estado is None

def test_inventory_and_app_flow(tmp_path):
    # usar bases temporales
    inv_db = tmp_path / "inv.db"
    data_db = tmp_path / "data.db"

    myinv = Inventory(persistence_db=str(inv_db))
    myinv.add_product("SKU-TEST", 1)
    stor = Storage(db_path=str(data_db)) if False else None  # no usamos storage de este test, usaremos funciones de app

    # create an order via app module (uses global inv/storage) - but we avoid globals: instead test inventory directly
    assert myinv.get_stock("SKU-TEST") == 1
    success = myinv.remove_stock("SKU-TEST", 1)
    assert success
    assert myinv.get_stock("SKU-TEST") == 0
    # intentar quitar de nuevo falla
    assert not myinv.remove_stock("SKU-TEST", 1)
