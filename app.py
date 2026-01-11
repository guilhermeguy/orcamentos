import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from gerador_pdf import criar_orcamento_pdf

# --- Configuração Inicial da Página ---
st.set_page_config(page_title="Orçamentos Inovasol", layout="wide")

st.title("☀️ Gerador de Orçamentos - Inovasol")
st.markdown("---")

# ==========================================
# BARRA LATERAL (ENTRADA DE DADOS)
# ==========================================

st.sidebar.header("1. Dados do Cliente")
cliente_nome = st.sidebar.text_input("Nome do Cliente", "Ex: Padaria do João")

st.sidebar.header("2. Consumo e Energia")
consumo_medio = st.sidebar.number_input(
    "Consumo Médio (kWh)", min_value=0, value=500, help="Média da conta de luz"
)
tarifa_cemig = st.sidebar.number_input(
    "Tarifa (R$/kWh)", min_value=0.0, value=0.95, format="%.2f"
)

st.sidebar.header("3. Equipamento (Kit)")
custo_kit = st.sidebar.number_input(
    "Custo do Kit PHB (R$)", min_value=0.0, value=12000.00
)
potencia_kit = st.sidebar.number_input(
    "Potência do Kit (kWp)", min_value=0.0, value=4.5
)

# --- NOVIDADE: TABELA DE CUSTOS EXTRAS ---
st.sidebar.header("4. Custos de Instalação e Extras")

# Custo fixo base (mão de obra padrão, etc)
custo_base_instalacao = st.sidebar.number_input("Mão de Obra Base (R$)", value=3000.0)

# Lista inicial para a tabela (Exemplo)
dados_iniciais = [
    {"Descrição": "Cabos Solares (Extras)", "Valor (R$)": 0.00},
    {"Descrição": "Estrutura Solo", "Valor (R$)": 0.00},
    {"Descrição": "Homologação/Projeto", "Valor (R$)": 1500.00},
]

# Criação do DataFrame (a tabela do Pandas)
df_custos_extras = pd.DataFrame(dados_iniciais)

# O Expander serve para "esconder" a tabela e não poluir a tela se não for usada
with st.sidebar.expander("📝 Detalhar Outros Custos (Tabela)", expanded=True):
    st.write("Adicione ou remova itens de custo:")
    # O st.data_editor permite ao usuário modificar a tabela na hora!
    # num_rows="dynamic" permite adicionar linhas novas
    tabela_editada = st.data_editor(
        df_custos_extras, num_rows="dynamic", use_container_width=True, hide_index=True
    )

# SOMA AUTOMÁTICA: O Pandas soma a coluna "Valor (R$)" instantaneamente
total_extras_tabela = tabela_editada["Valor (R$)"].sum()

# Mostra o subtotal na barra lateral para conferência
st.sidebar.caption(f"Subtotal Extras: R$ {total_extras_tabela:,.2f}")

# Margem de Lucro
st.sidebar.markdown("---")
margem_lucro = st.sidebar.slider("Margem de Lucro (%)", 0, 100, 20)


# ==========================================
# CÁLCULOS (O MOTOR DO SISTEMA)
# ==========================================

# 1. Custo Total para a Inovasol (Kit + Mão de Obra + Soma da Tabela)
custo_total_inovasol = custo_kit + custo_base_instalacao + total_extras_tabela

# 2. Preço de Venda (Custo + Margem)
preco_final = custo_total_inovasol * (1 + (margem_lucro / 100))

# 3. Estimativa de Geração (Fórmula padrão solar)
geracao_estimada = potencia_kit * 5.0 * 30 * 0.80

# 4. Economia Financeira
economia_mensal = geracao_estimada * tarifa_cemig

# 5. Payback (Tempo de retorno)
if economia_mensal > 0:
    payback_meses = preco_final / economia_mensal
    payback_anos = payback_meses / 12
else:
    payback_anos = 0


# ==========================================
# VISUALIZAÇÃO (DASHBOARD)
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Geração Estimada", f"{geracao_estimada:.0f} kWh/mês")
    percentual = (geracao_estimada / consumo_medio) * 100 if consumo_medio > 0 else 0
    st.info(f"Cobertura: {percentual:.1f}% da conta")

with col2:
    st.metric("Economia Mensal", f"R$ {economia_mensal:,.2f}")
    st.metric("Investimento Final", f"R$ {preco_final:,.2f}")

with col3:
    st.metric("Retorno (Payback)", f"{payback_anos:.1f} Anos")
    if payback_anos < 4:
        st.success("⚡ Retorno Rápido!")
    else:
        st.warning("Retorno Padrão")

# Gráfico simples
st.markdown("---")
st.subheader("Comparativo em 1 Ano")

gasto_sem_solar = consumo_medio * tarifa_cemig * 12
gasto_com_solar = 0  # Considerando que zerou a conta (exceto taxa mínima)

dados_grafico = pd.DataFrame(
    {
        "Cenário": ["Sem Energia Solar", "Com Inovasol"],
        "Gasto Acumulado (R$)": [gasto_sem_solar, gasto_com_solar],
    }
)

st.bar_chart(dados_grafico.set_index("Cenário"))


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
