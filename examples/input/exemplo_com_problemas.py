import sqlite3

# Arquivo de exemplo com problemas propositais, para o agente ter o que revisar.

SENHA = "admin123"


def buscar_usuario(nome):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    # Query montada por concatenacao: aberta a SQL injection
    cursor.execute("SELECT * FROM usuarios WHERE nome = '" + nome + "'")
    resultado = cursor.fetchall()
    return resultado


def dividir(a, b):
    # Sem tratamento para divisao por zero
    return a / b


def processar(lista):
    x = 0
    for i in range(len(lista)):
        x = x + lista[i]
    return x


def salvar(dados):
    try:
        arquivo = open("saida.txt", "w")
        arquivo.write(dados)
    except:
        pass
