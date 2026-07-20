# Agente Revisor de Codigo

Agente de IA construido com LangGraph que revisa um arquivo de codigo e gera um
relatorio de revisao em Markdown, com os problemas separados por severidade e uma
sugestao de correcao para cada um.

## O problema

Revisar codigo na mao toma tempo e depende de quem esta olhando estar atento
naquele momento. Numa primeira passada e comum deixar escapar coisa repetida:
concatenacao que abre SQL injection, `except` vazio que esconde erro, credencial
esquecida no meio do arquivo, trecho pouco idiomatico. Esse tipo de problema
aparece bastante em revisao de pull request e cansa quem revisa.

A ideia aqui e automatizar essa primeira passada. O agente le o arquivo, faz a
analise e devolve um relatorio pronto, que serve de ponto de partida para a
revisao humana continuar de onde faz sentido.

## Objetivo do agente

- **Entrada:** o caminho de um arquivo de codigo (Python, Java, JavaScript,
  TypeScript, SQL ou Go).
- **Processamento:** validar a entrada, ler o codigo, analisar com o modelo da
  Anthropic e organizar os achados.
- **Saida:** um relatorio em Markdown gravado em `examples/output/`, com nota
  geral, resumo e a lista de problemas por severidade, mais um resumo no
  terminal.

## Por que isso e um agente

Nao e so uma chamada solta ao modelo. Existe um fluxo com etapas bem definidas,
um estado que carrega a informacao de uma etapa para a outra, uma decisao de
caminho no meio do percurso (validar antes de gastar chamada de modelo),
ferramentas que agem no sistema de arquivos e uma saida estruturada e validada. O
agente decide se segue ou para, usa as ferramentas na hora certa e monta o
resultado sozinho.

## Fluxo com LangGraph

O agente e um `StateGraph`. Os nos sao as etapas e as arestas ligam uma na outra.
Depois da validacao existe uma aresta condicional: se a entrada for reprovada, o
grafo desvia para o no de erro e encerra, sem chamar o modelo.

```
        START
          |
   validar_entrada
        /      \
   (valido)   (invalido)
      |            |
preparar_contexto  relatar_erro
      |            |
analisar_codigo    END
      |
gerar_relatorio
      |
     END
```

O que cada no faz:

1. **validar_entrada:** confere se o arquivo existe, se a extensao e suportada, se
   nao esta vazio e se nao passa do limite de tamanho.
2. **preparar_contexto:** le o codigo do disco usando a ferramenta e guarda no
   estado.
3. **analisar_codigo:** envia o codigo ao modelo e recebe a resposta ja no formato
   do schema (saida estruturada com Pydantic).
4. **gerar_relatorio:** monta o Markdown e grava usando a ferramenta de escrita.
5. **relatar_erro:** caminho de saida quando a entrada foi reprovada.

### Estado, contexto e memoria

O estado compartilhado (`src/state.py`) e a memoria de trabalho da execucao. Cada
no le e escreve campos ali, entao o codigo lido, os achados e a nota vao se
acumulando ate o relatorio final.

Alem disso, o grafo usa um checkpointer (`MemorySaver`) com `thread_id`. Ele
guarda o estado por sessao, o que da ao agente memoria entre execucoes dentro da
mesma sessao, e nao so dentro de uma unica rodada.

## Ferramenta utilizada

O agente usa duas ferramentas que mexem de verdade no sistema de arquivos, em
`src/tools.py`:

- `ler_codigo`: le o conteudo do arquivo de codigo do disco.
- `salvar_relatorio`: grava o relatorio de revisao em Markdown.

As duas sao acoes reais, nao simuladas. E o que permite o agente ler a entrada e
entregar a saida sozinho.

## Cuidados de seguranca

- A chave da API fica em um arquivo `.env`, que esta no `.gitignore` e nunca vai
  para o repositorio.
- Tem um `.env.example` so com os nomes das variaveis, sem valor nenhum.
- A validacao de entrada barra arquivo inexistente, extensao desconhecida, arquivo
  vazio e arquivo grande demais, evitando processar dado malformado.

## Como executar

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate # Linux ou Mac
   ```

2. Instale as dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure a chave da API:

   ```bash
   copy .env.example .env      # Windows
   # cp .env.example .env      # Linux ou Mac
   ```

   Abra o `.env` e preencha a `ANTHROPIC_API_KEY`.

4. Rode o agente apontando para um arquivo:

   ```bash
   python -m src.main examples/input/exemplo_com_problemas.py
   ```

## Exemplo de entrada

O arquivo `examples/input/exemplo_com_problemas.py` tem problemas propositais:

```python
SENHA = "admin123"

def buscar_usuario(nome):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nome = '" + nome + "'")
    return cursor.fetchall()
```

## Exemplo de saida

No terminal:

```
============================================================
Revisao concluida: examples/input/exemplo_com_problemas.py
============================================================
Linguagem: Python
Nota geral: 3/10
Problemas encontrados: 8
Resumo: O codigo contem vulnerabilidades serias de seguranca (SQL injection e
senha hardcoded), alem de vazamento de recursos, tratamento de erro inadequado
e trechos que nao seguem as boas praticas idiomaticas do Python.

Relatorio completo gravado em: examples/output/revisao_exemplo_com_problemas.md
```

O relatorio completo fica em
[examples/output/revisao_exemplo_com_problemas.md](examples/output/revisao_exemplo_com_problemas.md).

## Principais decisoes

- **LangGraph com aresta condicional:** a validacao vem antes de tudo e pode cortar
  o fluxo. Assim o agente nao gasta chamada de modelo com entrada invalida.
- **Saida estruturada com Pydantic:** em vez de tratar texto livre do modelo, forco
  a resposta para um schema. Isso deixa o formato previsivel e valida o retorno.
- **Ferramentas separadas do resto:** leitura e escrita ficam isoladas em
  `tools.py`, o que deixa claro onde o agente toca o mundo externo.
- **Memoria via checkpointer:** usei o `MemorySaver` do proprio LangGraph em vez de
  inventar um mecanismo de memoria por fora.

## Limitacoes

- Revisa um arquivo por vez, nao um diretorio ou um diff inteiro.
- A qualidade da revisao depende do modelo e pode variar entre execucoes.
- O limite de tamanho de arquivo e simples, por numero de bytes.
- A memoria do checkpointer fica so na memoria do processo, entao nao sobrevive a
  um reinicio.

## Estrutura do projeto

```
agente-langgraph/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── src/
│   ├── state.py       # estado compartilhado do grafo
│   ├── schemas.py     # saida estruturada e validacao (Pydantic)
│   ├── tools.py       # ferramentas de leitura e escrita
│   ├── prompts.py     # prompts do agente
│   ├── nodes.py       # etapas do fluxo
│   ├── graph.py       # montagem do StateGraph
│   └── main.py        # execucao pela linha de comando
├── docs/
│   ├── prompts.md
│   └── apresentacao/
└── examples/
    ├── input/
    └── output/
```
