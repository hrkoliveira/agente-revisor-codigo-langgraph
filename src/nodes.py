"""
Nos do grafo.

Cada funcao aqui e uma etapa do processo. Todas recebem o estado atual e
devolvem so os campos que mudaram. A ordem natural e:

    validar_entrada -> preparar_contexto -> analisar_codigo -> gerar_relatorio

O primeiro no decide se vale a pena seguir. Se a entrada for invalida, o grafo
corta o fluxo antes de gastar chamada de modelo.
"""

import os
from pathlib import Path

from langchain_anthropic import ChatAnthropic

from src.prompts import INSTRUCAO_SISTEMA, montar_prompt_analise
from src.schemas import ResultadoRevisao
from src.state import EstadoRevisao
from src.tools import (
    EXTENSOES_SUPORTADAS,
    LIMITE_BYTES,
    ler_codigo,
    salvar_relatorio,
)

# Modelo configuravel por variavel de ambiente, com um padrao razoavel.
# Nao passo temperature nem top_p: os modelos atuais da Anthropic nao aceitam
# mais esses parametros e devolvem erro 400 se eles vierem na requisicao.
MODELO = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8")

PASTA_SAIDA = "examples/output"


def validar_entrada(estado: EstadoRevisao) -> dict:
    """Confere se o arquivo existe, tem extensao conhecida e nao esta vazio."""
    caminho = estado.get("caminho_arquivo", "").strip()

    if not caminho:
        return _invalido("Nenhum caminho de arquivo foi informado.")

    arquivo = Path(caminho)
    if not arquivo.is_file():
        return _invalido(f"Arquivo nao encontrado: {caminho}")

    extensao = arquivo.suffix.lower()
    if extensao not in EXTENSOES_SUPORTADAS:
        suportadas = ", ".join(sorted(EXTENSOES_SUPORTADAS))
        return _invalido(
            f"Extensao '{extensao}' nao suportada. Aceito: {suportadas}"
        )

    tamanho = arquivo.stat().st_size
    if tamanho == 0:
        return _invalido("O arquivo esta vazio, nao ha o que revisar.")
    if tamanho > LIMITE_BYTES:
        return _invalido(
            f"Arquivo grande demais ({tamanho} bytes). Limite: {LIMITE_BYTES} bytes."
        )

    return {"valido": True, "linguagem": EXTENSOES_SUPORTADAS[extensao]}


def preparar_contexto(estado: EstadoRevisao) -> dict:
    """Le o codigo do disco usando a ferramenta e guarda no estado."""
    caminho = estado["caminho_arquivo"]
    conteudo = ler_codigo.invoke({"caminho": caminho})
    return {"conteudo": conteudo}


def analisar_codigo(estado: EstadoRevisao) -> dict:
    """Pede a revisao ao modelo e recebe a resposta ja no formato do schema."""
    modelo = ChatAnthropic(model=MODELO)
    revisor = modelo.with_structured_output(ResultadoRevisao)

    prompt_usuario = montar_prompt_analise(
        estado["linguagem"], estado["conteudo"]
    )
    resultado = revisor.invoke(
        [
            ("system", INSTRUCAO_SISTEMA),
            ("human", prompt_usuario),
        ]
    )

    # Guardo os achados como dicionarios para facilitar a serializacao do estado.
    return {
        "achados": [a.model_dump() for a in resultado.achados],
        "resumo": resultado.resumo,
        "nota_geral": resultado.nota_geral,
    }


def gerar_relatorio(estado: EstadoRevisao) -> dict:
    """Monta o relatorio em Markdown e grava com a ferramenta de escrita."""
    relatorio = _montar_markdown(estado)

    nome_base = Path(estado["caminho_arquivo"]).stem
    destino = str(Path(PASTA_SAIDA) / f"revisao_{nome_base}.md")
    caminho_gravado = salvar_relatorio.invoke(
        {"caminho": destino, "conteudo": relatorio}
    )

    return {"relatorio_md": relatorio, "caminho_relatorio": caminho_gravado}


def relatar_erro(estado: EstadoRevisao) -> dict:
    """No de saida quando a entrada foi reprovada na validacao."""
    # Nada a fazer alem de deixar a mensagem de erro visivel no estado final.
    return {}


def _invalido(mensagem: str) -> dict:
    return {"valido": False, "mensagem_erro": mensagem}


def _montar_markdown(estado: EstadoRevisao) -> str:
    achados = estado.get("achados", [])
    linhas = [
        f"# Revisao de codigo: {Path(estado['caminho_arquivo']).name}",
        "",
        f"- Linguagem: {estado.get('linguagem', 'desconhecida')}",
        f"- Nota geral: {estado.get('nota_geral', 'n/d')}/10",
        f"- Problemas encontrados: {len(achados)}",
        "",
        "## Resumo",
        "",
        estado.get("resumo", "Sem resumo."),
        "",
        "## Achados",
        "",
    ]

    if not achados:
        linhas.append("Nenhum problema relevante encontrado. Bom trabalho.")
    else:
        ordem = {"alta": 0, "media": 1, "baixa": 2}
        for achado in sorted(achados, key=lambda a: ordem.get(a["severidade"], 9)):
            linha = achado.get("linha")
            local = f" (linha {linha})" if linha else ""
            linhas.extend(
                [
                    f"### [{achado['severidade'].upper()}] "
                    f"{achado['categoria']}{local}",
                    "",
                    f"{achado['descricao']}",
                    "",
                    f"**Sugestao:** {achado['sugestao']}",
                    "",
                ]
            )

    return "\n".join(linhas)
