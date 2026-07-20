"""
Estado compartilhado do grafo.

Esse dicionario e a memoria de trabalho do agente durante uma execucao. Cada no
do grafo le e escreve campos aqui, entao a informacao vai sendo acumulada de uma
etapa para a outra ate a geracao do relatorio final.
"""

from typing import List, Optional, TypedDict


class EstadoRevisao(TypedDict, total=False):
    """Campos que trafegam entre os nos do grafo."""

    # Entrada
    caminho_arquivo: str

    # Preenchido durante a preparacao do contexto
    conteudo: Optional[str]
    linguagem: Optional[str]

    # Preenchido pela analise do modelo
    achados: List[dict]
    resumo: Optional[str]
    nota_geral: Optional[int]

    # Saida
    relatorio_md: Optional[str]
    caminho_relatorio: Optional[str]

    # Controle de fluxo e validacao
    valido: bool
    mensagem_erro: Optional[str]
