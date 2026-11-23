from dados import (
    produtos, pedidos, fila_prioridade, historico, pilha_desfazer,
    categorias, idx_produtos, idx_pedidos, contador,
)

# ==========================================
# ORDENAÇÃO MANUAL - MERGE SORT (estável)
# Tempo: O(n log n) melhor/médio/pior | Memória: O(n)
# ==========================================

def merge_sort(lista, chave=lambda x: x, reverso=False):
    if len(lista) <= 1:from dados import (
    produtos, pedidos, fila_prioridade, historico, pilha_desfazer,
    categorias, idx_produtos, idx_pedidos, contador,
)

# ==========================================
# ORDENAÇÃO MANUAL - MERGE SORT (estável)
# Tempo: O(n log n) melhor/médio/pior | Memória: O(n)
# ==========================================

def merge_sort(lista, chave=lambda x: x, reverso=False):
    if len(lista) <= 1:
        return list(lista)
    meio = len(lista) // 2
    esq = merge_sort(lista[:meio], chave, reverso)
    dir_ = merge_sort(lista[meio:], chave, reverso)
    res, i, j = [], 0, 0
    while i < len(esq) and j < len(dir_):
        a, b = chave(esq[i]), chave(dir_[j])
        pegar_esq = (a >= b) if reverso else (a <= b)
        if pegar_esq:
            res.append(esq[i]); i += 1
        else:
            res.append(dir_[j]); j += 1
    res.extend(esq[i:])
    res.extend(dir_[j:])
    return res


# ==========================================
# HEAP BINÁRIO MANUAL (fila de prioridade)
# inserir/extrair/remover: O(log n) (remover por pedido: O(n) p/ achar posição)
# item = (prioridade, prazo, ordem, pedido) ; menor = mais urgente
# ==========================================

def _item(pedido):
    return (pedido["prioridade"], pedido["prazo"], pedido["ordem"], pedido)


def _menor(a, b):
    return a[:3] < b[:3]


def _subir(h, i):
    while i > 0:
        p = (i - 1) // 2
        if _menor(h[i], h[p]):
            h[i], h[p] = h[p], h[i]
            i = p
        else:
            break


def _descer(h, i):
    n = len(h)
    while True:
        e, d, m = 2 * i + 1, 2 * i + 2, i
        if e < n and _menor(h[e], h[m]):
            m = e
        if d < n and _menor(h[d], h[m]):
            m = d
        if m == i:
            break
        h[i], h[m] = h[m], h[i]
        i = m


def heap_inserir(pedido):
    fila_prioridade.append(_item(pedido))
    _subir(fila_prioridade, len(fila_prioridade) - 1)


def heap_extrair():
    topo = fila_prioridade[0]
    ultimo = fila_prioridade.pop()
    if fila_prioridade:
        fila_prioridade[0] = ultimo
        _descer(fila_prioridade, 0)
    return topo[3]


def heap_remover(pedido):
    for i in range(len(fila_prioridade)):
        if fila_prioridade[i][3] is pedido:
            ultimo = fila_prioridade.pop()
            if i < len(fila_prioridade):
                fila_prioridade[i] = ultimo
                _subir(fila_prioridade, i)
                _descer(fila_prioridade, i)
            return


def exibir_fila_prioridade():
    """Cópia ordenada pelo merge sort manual: O(n log n)."""
    copia = merge_sort(fila_prioridade, chave=lambda it: it[:3])
    return [it[3] for it in copia]


# ==========================================
# AUXILIARES / BUSCAS
# ==========================================

def normalizar_codigo(codigo):
    try:
        return int(codigo)
    except (ValueError, TypeError):
        return None


def buscar_produto(codigo):          # O(1) via dicionário
    return idx_produtos.get(normalizar_codigo(codigo))


def buscar_pedido(numero):           # O(1) via dicionário
    return idx_pedidos.get(normalizar_codigo(numero))


def buscar_produtos_por_nome(texto):  # busca linear manual: O(n)
    texto = str(texto).strip().lower()
    achados = []
    for p in produtos:
        if texto in p["nome"].lower():
            achados.append(p)
    return achados


def estoque_disponivel(codigo):      # O(1): reservado é mantido incrementalmente
    p = buscar_produto(codigo)
    if p is None:
        return 0
    return p["estoque"] - p["reservado"]


def _registrar_categoria(cat):
    for c in categorias:
        if c == cat:
            return
    categorias.append(cat)


def _empilhar(*op):
    pilha_desfazer.append(op)       # O(1)


# ==========================================
# PRODUTOS - CRUD
# ==========================================

def _validar_produto(nome, categoria, preco, estoque):
    if nome is None or not str(nome).strip():
        return "O nome do produto é obrigatório."
    if categoria is None or not str(categoria).strip():
        return "Selecione uma categoria."
    try:
        float(preco); int(estoque)
    except (ValueError, TypeError):
        return "Preço ou estoque inválido."
    if float(preco) <= 0:
        return "O preço deve ser maior que zero."
    if int(estoque) < 0:
        return "O estoque não pode ser negativo."
    return None


def cadastrar_produto(codigo, nome, categoria, preco, estoque):
    codigo = normalizar_codigo(codigo)
    if codigo is None or codigo <= 0:
        return False, "Informe um código válido."
    if codigo in idx_produtos:
        return False, "Já existe um produto com esse código."
    erro = _validar_produto(nome, categoria, preco, estoque)
    if erro:
        return False, erro

    produto = {
        "codigo": codigo,
        "nome": str(nome).strip(),
        "categoria": str(categoria).strip(),
        "preco": float(preco),
        "estoque": int(estoque),
        "reservado": 0,
    }
    produtos.append(produto)
    idx_produtos[codigo] = produto
    _registrar_categoria(produto["categoria"])
    _empilhar("remover_produto", codigo)
    historico.append(f"Produto {produto['nome']} cadastrado.")
    return True, "Produto cadastrado com sucesso!"


def alterar_produto(codigo, nome, categoria, preco, estoque):
    produto = buscar_produto(codigo)
    if produto is None:
        return False, "Produto não encontrado."
    erro = _validar_produto(nome, categoria, preco, estoque)
    if erro:
        return False, erro
    if int(estoque) < produto["reservado"]:
        return False, (f"Estoque menor que o reservado por pedidos "
                       f"pendentes ({produto['reservado']}).")
    _empilhar("restaurar_produto", dict(produto))
    produto["nome"] = str(nome).strip()
    produto["categoria"] = str(categoria).strip()
    produto["preco"] = float(preco)
    produto["estoque"] = int(estoque)
    _registrar_categoria(produto["categoria"])
    historico.append(f"Produto {produto['codigo']} alterado.")
    return True, "Produto alterado com sucesso!"


def remover_produto(codigo):
    produto = buscar_produto(codigo)
    if produto is None:
        return False, "Produto não encontrado."
    if produto["reservado"] > 0:
        return False, "Produto possui pedido pendente. Remoção bloqueada."
    _remover_produto_raw(produto["codigo"])
    _empilhar("readicionar_produto", produto)
    historico.append(f"Produto {produto['nome']} removido.")
    return True, "Produto removido com sucesso!"


def _remover_produto_raw(codigo):
    produto = idx_produtos.pop(codigo)
    produtos.remove(produto)


def listar_produtos():
    return produtos


def filtrar_por_categoria(categoria):
    resultado = []
    for p in produtos:
        if p["categoria"] == categoria:
            resultado.append(p)
    return resultado


def ordenar_produtos(campo="nome", reverso=False):
    if campo == "nome":
        chave = lambda p: p["nome"].lower()
    else:
        chave = lambda p: p[campo]
    return merge_sort(produtos, chave, reverso)


def ordenar_produtos_por_nome():
    return ordenar_produtos("nome")


# ==========================================
# PEDIDOS - CRUD
# ==========================================

def _validar_pedido(cliente, quantidade, prioridade, prazo):
    if cliente is None or not str(cliente).strip():
        return "O nome do cliente é obrigatório."
    try:
        int(quantidade); int(prioridade); int(prazo)
    except (ValueError, TypeError):
        return "Quantidade, prioridade ou prazo inválido."
    if int(quantidade) <= 0:
        return "A quantidade deve ser maior que zero."
    if int(prioridade) not in (1, 2, 3):
        return "Prioridade inválida."
    if int(prazo) <= 0:
        return "O prazo (dias) deve ser maior que zero."
    return None


def _inserir_pedido_raw(pedido):
    pedidos.append(pedido)
    idx_pedidos[pedido["numero"]] = pedido
    if pedido["status"] == "Pendente":
        idx_produtos[pedido["codigo_produto"]]["reservado"] += pedido["quantidade"]
        heap_inserir(pedido)


def _remover_pedido_raw(numero):
    pedido = idx_pedidos.pop(numero)
    pedidos.remove(pedido)
    if pedido["status"] == "Pendente":
        heap_remover(pedido)
        idx_produtos[pedido["codigo_produto"]]["reservado"] -= pedido["quantidade"]
    return pedido


def _atualizar_pedido(pedido, campos):
    heap_remover(pedido)
    idx_produtos[pedido["codigo_produto"]]["reservado"] -= pedido["quantidade"]
    pedido.update(campos)
    idx_produtos[pedido["codigo_produto"]]["reservado"] += pedido["quantidade"]
    heap_inserir(pedido)


def cadastrar_pedido(numero, cliente, produto, quantidade, prioridade, prazo=7):
    numero = normalizar_codigo(numero)
    codigo = normalizar_codigo(produto)
    if numero is None or numero <= 0:
        return False, "Informe um número de pedido válido."
    if numero in idx_pedidos:
        return False, "Já existe um pedido com esse número."
    if codigo is None:
        return False, "Informe o código numérico do produto."
    prod = idx_produtos.get(codigo)
    if prod is None:
        return False, "Este produto não está cadastrado. Verifique o código."
    erro = _validar_pedido(cliente, quantidade, prioridade, prazo)
    if erro:
        return False, erro
    quantidade, prioridade, prazo = int(quantidade), int(prioridade), int(prazo)
    disponivel = estoque_disponivel(codigo)
    if quantidade > disponivel:
        return False, (f"Estoque insuficiente! Existem apenas "
                       f"{disponivel} unidades disponíveis.")

    contador["ordem"] += 1
    pedido = {
        "numero": numero,
        "cliente": str(cliente).strip(),
        "codigo_produto": codigo,
        "produto": prod["nome"],
        "quantidade": quantidade,
        "prioridade": prioridade,
        "prazo": prazo,
        "valor": round(prod["preco"] * quantidade, 2),
        "status": "Pendente",
        "ordem": contador["ordem"],
    }
    _inserir_pedido_raw(pedido)
    _empilhar("remover_pedido", numero)
    historico.append(f"Pedido {numero} cadastrado para {pedido['cliente']}.")
    return True, (f"Pedido cadastrado! Produto: {prod['nome']}. "
                  f"Disponível para novos pedidos: {estoque_disponivel(codigo)}.")


def alterar_pedido(numero, cliente=None, produto=None, quantidade=None,
                   prioridade=None, prazo=None):
    pedido = buscar_pedido(numero)
    if pedido is None:
        return False, "Pedido não encontrado."
    if pedido["status"] != "Pendente":
        return False, "Somente pedidos pendentes podem ser alterados."

    novo_cod = pedido["codigo_produto"] if produto is None else normalizar_codigo(produto)
    prod = idx_produtos.get(novo_cod) if novo_cod is not None else None
    if prod is None:
        return False, "Produto não encontrado."

    cli = pedido["cliente"] if cliente is None else cliente
    qtd = pedido["quantidade"] if quantidade is None else quantidade
    pri = pedido["prioridade"] if prioridade is None else prioridade
    prz = pedido["prazo"] if prazo is None else prazo
    erro = _validar_pedido(cli, qtd, pri, prz)
    if erro:
        return False, erro
    qtd, pri, prz = int(qtd), int(pri), int(prz)

    disponivel = estoque_disponivel(novo_cod)
    if novo_cod == pedido["codigo_produto"]:
        disponivel += pedido["quantidade"]
    if qtd > disponivel:
        return False, (f"Estoque insuficiente! Existem apenas "
                       f"{disponivel} unidades disponíveis.")

    antigo = {k: pedido[k] for k in
              ("cliente", "codigo_produto", "produto", "quantidade",
               "prioridade", "prazo", "valor")}
    novo = {
        "cliente": str(cli).strip(),
        "codigo_produto": novo_cod,
        "produto": prod["nome"],
        "quantidade": qtd,
        "prioridade": pri,
        "prazo": prz,
        "valor": round(prod["preco"] * qtd, 2),
    }
    _atualizar_pedido(pedido, novo)
    _empilhar("restaurar_pedido", pedido["numero"], antigo)
    historico.append(f"Pedido {pedido['numero']} alterado.")
    return True, "Pedido alterado com sucesso!"


def remover_pedido(numero):
    pedido = buscar_pedido(numero)
    if pedido is None:
        return False, "Pedido não encontrado."
    _remover_pedido_raw(pedido["numero"])
    # Regra: pedido já processado NÃO devolve estoque (mercadoria já saiu).
    _empilhar("readicionar_pedido", pedido)
    historico.append(f"Pedido {pedido['numero']} removido.")
    return True, "Pedido removido com sucesso!"


def listar_pedidos():
    return pedidos


def filtrar_pedidos_por_status(status):
    resultado = []
    for p in pedidos:
        if p["status"].lower() == status.lower():
            resultado.append(p)
    return resultado


def ordenar_pedidos(campo="numero", reverso=False, lista=None):
    base = pedidos if lista is None else lista
    return merge_sort(base, lambda p: p[campo], reverso)


# ==========================================
# PROCESSAR PEDIDO (topo do heap)
# ==========================================

def processar_pedido():
    if not fila_prioridade:
        return False, "Não existem pedidos na fila."
    pedido = fila_prioridade[0][3]
    prod = idx_produtos.get(pedido["codigo_produto"])
    if prod is None:
        return False, "O produto deste pedido não foi encontrado."
    if prod["estoque"] < pedido["quantidade"]:
        return False, "Estoque insuficiente para processar este pedido."

    heap_extrair()
    prod["estoque"] -= pedido["quantidade"]
    prod["reservado"] -= pedido["quantidade"]
    pedido["status"] = "Processado"
    _empilhar("reverter_processamento", pedido["numero"])
    historico.append(f"Pedido {pedido['numero']} processado. "
                     f"{pedido['quantidade']} un. de {prod['nome']} retiradas.")
    return True, (f"Pedido {pedido['numero']} processado! "
                  f"Estoque de {prod['nome']}: {prod['estoque']}.")


def exibir_historico():
    return historico


# ==========================================
# DESFAZER - PILHA DE OPERAÇÕES INVERSAS (O(1) por ação)
# ==========================================

def desfazer_ultima_acao():
    if not pilha_desfazer:
        return False, "Não existem ações para desfazer."
    op = pilha_desfazer.pop()
    tipo = op[0]

    if tipo == "remover_produto":
        _remover_produto_raw(op[1])
    elif tipo == "restaurar_produto":
        idx_produtos[op[1]["codigo"]].update(op[1])
    elif tipo == "readicionar_produto":
        produtos.append(op[1])
        idx_produtos[op[1]["codigo"]] = op[1]
    elif tipo == "remover_pedido":
        _remover_pedido_raw(op[1])
    elif tipo == "restaurar_pedido":
        _atualizar_pedido(idx_pedidos[op[1]], op[2])
    elif tipo == "readicionar_pedido":
        _inserir_pedido_raw(op[1])
    elif tipo == "reverter_processamento":
        pedido = idx_pedidos.get(op[1])
        if pedido is None:
            return False, "Pedido não existe mais; não foi possível desfazer."
        prod = idx_produtos[pedido["codigo_produto"]]
        prod["estoque"] += pedido["quantidade"]
        prod["reservado"] += pedido["quantidade"]
        pedido["status"] = "Pendente"
        heap_inserir(pedido)

    historico.append("Última operação desfeita.")
    return True, "Operação desfeita com sucesso!"

        return list(lista)
    meio = len(lista) // 2
    esq = merge_sort(lista[:meio], chave, reverso)
    dir_ = merge_sort(lista[meio:], chave, reverso)
    res, i, j = [], 0, 0
    while i < len(esq) and j < len(dir_):
        a, b = chave(esq[i]), chave(dir_[j])
        pegar_esq = (a >= b) if reverso else (a <= b)
        if pegar_esq:
            res.append(esq[i]); i += 1
        else:
            res.append(dir_[j]); j += 1
    res.extend(esq[i:])
    res.extend(dir_[j:])
    return res


# ==========================================
# HEAP BINÁRIO MANUAL (fila de prioridade)
# inserir/extrair/remover: O(log n) (remover por pedido: O(n) p/ achar posição)
# item = (prioridade, prazo, ordem, pedido) ; menor = mais urgente
# ==========================================

def _item(pedido):
    return (pedido["prioridade"], pedido["prazo"], pedido["ordem"], pedido)


def _menor(a, b):
    return a[:3] < b[:3]


def _subir(h, i):
    while i > 0:
        p = (i - 1) // 2
        if _menor(h[i], h[p]):
            h[i], h[p] = h[p], h[i]
            i = p
        else:
            break


def _descer(h, i):
    n = len(h)
    while True:
        e, d, m = 2 * i + 1, 2 * i + 2, i
        if e < n and _menor(h[e], h[m]):
            m = e
        if d < n and _menor(h[d], h[m]):
            m = d
        if m == i:
            break
        h[i], h[m] = h[m], h[i]
        i = m


def heap_inserir(pedido):
    fila_prioridade.append(_item(pedido))
    _subir(fila_prioridade, len(fila_prioridade) - 1)


def heap_extrair():
    topo = fila_prioridade[0]
    ultimo = fila_prioridade.pop()
    if fila_prioridade:
        fila_prioridade[0] = ultimo
        _descer(fila_prioridade, 0)
    return topo[3]


def heap_remover(pedido):
    for i in range(len(fila_prioridade)):
        if fila_prioridade[i][3] is pedido:
            ultimo = fila_prioridade.pop()
            if i < len(fila_prioridade):
                fila_prioridade[i] = ultimo
                _subir(fila_prioridade, i)
                _descer(fila_prioridade, i)
            return


def exibir_fila_prioridade():
    """Cópia ordenada pelo merge sort manual: O(n log n)."""
    copia = merge_sort(fila_prioridade, chave=lambda it: it[:3])
    return [it[3] for it in copia]


# ==========================================
# AUXILIARES / BUSCAS
# ==========================================

def normalizar_codigo(codigo):
    try:
        return int(codigo)
    except (ValueError, TypeError):
        return None


def buscar_produto(codigo):          # O(1) via dicionário
    return idx_produtos.get(normalizar_codigo(codigo))


def buscar_pedido(numero):           # O(1) via dicionário
    return idx_pedidos.get(normalizar_codigo(numero))


def buscar_produtos_por_nome(texto):  # busca linear manual: O(n)
    texto = str(texto).strip().lower()
    achados = []
    for p in produtos:
        if texto in p["nome"].lower():
            achados.append(p)
    return achados


def estoque_disponivel(codigo):      # O(1): reservado é mantido incrementalmente
    p = buscar_produto(codigo)
    if p is None:
        return 0
    return p["estoque"] - p["reservado"]


def _registrar_categoria(cat):
    for c in categorias:
        if c == cat:
            return
    categorias.append(cat)


def _empilhar(*op):
    pilha_desfazer.append(op)       # O(1)


# ==========================================
# PRODUTOS - CRUD
# ==========================================

def _validar_produto(nome, categoria, preco, estoque):
    if nome is None or not str(nome).strip():
        return "O nome do produto é obrigatório."
    if categoria is None or not str(categoria).strip():
        return "Selecione uma categoria."
    try:
        float(preco); int(estoque)
    except (ValueError, TypeError):
        return "Preço ou estoque inválido."
    if float(preco) <= 0:
        return "O preço deve ser maior que zero."
    if int(estoque) < 0:
        return "O estoque não pode ser negativo."
    return None


def cadastrar_produto(codigo, nome, categoria, preco, estoque):
    codigo = normalizar_codigo(codigo)
    if codigo is None or codigo <= 0:
        return False, "Informe um código válido."
    if codigo in idx_produtos:
        return False, "Já existe um produto com esse código."
    erro = _validar_produto(nome, categoria, preco, estoque)
    if erro:
        return False, erro

    produto = {
        "codigo": codigo,
        "nome": str(nome).strip(),
        "categoria": str(categoria).strip(),
        "preco": float(preco),
        "estoque": int(estoque),
        "reservado": 0,
    }
    produtos.append(produto)
    idx_produtos[codigo] = produto
    _registrar_categoria(produto["categoria"])
    _empilhar("remover_produto", codigo)
    historico.append(f"Produto {produto['nome']} cadastrado.")
    return True, "Produto cadastrado com sucesso!"


def alterar_produto(codigo, nome, categoria, preco, estoque):
    produto = buscar_produto(codigo)
    if produto is None:
        return False, "Produto não encontrado."
    erro = _validar_produto(nome, categoria, preco, estoque)
    if erro:
        return False, erro
    if int(estoque) < produto["reservado"]:
        return False, (f"Estoque menor que o reservado por pedidos "
                       f"pendentes ({produto['reservado']}).")
    _empilhar("restaurar_produto", dict(produto))
    produto["nome"] = str(nome).strip()
    produto["categoria"] = str(categoria).strip()
    produto["preco"] = float(preco)
    produto["estoque"] = int(estoque)
    _registrar_categoria(produto["categoria"])
    historico.append(f"Produto {produto['codigo']} alterado.")
    return True, "Produto alterado com sucesso!"


def remover_produto(codigo):
    produto = buscar_produto(codigo)
    if produto is None:
        return False, "Produto não encontrado."
    if produto["reservado"] > 0:
        return False, "Produto possui pedido pendente. Remoção bloqueada."
    _remover_produto_raw(produto["codigo"])
    _empilhar("readicionar_produto", produto)
    historico.append(f"Produto {produto['nome']} removido.")
    return True, "Produto removido com sucesso!"


def _remover_produto_raw(codigo):
    produto = idx_produtos.pop(codigo)
    produtos.remove(produto)


def listar_produtos():
    return produtos


def filtrar_por_categoria(categoria):
    resultado = []
    for p in produtos:
        if p["categoria"] == categoria:
            resultado.append(p)
    return resultado


def ordenar_produtos(campo="nome", reverso=False):
    if campo == "nome":
        chave = lambda p: p["nome"].lower()
    else:
        chave = lambda p: p[campo]
    return merge_sort(produtos, chave, reverso)


def ordenar_produtos_por_nome():
    return ordenar_produtos("nome")


# ==========================================
# PEDIDOS - CRUD
# ==========================================

def _validar_pedido(cliente, quantidade, prioridade, prazo):
    if cliente is None or not str(cliente).strip():
        return "O nome do cliente é obrigatório."
    try:
        int(quantidade); int(prioridade); int(prazo)
    except (ValueError, TypeError):
        return "Quantidade, prioridade ou prazo inválido."
    if int(quantidade) <= 0:
        return "A quantidade deve ser maior que zero."
    if int(prioridade) not in (1, 2, 3):
        return "Prioridade inválida."
    if int(prazo) <= 0:
        return "O prazo (dias) deve ser maior que zero."
    return None


def _inserir_pedido_raw(pedido):
    pedidos.append(pedido)
    idx_pedidos[pedido["numero"]] = pedido
    if pedido["status"] == "Pendente":
        idx_produtos[pedido["codigo_produto"]]["reservado"] += pedido["quantidade"]
        heap_inserir(pedido)


def _remover_pedido_raw(numero):
    pedido = idx_pedidos.pop(numero)
    pedidos.remove(pedido)
    if pedido["status"] == "Pendente":
        heap_remover(pedido)
        idx_produtos[pedido["codigo_produto"]]["reservado"] -= pedido["quantidade"]
    return pedido


def _atualizar_pedido(pedido, campos):
    heap_remover(pedido)
    idx_produtos[pedido["codigo_produto"]]["reservado"] -= pedido["quantidade"]
    pedido.update(campos)
    idx_produtos[pedido["codigo_produto"]]["reservado"] += pedido["quantidade"]
    heap_inserir(pedido)


def cadastrar_pedido(numero, cliente, produto, quantidade, prioridade, prazo=7):
    numero = normalizar_codigo(numero)
    codigo = normalizar_codigo(produto)
    if numero is None or numero <= 0:
        return False, "Informe um número de pedido válido."
    if numero in idx_pedidos:
        return False, "Já existe um pedido com esse número."
    if codigo is None:
        return False, "Informe o código numérico do produto."
    prod = idx_produtos.get(codigo)
    if prod is None:
        return False, "Este produto não está cadastrado. Verifique o código."
    erro = _validar_pedido(cliente, quantidade, prioridade, prazo)
    if erro:
        return False, erro
    quantidade, prioridade, prazo = int(quantidade), int(prioridade), int(prazo)
    disponivel = estoque_disponivel(codigo)
    if quantidade > disponivel:
        return False, (f"Estoque insuficiente! Existem apenas "
                       f"{disponivel} unidades disponíveis.")

    contador["ordem"] += 1
    pedido = {
        "numero": numero,
        "cliente": str(cliente).strip(),
        "codigo_produto": codigo,
        "produto": prod["nome"],
        "quantidade": quantidade,
        "prioridade": prioridade,
        "prazo": prazo,
        "valor": round(prod["preco"] * quantidade, 2),
        "status": "Pendente",
        "ordem": contador["ordem"],
    }
    _inserir_pedido_raw(pedido)
    _empilhar("remover_pedido", numero)
    historico.append(f"Pedido {numero} cadastrado para {pedido['cliente']}.")
    return True, (f"Pedido cadastrado! Produto: {prod['nome']}. "
                  f"Disponível para novos pedidos: {estoque_disponivel(codigo)}.")


def alterar_pedido(numero, cliente=None, produto=None, quantidade=None,
                   prioridade=None, prazo=None):
    pedido = buscar_pedido(numero)
    if pedido is None:
        return False, "Pedido não encontrado."
    if pedido["status"] != "Pendente":
        return False, "Somente pedidos pendentes podem ser alterados."

    novo_cod = pedido["codigo_produto"] if produto is None else normalizar_codigo(produto)
    prod = idx_produtos.get(novo_cod) if novo_cod is not None else None
    if prod is None:
        return False, "Produto não encontrado."

    cli = pedido["cliente"] if cliente is None else cliente
    qtd = pedido["quantidade"] if quantidade is None else quantidade
    pri = pedido["prioridade"] if prioridade is None else prioridade
    prz = pedido["prazo"] if prazo is None else prazo
    erro = _validar_pedido(cli, qtd, pri, prz)
    if erro:
        return False, erro
    qtd, pri, prz = int(qtd), int(pri), int(prz)

    disponivel = estoque_disponivel(novo_cod)
    if novo_cod == pedido["codigo_produto"]:
        disponivel += pedido["quantidade"]
    if qtd > disponivel:
        return False, (f"Estoque insuficiente! Existem apenas "
                       f"{disponivel} unidades disponíveis.")

    antigo = {k: pedido[k] for k in
              ("cliente", "codigo_produto", "produto", "quantidade",
               "prioridade", "prazo", "valor")}
    novo = {
        "cliente": str(cli).strip(),
        "codigo_produto": novo_cod,
        "produto": prod["nome"],
        "quantidade": qtd,
        "prioridade": pri,
        "prazo": prz,
        "valor": round(prod["preco"] * qtd, 2),
    }
    _atualizar_pedido(pedido, novo)
    _empilhar("restaurar_pedido", pedido["numero"], antigo)
    historico.append(f"Pedido {pedido['numero']} alterado.")
    return True, "Pedido alterado com sucesso!"


def remover_pedido(numero):
    pedido = buscar_pedido(numero)
    if pedido is None:
        return False, "Pedido não encontrado."
    _remover_pedido_raw(pedido["numero"])
    # Regra: pedido já processado NÃO devolve estoque (mercadoria já saiu).
    _empilhar("readicionar_pedido", pedido)
    historico.append(f"Pedido {pedido['numero']} removido.")
    return True, "Pedido removido com sucesso!"


def listar_pedidos():
    return pedidos


def filtrar_pedidos_por_status(status):
    resultado = []
    for p in pedidos:
        if p["status"].lower() == status.lower():
            resultado.append(p)
    return resultado


def ordenar_pedidos(campo="numero", reverso=False, lista=None):
    base = pedidos if lista is None else lista
    return merge_sort(base, lambda p: p[campo], reverso)


# ==========================================
# PROCESSAR PEDIDO (topo do heap)
# ==========================================

def processar_pedido():
    if not fila_prioridade:
        return False, "Não existem pedidos na fila."
    pedido = fila_prioridade[0][3]
    prod = idx_produtos.get(pedido["codigo_produto"])
    if prod is None:
        return False, "O produto deste pedido não foi encontrado."
    if prod["estoque"] < pedido["quantidade"]:
        return False, "Estoque insuficiente para processar este pedido."

    heap_extrair()
    prod["estoque"] -= pedido["quantidade"]
    prod["reservado"] -= pedido["quantidade"]
    pedido["status"] = "Processado"
    _empilhar("reverter_processamento", pedido["numero"])
    historico.append(f"Pedido {pedido['numero']} processado. "
                     f"{pedido['quantidade']} un. de {prod['nome']} retiradas.")
    return True, (f"Pedido {pedido['numero']} processado! "
                  f"Estoque de {prod['nome']}: {prod['estoque']}.")


def exibir_historico():
    return historico


# ==========================================
# DESFAZER - PILHA DE OPERAÇÕES INVERSAS (O(1) por ação)
# ==========================================

def desfazer_ultima_acao():
    if not pilha_desfazer:
        return False, "Não existem ações para desfazer."
    op = pilha_desfazer.pop()
    tipo = op[0]

    if tipo == "remover_produto":
        _remover_produto_raw(op[1])
    elif tipo == "restaurar_produto":
        idx_produtos[op[1]["codigo"]].update(op[1])
    elif tipo == "readicionar_produto":
        produtos.append(op[1])
        idx_produtos[op[1]["codigo"]] = op[1]
    elif tipo == "remover_pedido":
        _remover_pedido_raw(op[1])
    elif tipo == "restaurar_pedido":
        _atualizar_pedido(idx_pedidos[op[1]], op[2])
    elif tipo == "readicionar_pedido":
        _inserir_pedido_raw(op[1])
    elif tipo == "reverter_processamento":
        pedido = idx_pedidos.get(op[1])
        if pedido is None:
            return False, "Pedido não existe mais; não foi possível desfazer."
        prod = idx_produtos[pedido["codigo_produto"]]
        prod["estoque"] += pedido["quantidade"]
        prod["reservado"] += pedido["quantidade"]
        pedido["status"] = "Pendente"
        heap_inserir(pedido)

    historico.append("Última operação desfeita.")
    return True, "Operação desfeita com sucesso!"
