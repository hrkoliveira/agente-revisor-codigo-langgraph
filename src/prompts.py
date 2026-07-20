"""
Prompts usados pelo agente.

Deixei os prompts centralizados aqui para ficar facil de ajustar e para bater
com o que esta registrado em docs/prompts.md.
"""

INSTRUCAO_SISTEMA = (
    "Voce e um revisor de codigo experiente. Sua tarefa e analisar o codigo "
    "recebido e apontar problemas de forma objetiva e util para quem escreveu.\n"
    "Procure por: bugs, riscos de seguranca, problemas de performance, codigo "
    "dificil de ler, nomes ruins, falta de tratamento de erro e desvios de boas "
    "praticas da linguagem.\n"
    "Seja direto. Nao invente problema onde nao existe. Se o codigo estiver bom, "
    "devolva a lista de achados vazia e uma nota alta.\n"
    "Para cada problema, informe a severidade, a categoria, a linha aproximada "
    "quando der, a descricao e uma sugestao de correcao."
)


def montar_prompt_analise(linguagem: str, conteudo: str) -> str:
    """Monta o texto que descreve o codigo a ser revisado."""
    return (
        f"Linguagem do arquivo: {linguagem}\n\n"
        f"Codigo a revisar (com numero de linha no inicio de cada linha):\n\n"
        f"{numerar_linhas(conteudo)}"
    )


def numerar_linhas(texto: str) -> str:
    """Prefixa cada linha com o numero, para o modelo referenciar posicoes."""
    linhas = texto.splitlines()
    return "\n".join(f"{i:>4} | {linha}" for i, linha in enumerate(linhas, start=1))
