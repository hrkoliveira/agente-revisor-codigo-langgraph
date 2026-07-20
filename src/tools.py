"""
Ferramentas do agente.

Sao as acoes concretas que o agente executa no mundo real: ler um arquivo de
codigo do disco e gravar o relatorio de revisao. As duas mexem no sistema de
arquivos de verdade, nao e simulacao. Decorei as funcoes com @tool para deixar
explicito que sao ferramentas no vocabulario do LangChain.
"""

from pathlib import Path

from langchain_core.tools import tool

# Extensoes que a gente sabe revisar, com o nome amigavel da linguagem.
EXTENSOES_SUPORTADAS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".sql": "SQL",
    ".go": "Go",
}

# Limite de tamanho para nao mandar um arquivo gigante para o modelo por engano.
LIMITE_BYTES = 100_000


@tool
def ler_codigo(caminho: str) -> str:
    """Le o conteudo de um arquivo de codigo do disco e devolve como texto."""
    return Path(caminho).read_text(encoding="utf-8")


@tool
def salvar_relatorio(caminho: str, conteudo: str) -> str:
    """Grava o relatorio de revisao em um arquivo Markdown e devolve o caminho."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")
    return str(destino)
