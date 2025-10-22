# utils.py
from typing import List
import graphviz


def generar_diagrama_afd(transiciones: dict, filename: str = "afd_diagrama"):
    """
    Genera diagram.dot y archivo PNG/SVG con Graphviz si está instalado.
    transiciones: dict (estado_actual, simbolo) -> estado_siguiente
    """
    dot = graphviz.Digraph(format='png')
    estados = set()
    for (source, sym), dest in transiciones.items():
        estados.add(source)
        estados.add(dest)
        dot.edge(source, dest, label=sym)
    for s in estados:
        dot.node(s)
    dot.render(filename, cleanup=True)
    return filename + ".png"
