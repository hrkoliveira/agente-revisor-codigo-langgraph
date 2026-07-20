"""
Ponto de entrada pela linha de comando.

Uso:
    python -m src.main examples/input/exemplo_com_problemas.py

O script recebe o caminho de um arquivo de codigo, roda o agente e mostra um
resumo no terminal. O relatorio completo fica gravado em examples/output.
"""

import sys

from dotenv import load_dotenv

from src.graph import construir_grafo


def executar(caminho_arquivo: str) -> None:
    """Roda o agente para um arquivo e imprime o resultado."""
    load_dotenv()  # carrega a ANTHROPIC_API_KEY do .env, se existir

    agente = construir_grafo()

    # O thread_id identifica a sessao. Com o checkpointer, o estado dessa thread
    # fica guardado e pode ser retomado em chamadas futuras.
    config = {"configurable": {"thread_id": "revisao-cli"}}

    estado_final = agente.invoke(
        {"caminho_arquivo": caminho_arquivo}, config=config
    )

    _imprimir_resultado(estado_final)


def _imprimir_resultado(estado: dict) -> None:
    if not estado.get("valido"):
        print("\nEntrada invalida:")
        print(f"  {estado.get('mensagem_erro')}\n")
        return

    achados = estado.get("achados", [])
    print("\n" + "=" * 60)
    print(f"Revisao concluida: {estado['caminho_arquivo']}")
    print("=" * 60)
    print(f"Linguagem: {estado.get('linguagem')}")
    print(f"Nota geral: {estado.get('nota_geral')}/10")
    print(f"Problemas encontrados: {len(achados)}")
    print(f"Resumo: {estado.get('resumo')}")
    print(f"\nRelatorio completo gravado em: {estado.get('caminho_relatorio')}\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python -m src.main <caminho_do_arquivo>")
        sys.exit(1)
    executar(sys.argv[1])


if __name__ == "__main__":
    main()
