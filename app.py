import streamlit as st
import pandas as pd
import base64
from gerador_pdf import criar_orcamento_pdf
from calculos import calcular_cenario_solar

# --- Configuração Inicial da Página ---
st.set_page_config(page_title="Orçamentos Inovasol", layout="wide")

st.title("☀️ Gerador de Orçamentos - Inovasol")
st.markdown("---")

# ==========================================
# BARRA LATERAL (ENTRADA DE DADOS)
# ==========================================

st.sidebar.header("1. Dados do Cliente")
cliente_nome = st.sidebar.text_input("Nome do Cliente", "Ex: Padaria do João")
endereco_cliente = st.sidebar.text_input(
    "Endereço do cliente", "Ex: Alameda das Castanheiras"
)
cliente_numero = st.sidebar.number_input("Número do cliente", min_value=0, value=355)
numero_proposta = st.sidebar.number_input("Versão da proposta", min_value=0, value=1)
ano_proposta = st.sidebar.number_input("Ano da Proposta", min_value=2025, value=2026)

st.sidebar.header("2. Composição da Tarifa")
icms = st.sidebar.number_input("ICMS (%)", min_value=0.0, value=18.0)
pis = st.sidebar.number_input("PIS (%)", min_value=0.0, value=0.8)
cofins = st.sidebar.number_input("COFINS (%)", min_value=0.0, value=3.7)
fator_simultaneidade = st.sidebar.number_input(
    "Fator de Simultaniedade", min_value=0.0, max_value=1.0, value=0.38
)
custo_fio_b = st.sidebar.number_input("Custo Fio B (R$)", min_value=0.0, value=240.38)
custo_tusd = st.sidebar.number_input("Custo TUSD (R$/kWh)", min_value=0.0, value=0.4354)
custo_tusd_impostos = (
    custo_tusd / (1 - (pis / 100) - (cofins / 100)) / (1 - (icms / 100))
)
st.sidebar.caption(f"Custo TUSD com impostos: R$ {custo_tusd_impostos:.4f} por kWh")
custo_te = st.sidebar.number_input("Custo TE (R$/kWh)", min_value=0.0, value=0.3136)
custo_te_impostos = custo_te / (1 - (pis / 100) - (cofins / 100)) / (1 - (icms / 100))
st.sidebar.caption(f"Custo TE com impostos: R$ {custo_te_impostos:.4f} por kWh")


# ==========================================
# CÁLCULOS (O MOTOR DO SISTEMA)
# ==========================================

# 1. Custo Total para a Inovasol (Kit + Mão de Obra + Soma da Tabela)
# custo_total_inovasol = calculos["custo_total_inovasol"]

# 2. Preço de Venda (Custo + Margem)
# preco_final = calculos["preco_final"]

# 3. Estimativa de Geração (Fórmula padrão solar)
# geracao_estimada = calculos["geracao_estimada"]

# 4. Economia Financeira
# economia_mensal = calculos["economia_mensal"]

# payback = calculos["payback"]
#

# ==========================================
# VISUALIZAÇÃO
# ==========================================

# --- INÍCIO DO FORMULÁRIO ---
# O st.form impede que a página recarregue a cada digitação
meses = [
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
]
dict_consumo = {x: 0 for x in meses}
dict_geracao = {x: 0 for x in meses}

with st.form("form_orcamento"):
    # Criamos 4 Abas para organizar a entrada de dados
    tab_cliente, tab_preco = st.tabs(["Dados de Consumo", "Composição do Preço"])

    # --- ABA 1: DADOS DE CONSUMO ---
    with tab_cliente:
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.markdown("### Imóvel 1")
            for mes in dict_consumo:
                dict_consumo[mes] = st.number_input(
                    f"{mes.title()}", min_value=0, value=0, key=f"{mes}+'imovel1'"
                )
            st.markdown("---")
            st.number_input(
                "Custo de disponibilidade", min_value=0, value=0, key="imovel1_dispo"
            )

        with col_c2:
            st.markdown("### Imóvel 2")
            for mes in dict_consumo:
                dict_consumo[mes] = st.number_input(
                    f"{mes.title()}", min_value=0, value=0, key=f"{mes}+'imovel2'"
                )
            st.markdown("---")
            st.number_input(
                "Custo de disponibilidade", min_value=0, value=0, key="imovel2_dispo"
            )
        with col_c3:
            st.markdown("### Imóvel 3")
            for mes in dict_consumo:
                dict_consumo[mes] = st.number_input(
                    f"{mes.title()}", min_value=0, value=0, key=f"{mes}+'imovel3'"
                )
            st.markdown("---")
            st.number_input(
                "Custo de disponibilidade", min_value=0, value=0, key="imovel3_dispo"
            )
        with col_c4:
            st.markdown("### Imóvel 4")
            for mes in dict_consumo:
                dict_consumo[mes] = st.number_input(
                    f"{mes.title()}", min_value=0, value=0, key=f"{mes}+'imovel4'"
                )
            st.markdown("---")
            st.number_input(
                "Custo de disponibilidade", min_value=0, value=0, key="imovel4_dispo"
            )

    # --- ABA 2: (Composição do Preço) ---
    #
    with tab_preco:
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            potencia_kit = st.number_input("Potência do Kit (kWp)", value=4.5)
        with col_t2:
            custo_kit = st.number_input("Custo do Kit (R$)", value=12000.00)

    st.markdown("---")
    # Botão principal que submete o formulário e faz os cálculos
    submit_button = st.form_submit_button("🚀 Calcular Orçamento", type="primary")


# --- LÓGICA DE EXIBIÇÃO (Só roda se apertar o botão) ---
if submit_button:
    # 1. Somar os extras da tabela
    total_extras = tabela_extras["Valor"].sum()
    custo_total_projeto = custo_kit + custo_mao_obra + total_extras

    # 2. Chamar a nossa função de cálculo (do arquivo calculos.py)
    resultados = calcular_cenario_solar(
        consumo=consumo_medio,
        tarifa=tarifa_cemig,
        potencia_kit=potencia_kit,
        custo_total=custo_total_projeto,
        margem=margem_lucro,
    )

    # Desempacotar resultados para usar fácil
    preco_final = resultados["preco_final"]
    geracao = resultados["geracao_estimada"]
    economia = resultados["economia_mensal"]
    payback = resultados["payback_anos"]

    # --- MOSTRAR RESULTADOS ---
    st.subheader("📊 Resultado da Análise")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Investimento Final", f"R$ {preco_final:,.2f}")
    kpi2.metric("Geração Mensal", f"{geracao:.0f} kWh")
    kpi3.metric("Economia Mensal", f"R$ {economia:,.2f}")
    kpi4.metric("Payback", f"{payback:.1f} Anos")


# ==========================================
# GERAÇÃO DO PDF
# ==========================================

# Prepara os dados para enviar ao gerador_pdf.py
dados_cliente = {"nome": cliente_nome}

# Convertemos a tabela editada para uma lista de dicionários para facilitar no PDF
# Ex: [{'Descrição': 'Cabos', 'Valor (R$)': 50}, ...]
lista_itens_extras = tabela_editada.to_dict("records")

dados_financeiros = {
    "kit": custo_kit,
    "instalacao_base": custo_base_instalacao,
    "lista_extras": lista_itens_extras,  # Enviamos a lista detalhada
    "total_extras": total_extras_tabela,  # Enviamos a soma
    "total_final": preco_final,
    "economia": economia_mensal,
    "payback": payback_anos,
}

st.subheader("Emitir Proposta")

if st.button("📄 Gerar PDF da Proposta", type="primary"):
    try:
        # Chama a função mágica do outro arquivo
        pdf_bytes = criar_orcamento_pdf(dados_cliente, dados_financeiros)

        # Cria o link de download
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Orcamento_{cliente_nome}.pdf">📥 Clique aqui para baixar o PDF</a>'

        st.success("PDF Gerado com sucesso!")
        st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
