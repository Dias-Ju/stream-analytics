import json

arquivo = 'pedidos_processados.jsonl'

total = 0
produtos = {}

try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            total += 1
            evento = json.loads(linha)

            produto = evento.get('produto')
            produtos[produto] = produtos.get(produto, 0) + 1

    print("ANÁLISE DOS DADOS")
    print("-" * 40)
    print(f"Total de pedidos: {total}")

    print("\nProdutos mais frequentes:")
    for p, qtd in produtos.items():
        print(f"{p}: {qtd}")

except FileNotFoundError:
    print("Arquivo não encontrado. Rode o consumer primeiro.")