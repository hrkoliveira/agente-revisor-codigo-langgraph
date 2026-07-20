# Apresentacao (2 slides)

Conteudo dos slides da ideia do projeto. Pode ser passado para PowerPoint, Google
Slides ou Canva mantendo essa divisao.

---

## Slide 1: O problema e a proposta

**Agente Revisor de Codigo**

**Problema**
Revisar codigo na mao toma tempo e deixa escapar problema repetido: SQL injection,
`except` vazio, credencial esquecida, trecho pouco idiomatico.

**Processo automatizado**
A primeira passada da revisao de um arquivo de codigo.

**Proposta do agente**
Um agente em LangGraph que le o arquivo, analisa com IA e entrega um relatorio de
revisao pronto, com os problemas separados por severidade.

**Entrada:** caminho de um arquivo de codigo (Python, Java, JS, TS, SQL, Go).
**Saida:** relatorio em Markdown com nota, resumo e lista de achados.

---

## Slide 2: Como funciona

**Fluxo da solucao (LangGraph)**

```
Entrada (arquivo)
   -> Validar entrada  --(invalido)-->  encerra
   -> Preparar contexto (le o codigo)
   -> Analisar com o modelo (Anthropic)
   -> Gerar relatorio (grava o Markdown)
```

**Ferramentas:** leitura do arquivo de codigo e escrita do relatorio (acoes reais
no sistema de arquivos).

**Estado, contexto e memoria:** um estado compartilhado carrega a informacao entre
as etapas, e um checkpointer da memoria entre execucoes na mesma sessao.

**Seguranca e validacao:** chave de API fora do repositorio (`.env` + `.gitignore`
+ `.env.example`), saida estruturada e validada com Pydantic, e checagem da
entrada antes de chamar o modelo.
