from numpy import require
import streamlit as st
import pandas as pd
import base64
from gerador_pdf import criar_orcamento_pdf
import calculos

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
imoveis = [
    "imv1",
    "imv2",
    "imv3",
    "imv4",
]
dict_consumo = {(x, imv): 0 for x in meses for imv in imoveis}
dict_geracao = {x: 0 for x in meses}

with st.form("form_orcamento"):
    # Criamos 4 Abas para organizar a entrada de dados
    tab_cliente, tab_preco, tab_infos = st.tabs(
        ["Dados de Consumo", "Composição do Preço", "Informações adicionais"]
    )

    # --- ABA 1: DADOS DE CONSUMO ---
    with tab_cliente:
        st.subheader("Consumo Mensal (kWh)")
        st.caption("Inserir o imóvel com gerador no Imóvel 1!")

        # 1. Criamos um DataFrame pandas para servir de base
        # As linhas são os meses, as colunas são os imóveis
        df_inicial = pd.DataFrame(0, index=meses, columns=imoveis)

        # 2. Exibimos a tabela editável
        df_consumos = st.data_editor(
            df_inicial,
            use_container_width=True,
            height=460,  # Altura suficiente para ver o ano todo sem rolar
            column_config={
                "Imóvel 1": st.column_config.NumberColumn(required=True, min_value=0),
                "Imóvel 2": st.column_config.NumberColumn(required=True, min_value=0),
                "Imóvel 3": st.column_config.NumberColumn(required=True, min_value=0),
                "Imóvel 4": st.column_config.NumberColumn(required=True, min_value=0),
            },
        )
        st.markdown("---")
        st.markdown("**Custo de Disponibilidade (Taxa Mínima):**")
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)

        # Exemplo manual ou poderia ser outra tabela pequena
        disp_imv1 = col_d1.number_input("Disp. Imv 1", min_value=0, value=50)
        disp_imv2 = col_d2.number_input("Disp. Imv 2", min_value=0, value=0)
        disp_imv3 = col_d3.number_input("Disp. Imv 3", min_value=0, value=0)
        disp_imv4 = col_d4.number_input("Disp. Imv 4", min_value=0, value=0)

    # --- ABA 2: (Composição do Preço) ---
    #
    with tab_preco:
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            potencia_kit = st.number_input("Potência do Kit (kWp)", value=4.5)
            ganho_perda = st.number_input(
                "Ganho ou perda em relacao ao plano horizontal (%)", value=0
            )
        with col_t2:
            custo_kit = st.number_input("Custo do Kit (R$)", value=12000.00)
        with col_t3:
            adicional_projeto = st.number_input(
                "Adicional de valor de projeto (%)", value=0, step=5
            )
            st.caption("Valor do projeto calculado de acordo com a tabela de valores.")
        st.markdown("---")
        df_preco = pd.DataFrame(
            [
                {"Descr": "Mao de obra", "Qtd": 1, "Valor Unit (R$)": 1000.00},
                {"Descr": "ART", "Qtd": 1, "Valor Unit (R$)": 100.00},
                {"Descr": "Combustível", "Qtd": 1.0, "Valor Unit (R$)": 1.50},
                {"Descr": "Aluguel de Veículo", "Qtd": 1, "Valor Unit (R$)": 250.00},
                {
                    "Descr": "Equipamentos Adicionais",
                    "Qtd": 1,
                    "Valor Unit (R$)": 100.00,
                },
            ]
        )
        tabela_preco = st.data_editor(
            df_preco,
            column_config={
                "Descr": st.column_config.TextColumn(
                    "Descrição", width="medium", required=True
                ),
                "Qtd:": st.column_config.NumberColumn(
                    "Qtd",
                    min_value=0.0,
                    format="%f",
                    required=True,
                    step=0.1,
                    default=1.0,
                ),
                "Valor Unit (R$)": st.column_config.NumberColumn(
                    "Valor Unit. (R$)", min_value=0.0, format="R$ %.2f"
                ),
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
        )
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            comissao = st.slider(
                "Comissao de venda (%)", min_value=0, max_value=15, value=5, step=1
            )
        with col_a2:
            lucro_inovasol = st.slider(
                "Lucro Inovasol (%)", min_value=0, max_value=100, step=5, value=30
            )
    with tab_infos:
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            df_projeto = pd.DataFrame(
                [
                    {"de": 0, "ate": 5, "preco (R$)": 1080.00, "Potencia": "0 a 5 kWp"},
                    {
                        "de": 5,
                        "ate": 10,
                        "preco (R$)": 1180.00,
                        "Potencia": "5 a 10 kWp",
                    },
                    {
                        "de": 10,
                        "ate": 20,
                        "preco (R$)": 1650.00,
                        "Potencia": "10 a 20 kWp",
                    },
                    {
                        "de": 20,
                        "ate": 30,
                        "preco (R$)": 2650.00,
                        "Potencia": "20 a 30 kWp",
                    },
                    {
                        "de": 30,
                        "ate": 40,
                        "preco (R$)": 3650.00,
                        "Potencia": "30 a 40 kWp",
                    },
                    {
                        "de": 40,
                        "ate": 50,
                        "preco (R$)": 4650.00,
                        "Potencia": "40 a 50 kWp",
                    },
                    {
                        "de": 50,
                        "ate": 60,
                        "preco (R$)": 5650.00,
                        "Potencia": "50 a 60 kWp",
                    },
                    {
                        "de": 60,
                        "ate": 70,
                        "preco (R$)": 6650.00,
                        "Potencia": "60 a 70 kWp",
                    },
                    {
                        "de": 70,
                        "ate": 80,
                        "preco (R$)": 7650.00,
                        "Potencia": "70 a 80 kWp",
                    },
                    {
                        "de": 80,
                        "ate": 90,
                        "preco (R$)": 8650.00,
                        "Potencia": "80 a 90 kWp",
                    },
                    {
                        "de": 90,
                        "ate": 100,
                        "preco (R$)": 9650.00,
                        "Potencia": "90 a 100 kWp",
                    },
                ]
            )
            st.dataframe(
                df_projeto,
                use_container_width=True,
                hide_index=True,
                height=420,
            )
        with col_i2:
            df_nf = pd.DataFrame(
                [
                    {"descricao": "Custos Inovasol", "Valor (R$)": 0.0},
                    {"descricao": "Lucro Inovasol", "Valor (R$)": 0.0},
                    {"descricao": "Comissao do vendedor", "Valor (R$)": 0.0},
                    {"descricao": "Total impostos", "Valor (R$)": 0.0},
                ]
            )
            st.dataframe(
                df_nf,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Total da Nota Fiscal: R$ {df_nf['Valor (R$)'].sum()}")
            df_impostos = pd.DataFrame(
                [
                    {"imposto": "ISS", "Valor": 6.0},
                    {"imposto": "PIS", "Valor": 0.0},
                    {"imposto": "COFINS", "Valor": 0.0},
                    {"imposto": "CSLL", "Valor": 0.0},
                    {"imposto": "IRPF", "Valor": 0.0},
                ]
            )
            st.dataframe(
                df_impostos,
                use_container_width=True,
                hide_index=True,
                column_config={"Valor": st.column_config.NumberColumn(format="%.1f%%")},
            )
            st.caption(f"Total dos impostos: {df_impostos['Valor'].sum()}%")
    st.markdown("---")
    # Botão principal que submete o formulário e faz os cálculos
    submit_button = st.form_submit_button("🚀 Calcular Orçamento", type="primary")


# --- LÓGICA DE EXIBIÇÃO (Só roda se apertar o botão) ---
if submit_button:
    dict_disponibilidade = {
        "disp_imv1": disp_imv1,
        "disp_imv2": disp_imv2,
        "disp_imv3": disp_imv3,
        "disp_imv4": disp_imv4,
    }

    dict_custos = {
        "df_preco": df_preco,
        "lucro_inovasol": lucro_inovasol,
        "comissao": comissao,
        "potencia_kit": potencia_kit,
        "df_projeto": df_projeto,
        "adicional_projeto": adicional_projeto,
        "df_impostos": df_impostos,
        "custo_kit": custo_kit,
    }

    consumo_mensal = calculos.consumo_medio(df_consumos, dict_disponibilidade)
    geracao_mensal = calculos.geracao_mensal(
        potencia_kit, ganho_perda, potencia_referencia=7.8
    )

    dict_calc_custos = calculos.custo_total(dict_custos=dict_custos)
    # --- MOSTRAR RESULTADOS ---
    st.subheader("📊 Resultado da Análise")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Consumo médio total", f"{consumo_mensal:.0f} kWh")
    kpi2.metric("Geração Mensal", f"{geracao_mensal:.0f} kWh")
    kpi3.metric("Valor NF", f"R$ {dict_calc_custos['total_nf']:,.2f}")
    kpi4.metric("Custo Total do Projeto", f"R$ {dict_calc_custos['total_projeto']:.2f}")

    custo_wp, custo_wp_inovasol, custo_wp_equip = st.columns(3)
    custo_wp.metric(
        "Custo por Wp", f"R$ {dict_calc_custos['total_projeto'] / potencia_kit:.2f}"
    )
    custo_wp_inovasol.metric(
        "Custo por WP Inovasol", f"R$ {dict_calc_custos['total_nf'] / potencia_kit:.2f}"
    )
    custo_wp_equip.metric(
        "Custo por Wp Equipamentos",
        f"R$ {custo_kit / potencia_kit:.2f}",
    )
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
