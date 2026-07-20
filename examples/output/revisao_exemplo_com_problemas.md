# Revisao de codigo: exemplo_com_problemas.py

- Linguagem: Python
- Nota geral: 3/10
- Problemas encontrados: 8

## Resumo

O código contém vulnerabilidades sérias de segurança (SQL injection e senha hardcoded), além de vazamento de recursos, tratamento de erro inadequado e trechos que não seguem as boas práticas idiomáticas do Python.

## Achados

### [ALTA] seguranca (linha 5)

Senha em texto plano (hardcoded) no codigo fonte. Qualquer pessoa com acesso ao repositorio ve a credencial, e ela nao pode ser rotacionada sem alterar o codigo.

**Sugestao:** Nunca versione segredos. Carregue de variavel de ambiente (os.environ) ou de um cofre de segredos, e mantenha o valor fora do repositorio.

### [ALTA] seguranca (linha 12)

SQL Injection: a query e montada por concatenacao de string com o parametro 'nome', permitindo que um atacante injete SQL arbitrario.

**Sugestao:** Use queries parametrizadas: cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,)). Deixe o driver escapar o valor.

### [ALTA] boas praticas (linha 33)

Bloco 'except:' (bare except) captura todas as excecoes, inclusive KeyboardInterrupt e SystemExit, e o 'pass' engole o erro silenciosamente, escondendo falhas de escrita.

**Sugestao:** Capture excecoes especificas (ex.: except OSError as e) e trate/registre o erro (logging). Nao use pass silencioso.

### [MEDIA] bug (linha 9)

A conexao com o banco nunca e fechada. Em uso repetido isso vaza conexoes/handles de arquivo do SQLite. Alem disso, se execute lancar excecao, a conexao fica aberta.

**Sugestao:** Use context manager: 'with sqlite3.connect("banco.db") as conn:' e/ou feche explicitamente conn no bloco finally. Considere fechar tambem o cursor.

### [MEDIA] bug (linha 19)

Divisao sem tratamento para b == 0, o que gera ZeroDivisionError nao tratado.

**Sugestao:** Valide b antes de dividir e levante um erro claro (ex.: raise ValueError('b nao pode ser zero')) ou trate o caso conforme a regra de negocio.

### [MEDIA] bug (linha 31)

O arquivo aberto em modo 'w' nao e fechado; se write falhar o handle vaza. O open esta dentro do try mas sem garantia de close/flush.

**Sugestao:** Use 'with open("saida.txt", "w") as arquivo: arquivo.write(dados)', que garante o fechamento mesmo em caso de excecao.

### [BAIXA] legibilidade (linha 24)

Iteracao por indice com range(len(lista)) nao e idiomatica em Python e o acumulador manual reimplementa a funcao built-in sum.

**Sugestao:** Use 'return sum(lista)' ou, se precisar iterar, 'for item in lista'. Isso reduz risco de erro de indice e melhora a clareza.

### [BAIXA] boas praticas (linha 9)

Caminhos de banco e arquivo estao hardcoded, dificultando testes e reuso em ambientes diferentes.

**Sugestao:** Receba os caminhos por parametro ou configuracao, com valores padrao definidos externamente.
