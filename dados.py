# ESTRUTURAS DE DADOS - ERP DISTRIBUIDORA
# Obs.: listas em nível de módulo => todos os visitantes compartilham dados
# e tudo some ao reiniciar o app (sem banco de dados, por escopo do trabalho).

produtos = []            # Lista (cadastro de produtos)
pedidos = []             # Lista (cadastro de pedidos)
fila_prioridade = []     # Heap binário manual: (prioridade, prazo, ordem, pedido)
historico = []           # Lista de mensagens
pilha_desfazer = []      # Pilha de operações inversas (padrão comando)

# Índices para busca O(1)
idx_produtos = {}        # codigo -> produto
idx_pedidos = {}         # numero -> pedido

# Contador de chegada (desempate FIFO)
contador = {"ordem": 0}

categorias = [
    "Alimentos",
    "Bebidas",
    "Higiene e limpeza",
    "Eletrônicos",
    "Informática e periféricos",
    "Utensílios domésticos",
    "Papelaria",
]
