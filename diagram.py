from afd import pedido_afd_definicion
from utils import generar_diagrama_afd

# Crear el AFD definido en afd.py
afd = pedido_afd_definicion()

# Generar y guardar el diagrama como archivo PNG
path = generar_diagrama_afd(afd.delta, filename="afd_pedidos")
print(f"✅ Diagrama generado: {path}")
