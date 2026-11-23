import streamlit as st

from dados import produtos, pedidos, fila_prioridade, historico, categorias
import sistema as s

ss = st.session_state
ROT = {1: "Alta", 2: "Média", 3: "Baixa"}


# ==========================================
# CALLBACKS
# ==========================================

def _fb(res):
    ss["fb"] = res


def cb_cad_produto():
    res = s.cadastrar_produto(ss.get("cp_codigo"), ss.get("cp_nome"),
                              ss.get("cp_cat"), ss.get("cp_preco"), ss.get("cp_estoque"))
    _fb(res)
    if res[0]:
        ss["cp_codigo"] = None; ss["cp_nome"] = ""; ss["cp_cat"] = None
        ss["cp_preco"] = None; ss["cp_estoque"] = None


def cb_alt_produto():
    c = ss.get("ap_sel")
    _fb(s.alterar_produto(c, ss.get(f"ap_nome_{c}"), ss.get(f"ap_cat_{c}"),
                          ss.get(f"ap_preco_{c}"), ss.get(f"ap_estoque_{c}")))


def cb_rem_produto():
    _fb(s.remover_produto(ss.get("ap_sel")))


def cb_cad_pedido():
    res = s.cadastrar_pedido(ss.get("pd_numero"), ss.get("pd_cliente"),
                             ss.get("pd_produto"), ss.get("pd_qtd"),
                             ss.get("pd_prio"), ss.get("pd_prazo"))
    _fb(res)
    if res[0]:
        ss["pd_numero"] = None; ss["pd_cliente"] = ""; ss["pd_produto"] = None
        ss["pd_qtd"] = None; ss["pd_prio"] = 1; ss["pd_prazo"] = 7


def cb_alt_pedido():
    n = ss.get("ep_sel")
    _fb(s.alterar_pedido(n, ss.get(f"ep_cli_{n}"), ss.get(f"ep_prod_{n}"),
                         ss.get(f"ep_qtd_{n}"), ss.get(f"ep_prio_{n}"),
                         ss.get(f"ep_prazo_{n}")))


def cb_rem_pedido():
    _fb(s.remover_pedido(ss.get("ep_sel")))


def cb_processar():
    _fb(s.processar_pedido())


def cb_desfazer():
    _fb(s.desfazer_ultima_acao())


def mostrar_fb():
    fb = ss.pop("fb", None)
    if fb:
        (st.success if fb[0] else st.error)(fb[1])


# ==========================================
# LINHAS DE TABELA
# ==========================================

def linhas_produtos(lista):
    return [{"Código": p["codigo"], "Nome": p["nome"], "Categoria": p["categoria"],
             "Preço": p["preco"], "Estoque": p["estoque"],
             "Reservado": p["reservado"], "Disponível": p["estoque"] - p["reservado"]}
            for p in lista]


def linhas_pedidos(lista):
    return [{"Número": p["numero"], "Cliente": p["cliente"], "Produto": p["produto"],
             "Quantidade": p["quantidade"], "Prioridade": ROT[p["prioridade"]],
             "Prazo (dias)": p["prazo"], "Valor": p["valor"], "Status": p["status"]}
            for p in lista]


# ==========================================
# PÁGINA / ESTILO
# ==========================================

st.set_page_config(page_title="ERP Distribuidora", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #F7F9FC; color: #263445; }
[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E5EAF0; }
h1, h2, h3 { color: #24364B; font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: 10px 12px; border-radius: 7px; margin-bottom: 4px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background-color: #EAF1F8; color: #24558A; font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background-color: #F0F4F8; }
[data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #E5EAF0; padding: 22px; border-radius: 10px; }
[data-testid="stMetricLabel"] { color: #64748B; font-size: 14px; }
[data-testid="stMetricValue"] { color: #1E293B; font-size: 30px; font-weight: 600; }
div.stButton > button, div.stFormSubmitButton > button { background-color: #3267A8; color: #FFFFFF; border: none; border-radius: 7px; font-weight: 600; padding: 8px 18px; }
div.stButton > button:hover, div.stFormSubmitButton > button:hover { background-color: #244F85; color: #FFFFFF; }
[data-testid="stDataFrame"] { border: 1px solid #E5EAF0; border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("ERP Distribuidora")
st.caption("Sistema de gestão de produtos, estoque e pedidos")
st.sidebar.title("Distribuidora")
st.sidebar.caption("Gestão de produtos e pedidos")
st.sidebar.divider()

aba = st.sidebar.radio("Menu principal", [
    "Início", "Produtos", "Pedidos", "Fila de prioridade", "Histórico e desfazer"])


# ==========================================
# INÍCIO
# ==========================================

if aba == "Início":
    st.subheader("Visão geral")
    c1, c2, c3 = st.columns(3)
    c1.metric("Produtos cadastrados", len(produtos))
    c2.metric("Pedidos registrados", len(pedidos))
    c3.metric("Pedidos na fila", len(fila_prioridade))
    st.caption("Utilize o menu lateral para acessar as funções do sistema.")


# ==========================================
# PRODUTOS
# ==========================================

elif aba == "Produtos":
    mostrar_fb()
    t1, t2, t3 = st.tabs(["Consultar / listar", "Cadastrar", "Alterar / remover"])

    with t2:
        with st.container(border=True):
            st.subheader("Novo produto")
            with st.form("form_produto"):
                st.number_input("Código do produto", min_value=1, value=None, step=1,
                                placeholder="Digite o código", key="cp_codigo")
                st.text_input("Nome do produto", placeholder="Digite o nome", key="cp_nome")
                st.selectbox("Categoria", options=categorias, index=None,
                             placeholder="Selecione ou digite uma categoria",
                             accept_new_options=True, key="cp_cat")
                st.number_input("Preço", min_value=0.01, value=None, step=0.01,
                                placeholder="Digite o preço", key="cp_preco")
                st.number_input("Quantidade em estoque", min_value=0, value=None, step=1,
                                placeholder="Digite a quantidade", key="cp_estoque")
                st.form_submit_button("Cadastrar produto", width="stretch",
                                      on_click=cb_cad_produto)

    with t1:
        if not produtos:
            st.warning("Nenhum produto cadastrado.")
        else:
            st.markdown("#### Consulta")
            q1, q2 = st.columns(2)
            cod = q1.number_input("Buscar por código", min_value=1, value=None, step=1,
                                  placeholder="Código", key="bc_cod")
            nome = q2.text_input("Buscar por nome", placeholder="Parte do nome", key="bc_nome")
            if cod is not None:
                achado = s.buscar_produto(cod)
                if achado:
                    st.dataframe(linhas_produtos([achado]), width="stretch", hide_index=True)
                else:
                    st.info("Produto não encontrado.")
            if nome.strip():
                achados = s.buscar_produtos_por_nome(nome)
                if achados:
                    st.dataframe(linhas_produtos(achados), width="stretch", hide_index=True)
                else:
                    st.info("Nenhum produto com esse nome.")

            st.divider()
            st.markdown("#### Listagem")
            cats = ["Todas"]
            for p in produtos:
                if p["categoria"] not in cats:
                    cats.append(p["categoria"])
            f1, f2, f3 = st.columns(3)
            cat = f1.selectbox("Filtrar por categoria", cats)
            campo = f2.selectbox("Ordenar por", ["nome", "preco", "estoque", "codigo"],
                                 format_func=lambda x: {"nome": "Nome", "preco": "Preço",
                                                        "estoque": "Estoque", "codigo": "Código"}[x])
            rev = f3.checkbox("Ordem decrescente")
            ordenados = s.ordenar_produtos(campo, rev)
            if cat != "Todas":
                filtrados = []
                for p in ordenados:
                    if p["categoria"] == cat:
                        filtrados.append(p)
                ordenados = filtrados
            st.write(f"Total de produtos encontrados: {len(ordenados)}")
            st.dataframe(linhas_produtos(ordenados), width="stretch", hide_index=True)

    with t3:
        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            cods = [p["codigo"] for p in s.ordenar_produtos("codigo")]
            c = st.selectbox("Produto", cods, key="ap_sel",
                             format_func=lambda x: f"{x} - {s.buscar_produto(x)['nome']}")
            p = s.buscar_produto(c)
            if p:
                with st.container(border=True):
                    st.text_input("Nome", value=p["nome"], key=f"ap_nome_{c}")
                    idx = categorias.index(p["categoria"]) if p["categoria"] in categorias else None
                    st.selectbox("Categoria", options=categorias, index=idx,
                                 accept_new_options=True, key=f"ap_cat_{c}")
                    st.number_input("Preço", min_value=0.01, value=float(p["preco"]),
                                    step=0.01, key=f"ap_preco_{c}")
                    st.number_input("Estoque", min_value=0, value=int(p["estoque"]),
                                    step=1, key=f"ap_estoque_{c}")
                    b1, b2 = st.columns(2)
                    b1.button("Salvar alterações", width="stretch", on_click=cb_alt_produto)
                    b2.button("Remover produto", width="stretch", on_click=cb_rem_produto)


# ==========================================
# PEDIDOS
# ==========================================

elif aba == "Pedidos":
    mostrar_fb()
    t1, t2, t3 = st.tabs(["Consultar / listar", "Cadastrar", "Alterar / remover"])

    with t2:
        with st.container(border=True):
            st.subheader("Novo pedido")
            if not produtos:
                st.warning("Cadastre pelo menos um produto antes de criar pedidos.")
            else:
                with st.form("form_pedido"):
                    st.number_input("Número do pedido", min_value=1, value=None, step=1,
                                    placeholder="Número", key="pd_numero")
                    st.text_input("Nome do cliente", placeholder="Cliente", key="pd_cliente")
                    st.number_input("Código do produto", min_value=1, value=None, step=1,
                                    placeholder="Código do produto", key="pd_produto")
                    st.number_input("Quantidade solicitada", min_value=1, value=None, step=1,
                                    placeholder="Quantidade", key="pd_qtd")
                    st.selectbox("Prioridade", [1, 2, 3], format_func=lambda x: ROT[x],
                                 key="pd_prio")
                    st.number_input("Prazo de entrega (dias)", min_value=1, value=7, step=1,
                                    key="pd_prazo")
                    st.form_submit_button("Cadastrar pedido", width="stretch",
                                          on_click=cb_cad_pedido)

    with t1:
        if not pedidos:
            st.info("Nenhum pedido cadastrado.")
        else:
            st.markdown("#### Consulta")
            num = st.number_input("Buscar por número do pedido", min_value=1, value=None,
                                  step=1, placeholder="Número", key="bp_num")
            if num is not None:
                achado = s.buscar_pedido(num)
                if achado:
                    st.dataframe(linhas_pedidos([achado]), width="stretch", hide_index=True)
                else:
                    st.info("Pedido não encontrado.")

            st.divider()
            st.markdown("#### Listagem")
            f1, f2, f3 = st.columns(3)
            status = f1.selectbox("Filtrar por status", ["Todos", "Pendente", "Processado"])
            campo = f2.selectbox("Ordenar por", ["numero", "valor", "prazo", "quantidade"],
                                 format_func=lambda x: {"numero": "Número", "valor": "Valor",
                                                        "prazo": "Prazo", "quantidade": "Quantidade"}[x])
            rev = f3.checkbox("Ordem decrescente")
            base = pedidos if status == "Todos" else s.filtrar_pedidos_por_status(status)
            lista = s.ordenar_pedidos(campo, rev, base)
            st.write(f"Total de pedidos: {len(lista)}")
            st.dataframe(linhas_pedidos(lista), width="stretch", hide_index=True)

    with t3:
        if not pedidos:
            st.info("Nenhum pedido cadastrado.")
        else:
            nums = [p["numero"] for p in s.ordenar_pedidos("numero")]
            n = st.selectbox("Pedido", nums, key="ep_sel",
                             format_func=lambda x: f"{x} - {s.buscar_pedido(x)['cliente']} "
                                                   f"({s.buscar_pedido(x)['status']})")
            p = s.buscar_pedido(n)
            if p:
                with st.container(border=True):
                    if p["status"] != "Pendente":
                        st.caption("Pedido processado: só pode ser removido "
                                   "(o estoque NÃO é devolvido).")
                    else:
                        st.text_input("Cliente", value=p["cliente"], key=f"ep_cli_{n}")
                        st.number_input("Código do produto", min_value=1,
                                        value=int(p["codigo_produto"]), step=1, key=f"ep_prod_{n}")
                        st.number_input("Quantidade", min_value=1, value=int(p["quantidade"]),
                                        step=1, key=f"ep_qtd_{n}")
                        st.selectbox("Prioridade", [1, 2, 3], index=p["prioridade"] - 1,
                                     format_func=lambda x: ROT[x], key=f"ep_prio_{n}")
                        st.number_input("Prazo (dias)", min_value=1, value=int(p["prazo"]),
                                        step=1, key=f"ep_prazo_{n}")
                    b1, b2 = st.columns(2)
                    if p["status"] == "Pendente":
                        b1.button("Salvar alterações", width="stretch", on_click=cb_alt_pedido)
                    b2.button("Remover pedido", width="stretch", on_click=cb_rem_pedido)


# ==========================================
# FILA DE PRIORIDADE
# ==========================================

elif aba == "Fila de prioridade":
    st.subheader("Fila de pedidos")
    st.caption("Ordem: prioridade, depois menor prazo, depois chegada.")
    if fila_prioridade:
        st.dataframe(linhas_pedidos(s.exibir_fila_prioridade()),
                     width="stretch", hide_index=True)
        st.button("Processar próximo pedido", width="stretch", on_click=cb_processar)
    else:
        st.info("Não existem pedidos na fila.")
    mostrar_fb()


# ==========================================
# HISTÓRICO E DESFAZER
# ==========================================

elif aba == "Histórico e desfazer":
    st.subheader("Histórico de operações")
    if historico:
        for item in reversed(historico):
            st.write("•", item)
    else:
        st.info("Nenhuma operação registrada.")
    st.divider()
    st.button("Desfazer última operação", width="stretch", on_click=cb_desfazer)
    mostrar_fb()
