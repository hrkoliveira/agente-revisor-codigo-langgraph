"""
Modelos de dados do agente.

Uso o Pydantic aqui por dois motivos: forcar o modelo de linguagem a devolver
a analise sempre no mesmo formato (saida estruturada) e validar esse retorno
antes de gerar o relatorio. Se o modelo devolver algo fora do esperado, o
Pydantic reclama e a gente evita processar dado malformado.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Severidade(str, Enum):
    """Nivel de gravidade de um problema encontrado na revisao."""

    alta = "alta"
    media = "media"
    baixa = "baixa"


class Achado(BaseModel):
    """Um problema individual encontrado no codigo."""

    severidade: Severidade = Field(
        description="Gravidade do problema: alta, media ou baixa"
    )
    categoria: str = Field(
        description="Tipo do problema, por exemplo: seguranca, performance, "
        "legibilidade, bug, boas praticas"
    )
    linha: Optional[int] = Field(
        default=None,
        description="Linha aproximada onde o problema aparece, quando aplicavel",
    )
    descricao: str = Field(description="Explicacao objetiva do problema")
    sugestao: str = Field(description="Como corrigir ou melhorar")


class ResultadoRevisao(BaseModel):
    """Resultado completo da revisao de um arquivo."""

    achados: List[Achado] = Field(
        description="Lista de problemas encontrados. Pode ser vazia se o codigo "
        "estiver bom."
    )
    resumo: str = Field(
        description="Resumo geral da revisao em uma ou duas frases"
    )
    nota_geral: int = Field(
        ge=0,
        le=10,
        description="Nota de 0 a 10 para a qualidade geral do codigo",
    )
