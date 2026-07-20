# Prompts do projeto

Aqui ficam registrados os prompts principais que usei. Separei em dois grupos: os
que o agente usa em tempo de execucao (ficam no codigo, em `src/prompts.py`) e os
que usei durante o desenvolvimento para planejar, implementar e melhorar a
solucao.

## 1. Prompts que o agente usa em execucao

### 1.1. Instrucao de sistema do revisor

Esse e o texto que define o papel do modelo na hora de revisar o codigo. Fica em
`src/prompts.py` na constante `INSTRUCAO_SISTEMA`:

> Voce e um revisor de codigo experiente. Sua tarefa e analisar o codigo recebido
> e apontar problemas de forma objetiva e util para quem escreveu.
> Procure por: bugs, riscos de seguranca, problemas de performance, codigo dificil
> de ler, nomes ruins, falta de tratamento de erro e desvios de boas praticas da
> linguagem.
> Seja direto. Nao invente problema onde nao existe. Se o codigo estiver bom,
> devolva a lista de achados vazia e uma nota alta.
> Para cada problema, informe a severidade, a categoria, a linha aproximada quando
> der, a descricao e uma sugestao de correcao.

### 1.2. Prompt de analise

Montado em tempo de execucao pela funcao `montar_prompt_analise`. Ele envia a
linguagem detectada e o codigo com as linhas numeradas, para o modelo conseguir
apontar a posicao de cada problema:

> Linguagem do arquivo: {linguagem}
>
> Codigo a revisar (com numero de linha no inicio de cada linha):
>
> {codigo numerado}

A saida desse prompt e forcada para o formato do schema `ResultadoRevisao`
(Pydantic), entao o modelo sempre responde com a lista de achados, o resumo e a
nota.

## 2. Prompts que usei no desenvolvimento

### 2.1. Planejamento

> Quero construir um agente com LangGraph que revisa um arquivo de codigo e gera
> um relatorio em Markdown. Me ajuda a desenhar o fluxo em nos: validacao da
> entrada, preparacao do contexto lendo o arquivo, analise pelo modelo e geracao
> do relatorio. O que deve entrar no estado compartilhado?

### 2.2. Implementacao

> Escreve o StateGraph com uma aresta condicional depois da validacao: se a
> entrada for invalida, desvia para um no de erro e encerra sem chamar o modelo.
> Se for valida, segue para a analise.

> Como forco o retorno do modelo da Anthropic para um schema Pydantic usando o
> langchain-anthropic? Quero campos de severidade, categoria, linha, descricao e
> sugestao.

### 2.3. Correcao e melhoria

> Adiciona validacao de entrada antes de gastar chamada de modelo: checar se o
> arquivo existe, se a extensao e suportada, se nao esta vazio e se nao passa de
> um limite de tamanho.

> Quero que o agente tenha memoria entre execucoes na mesma sessao. Como ligo um
> checkpointer no LangGraph e uso um thread_id para isso?
