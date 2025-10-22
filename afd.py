# afd.py
from typing import Set, Dict, Tuple, Any, Optional, List


class AFD:
    """
    Autómata Finito Determinista genérico.
    Estados: any hashable (str recommended)
    Alfabeto: set de símbolos (str)
    delta: dict de (estado, simbolo) -> estado
    q0: estado inicial
    F: conjunto de estados aceptacion (terminales válidos)
    """
    def __init__(
        self,
        states: Set[Any],
        alphabet: Set[str],
        transition: Dict[Tuple[Any, str], Any],
        start_state: Any,
        final_states: Set[Any]
    ):
        self.Q = set(states)
        self.Sigma = set(alphabet)
        self.delta = dict(transition)
        self.q0 = start_state
        self.F = set(final_states)
        # basic consistency checks
        if self.q0 not in self.Q:
            raise ValueError("Estado inicial no pertenece a Q")
        if not self.F.issubset(self.Q):
            raise ValueError("Algunos estados finales no pertenecen a Q")

    def step(self, estado: Any, simbolo: str) -> Optional[Any]:
        """una transición: devuelve el siguiente estado o None si no existe"""
        return self.delta.get((estado, simbolo), None)

    def validar(self, secuencia: List[str]) -> bool:
        """Valida una secuencia completa (lista de símbolos). Devuelve True si termina en F."""
        estado = self.q0
        for simbolo in secuencia:
            if simbolo not in self.Sigma:
                return False
            estado = self.step(estado, simbolo)
            if estado is None:
                return False
        return estado in self.F

    def procesar_eventos(self, eventos: List[str]) -> Tuple[bool, Optional[Any], List[str]]:
        """
        Procesa eventos uno a uno, devuelve (es_valida_final, estado_final, traza_estados)
        útil para depuración.
        """
        estado = self.q0
        traza = [str(estado)]
        for e in eventos:
            estado = self.step(estado, e)
            if estado is None:
                return False, None, traza
            traza.append(str(estado))
        return estado in self.F, estado, traza


def pedido_afd_definicion():
    # Conjunto de estados
    estados = {
        'INICIAL',      # <--- nuevo estado inicial
        'NUEVO',
        'PAGO_OK',
        'PREPARADO',
        'ENVIADO',
        'ENTREGADO',
        'ANULADO',
        'DEVUELTO'
    }

    # Alfabeto de eventos
    alfabeto = {'crear', 'pagar', 'preparar', 'enviar', 'entregar', 'anular', 'devolver'}

    # Función de transición δ: Q × Σ → Q
    transiciones = {
        ('INICIAL', 'crear'): 'NUEVO',         # <--- transición inicial
        ('NUEVO', 'pagar'): 'PAGO_OK',
        ('NUEVO', 'anular'): 'ANULADO',
        ('PAGO_OK', 'preparar'): 'PREPARADO',
        ('PAGO_OK', 'anular'): 'ANULADO',
        ('PREPARADO', 'enviar'): 'ENVIADO',
        ('ENVIADO', 'entregar'): 'ENTREGADO',
        ('ENTREGADO', 'devolver'): 'DEVUELTO',
        ('PREPARADO', 'anular'): 'ANULADO'
    }

    # Estado inicial
    q0 = 'INICIAL'

    # Estados de aceptación (finales)
    F = {'ENTREGADO', 'ANULADO', 'DEVUELTO'}

    return AFD(estados, alfabeto, transiciones, q0, F)
