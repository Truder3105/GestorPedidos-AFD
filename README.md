#  Gestión de Pedidos en una PyME mediante Autómatas Finitos Deterministas (AFD)

##  Descripción
Este prototipo modela el ciclo de vida de un pedido en una PyME utilizando un **Autómata Finito Determinista (AFD)**.  
Permite validar secuencias de eventos y controlar el inventario de forma automática para reducir errores operativos.

##  Estructura del proyecto
- `afd.py`: definición del AFD y sus transiciones
- `inventory.py`: módulo de inventario en memoria (persistente en SQLite)
- `storage.py`: almacenamiento de pedidos
- `app.py`: interfaz CLI
- `utils.py`: utilidades y generación de diagrama Graphviz
- `diagram.py`: script para generar el diagrama del AFD
- `afd_pedidos.png`: imagen generada del autómata
- `tests/`: pruebas unitarias

##  Instalación
1. Crear entorno virtual (opcional):
   ```bash
   python -m venv venv
   venv\Scripts\activate

2. Instalar dependencias:

pip install -r requirements.txt


(Windows) Instalar Graphviz:
https://graphviz.org/download/

Uso

1. Cargar inventario demo:

python app.py seed


2. Crear pedido:

python app.py crear --sku SKU-001 --qty 1


3. Aplicar eventos (usar el ID devuelto):

python app.py evento --id <ID> --evento pagar
python app.py evento --id <ID> --evento preparar
python app.py evento --id <ID> --evento enviar
python app.py evento --id <ID> --evento entregar


4. Listar pedidos:

python app.py listar

Diagrama AFD

El autómata generado se encuentra en afd_pedidos.png.

Autores

Julián Esteban Ballesteros Ortiz
David Santiago Castillo Molano
Juan Diego Walteros Cortés

Proyecto — Lenguajes y Autómatas
Universidad de Cundinamarca, 2025