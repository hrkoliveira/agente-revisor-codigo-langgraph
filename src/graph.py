"""
Montagem do grafo com LangGraph.

Aqui e onde as etapas viram um fluxo de verdade. Uso um StateGraph com uma
aresta condicional logo depois da validacao: se a entrada for reprovada, o grafo
desvia para o no de erro e encerra sem chamar o modelo. Se passar, segue o
caminho normal ate gravar o relatorio.

Ligo tambem um checkpointer (MemorySaver). Ele guarda o estado por thread, entao
o agente consegue lembrar de execucoes anteriores dentro da mesma sessao. E o
que da o comportamento de memoria alem do estado de uma unica rodada.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.nodes import (
    analisar_codigo,
    gerar_relatorio,
    preparar_contexto,
    relatar_erro,
    validar_entrada,
)
from src.state import EstadoRevisao


def _rota_apos_validar(estado: EstadoRevisao) -> str:
    """Decide o proximo passo com base no resultado da validacao."""
    return "seguir" if estado.get("valido") else "erro"


def construir_grafo():
    """Monta e compila o grafo do agente."""
    grafo = StateGraph(EstadoRevisao)

    grafo.add_node("validar_entrada", validar_entrada)
    grafo.add_node("preparar_contexto", preparar_contexto)
    grafo.add_node("analisar_codigo", analisar_codigo)
    grafo.add_node("gerar_relatorio", gerar_relatorio)
    grafo.add_node("relatar_erro", relatar_erro)

    grafo.add_edge(START, "validar_entrada")
    grafo.add_conditional_edges(
        "validar_entrada",
        _rota_apos_validar,
        {"seguir": "preparar_contexto", "erro": "relatar_erro"},
    )
    grafo.add_edge("preparar_contexto", "analisar_codigo")
    grafo.add_edge("analisar_codigo", "gerar_relatorio")
    grafo.add_edge("gerar_relatorio", END)
    grafo.add_edge("relatar_erro", END)

    return grafo.compile(checkpointer=MemorySaver())
