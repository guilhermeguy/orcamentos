from base64 import encode
from fpdf import FPDF
from pathlib import Path
import os


class PDF(FPDF):
    """
    Classe personalizada para criar o PDF da Inovasol.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.PATH_LOGO = str(Path("./images/Logotipo_Inovasol.png"))
        self.PATH_DESENHO = str(
            Path("./images/esquema_geracao_fv_desenho_segg_20260111.png")
        )

    def header(self):
        # 1. Logotipo (Tenta carregar 'logo.png' da pasta atual)
        if os.path.exists(self.PATH_LOGO):
            self.image(self.PATH_LOGO, 10, 8, 33)

        self.set_font("Arial", "B", 15)
        self.cell(80)  # Move para a direita
        self.cell(30, 10, "Proposta Comercial - Sistema Fotovoltaico", 0, 0, "C")
        self.ln(25)  # Pula linha

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(
            0,
            10,
            f"Inovasol Engenharia de Energia - Pagina {self.page_no()}",
            0,
            0,
            "C",
        )


def criar_orcamento_pdf(cliente, financeiro):
    """
    Gera o PDF com base nos dicionários recebidos do app.py
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- SEÇÃO 1: DADOS DO CLIENTE ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Cliente: {cliente['nome']}", ln=True)
    pdf.ln(5)

    # --- SEÇÃO 2: TABELA DE CUSTOS ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(95, 96, 98)  # Cinza claro para cabeçalho

    # Cabeçalhos da Tabela
    pdf.cell(140, 8, "Descrição do Item", border=1, fill=True)
    pdf.cell(50, 8, "Valor (R$)", border=1, fill=True, ln=True)

    # Conteúdo da Tabela
    pdf.set_font("Arial", "", 10)

    # 1. Kit Fotovoltaico
    pdf.cell(140, 8, "Kit Gerador Fotovoltaico (Painéis + Inversor)", border=1)
    pdf.cell(50, 8, f"{financeiro['kit']:,.2f}", border=1, align="R", ln=True)

    # 2. Instalação Base
    pdf.cell(140, 8, "Mão de Obra e Instalação Base", border=1)
    pdf.cell(
        50, 8, f"{financeiro['instalacao_base']:,.2f}", border=1, align="R", ln=True
    )

    # 3. Itens Extras (Vêm da tabela editável do Streamlit)
    # Loop para adicionar cada item extra que o usuário digitou
    for item in financeiro["lista_extras"]:
        descricao = item.get("Descrição", "Item Extra")
        valor = item.get("Valor (R$)", 0.0)

        # Só imprime se o valor for diferente de zero ou descrição preenchida
        if valor > 0 or descricao:
            pdf.cell(140, 8, f"   - {descricao}", border=1)
            pdf.cell(50, 8, f"{valor:,.2f}", border=1, align="R", ln=True)

    # --- SEÇÃO 3: TOTAL ---
    pdf.ln(2)  # Pequeno espaço
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(193, 216, 47)  # Laranja (cor da Inovasol?)
    pdf.set_text_color(95, 96, 98)  # Texto Branco

    pdf.cell(140, 10, "VALOR FINAL DO INVESTIMENTO", border=1, fill=True)
    pdf.cell(
        50,
        10,
        f"R$ {financeiro['total_final']:,.2f}",
        border=1,
        fill=True,
        align="R",
        ln=True,
    )

    # Reset de cores
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # --- SEÇÃO 4: ANÁLISE DE RETORNO ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Estimativa de Retorno Financeiro", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(
        0, 8, f"Economia Mensal Estimada: R$ {financeiro['economia']:,.2f}", ln=True
    )
    pdf.cell(
        0, 8, f"Tempo de Retorno (Payback): {financeiro['payback']:.1f} Anos", ln=True
    )

    # Imagem Ilustrativa (Opcional)
    if os.path.exists("imagem_solar.jpg"):
        pdf.ln(10)
        # Centraliza a imagem (aproximadamente)
        pdf.image("imagem_solar.jpg", x=60, w=90)

    # Retorna o conteúdo do PDF como bytes (string binária)
    saida_pdf = pdf.output(dest="S")

    if isinstance(saida_pdf, str):
        return saida_pdf.encode("latin-1")
    else:
        return bytes(saida_pdf)
