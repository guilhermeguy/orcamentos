from fpdf import FPDF
from datetime import datetime
from typing import Any


class PDFProposta(FPDF):
    def header(self):
        # O cabeçalho é personalizado por página no design fornecido,
        # então deixaremos este método genérico ou vazio se não houver repetição fixa.
        pass

    def footer(self):
        # Rodapé simples com numeração de página
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def criar_pdf(dados: dict, graficos: Any) -> bytes:
    """
    Gera o PDF da proposta comercial.

    Args:
        dados (dict): Dicionário com dados do cliente, sistema e financeiros.
        graficos (dict): Dicionário com objetos BytesIO ou caminhos das imagens dos gráficos.
    """

    # --- Configurações Iniciais ---
    pdf = PDFProposta(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cores da Marca (Baseado no PDF)
    COR_VERDE = (184, 212, 50)  # Aproximação do verde limão
    COR_CINZA = (80, 80, 80)  # Cinza escuro
    COR_CINZA_CLARO = (240, 240, 240)

    # ==============================================================================
    # PÁGINA 1: CAPA
    # ==============================================================================
    pdf.add_page()

    # Logo
    pdf.image(
        "images/Logotipo_Inovasol.png", x=10, y=10, w=60
    )  # Descomente se tiver a imagem
    pdf.ln(20)  # Espaço após logo

    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*COR_CINZA)
    pdf.cell(0, 20, "Proposta de Orçamento", ln=True, align="R")

    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Sistema Fotovoltaico Conectado à Rede", ln=True, align="R")

    # Linha decorativa
    pdf.set_draw_color(*COR_VERDE)
    pdf.set_line_width(1)
    pdf.line(10, 65, 200, 65)

    # Dados do Cliente (Centro da página)
    pdf.ln(40)
    pdf.set_text_color(*COR_CINZA)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, dados.get("nome_cliente", "Nome do cliente"), ln=True, align="C")

    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, dados.get("cidade", "Cidade do cliente"), ln=True, align="C")

    # Rodapé da Capa
    pdf.set_y(-50)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(
        0, 10, f"Proposta: {dados.get('numero_proposta', '999')}", ln=True, align="R"
    )
    pdf.cell(0, 10, f"{dados.get('data', '01-01-2026')}", ln=True, align="R")

    # ==============================================================================
    # PÁGINA 2: FUNCIONAMENTO
    # ==============================================================================
    pdf.add_page()

    # Imagem esquemática (Sol -> Casa)
    # pdf.image("assets/esquema_solar.png", x=10, y=20, w=190)
    pdf.ln(80)  # Espaço reservado para a imagem

    # Título: Sobre a Inovasol
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Sobre a Inovasol", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    texto_sobre = (
        "Criada em 2015 é formada por engenheiros com mais de 35 anos de experiência "
        "em geração de energia elétrica, com carreira profissional na CEMIG..."
    )
    pdf.multi_cell(0, 5, texto_sobre)
    pdf.ln(5)

    # Lista numerada: Funcionamento
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Funcionamento do Sistema Fotovoltaico", ln=True)

    itens_funcionamento = [
        "A luz do sol incide sobre os módulos que a convertem em CC.",
        "O inversor converte CC em CA (compatível com a rede).",
        "O inversor monitora os dados para acompanhamento online.",
        "Excedente de energia gera créditos na concessionária.",
        "A rede da concessionária supre a energia à noite.",
    ]

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for i, item in enumerate(itens_funcionamento, 1):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*COR_VERDE)
        pdf.cell(10, 8, f"{i}.", ln=0)  # Número verde

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, item)  # Texto preto

    # ==============================================================================
    # PÁGINA 3: VANTAGENS E PRAZOS
    # ==============================================================================
    pdf.add_page()

    # Vantagens
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Vantagens do Sistema Fotovoltaico", ln=True)

    vantagens = [
        "Redução da conta de luz e proteção contra tarifas.",
        "Investimento seguro e alta durabilidade.",
        "Geração de créditos para usar em até 60 meses.",
        "Valorização do imóvel (3% a 6%).",
        "Marketing ecológico e baixo impacto ambiental.",
    ]

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for v in vantagens:
        pdf.cell(5, 6, chr(149), ln=0)  # Bullet point
        pdf.multi_cell(0, 6, v)

    pdf.ln(10)

    # Etapas e Prazos (Simulação visual)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Etapas e Prazos", ln=True)

    # Criando caixas simples para simular o timeline
    etapas = [
        ("Projeto", "5-7 dias"),
        ("Homologação", "15 dias"),
        ("Compra", "25 dias"),
        ("Instalação", "2-3 dias"),
        ("Vistoria", "7 dias"),
    ]

    y_start = pdf.get_y() + 5
    w_box = 35
    for i, (nome, prazo) in enumerate(etapas):
        x = 10 + (i * 38)
        pdf.set_xy(x, y_start)
        pdf.set_fill_color(*COR_VERDE)
        pdf.rect(x, y_start, w_box, 20, "F")

        pdf.set_xy(x, y_start + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(255, 255, 255)  # Texto branco
        pdf.multi_cell(w_box, 4, nome, align="C")

        pdf.set_xy(x, y_start + 12)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(w_box, 5, prazo, align="C")

    # ==============================================================================
    # PÁGINA 4: DADOS TÉCNICOS E GRÁFICO MENSAL
    # ==============================================================================
    pdf.add_page()

    # Título
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Características do SFV", ln=True)

    # Tabela Técnica Estilizada (Verde e Cinza alternados como no PDF)
    def linha_tecnica(rotulo, valor):
        pdf.set_font("Helvetica", "", 10)
        pdf.set_fill_color(*COR_VERDE)  # Fundo Verde
        pdf.set_text_color(0, 0, 0)
        pdf.cell(90, 8, rotulo, fill=True, border=0)

        pdf.set_fill_color(*COR_CINZA)  # Fundo Cinza
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, valor, fill=True, border=0, ln=True)

    linha_tecnica("Potência total", f"{dados.get('potencia_kwp', '')} kWp")
    pdf.ln(1)  # Espaço branco fino entre linhas
    linha_tecnica("Nº de Módulos", str(dados.get("num_modulos", "")))
    pdf.ln(1)
    linha_tecnica("Inversor", dados.get("inversor", ""))
    pdf.ln(1)
    linha_tecnica("Geração mensal estimada", f"{dados.get('geracao_mensal', '')} kWh")
    pdf.ln(1)
    linha_tecnica("Área da instalação", f"{dados.get('area_minima', '')} m²")

    pdf.ln(10)

    # GRÁFICO DE GERAÇÃO X CONSUMO
    # Aqui inserimos a imagem gerada pelo Streamlit/Matplotlib
    if "geracao_consumo" in graficos:
        # Assumindo que o gráfico ocupa largura total
        pdf.image(graficos["geracao_consumo"], x=10, w=190)
    else:
        pdf.cell(
            0, 40, "[Gráfico de Geração x Consumo Aqui]", border=1, align="C", ln=True
        )

    pdf.ln(5)

    # Texto de Garantia
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Garantia", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        0,
        5,
        "Os módulos têm garantia de 15 anos contra defeitos e 25 anos de performance (80%).\nInversores: Garantia padrão de 5 a 10 anos.\nInstalação: 2 anos.",
    )

    # ==============================================================================
    # PÁGINA 5: INVESTIMENTO
    # ==============================================================================
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Investimento", ln=True)

    # Tabela de Itens (Usando pdf.table() para facilitar, ou manual para cores específicas)
    # Vamos fazer manual para replicar o estilo de linhas alternadas se necessário,
    # mas o fpdf2 table é ótimo.

    with pdf.table() as table:
        headers = table.row()
        headers.cell("Item")
        headers.cell("Descrição")

        itens_tabela = [
            ("1", "Equipamentos (Módulos, Inversores, Estruturas, Cabos)"),
            ("2", "Projeto de Engenharia"),
            ("3", "Tramitação na Concessionária"),
            ("4", "ART junto ao CREA"),
            ("5", "Instalação e Comissionamento"),
            ("6", "Frete"),
        ]

        for num, desc in itens_tabela:
            row = table.row()
            row.cell(num)
            row.cell(desc)

    pdf.ln(10)

    # Valor Total
    pdf.set_fill_color(*COR_VERDE)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0,
        15,
        f"Valor do Investimento: R$ {dados.get('valor_total', '')}",
        fill=True,
        ln=True,
        align="C",
    )

    pdf.ln(10)

    # Formas de Pagamento
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Formas de pagamento:", ln=True)

    pagamentos = [
        "À Vista (desconto a consultar)",
        "Entrada + Parcelamento",
        "Financiamento Bancário (BV, Santander, etc)",
    ]
    pdf.set_font("Helvetica", "", 10)
    for p in pagamentos:
        pdf.cell(5, 6, "v", ln=0)  # Checkmark simulado
        pdf.cell(0, 6, p, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(
        0,
        5,
        "Não inclusos: Obras civis, içamentos especiais ou adequações na rede interna.",
        ln=True,
    )

    # ==============================================================================
    # PÁGINA 6: FINANCEIRO E FECHAMENTO
    # ==============================================================================
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*COR_VERDE)
    pdf.cell(0, 10, "Retorno do Investimento", ln=True)

    # GRÁFICO FLUXO DE CAIXA
    if "fluxo_caixa" in graficos:
        pdf.image(graficos["fluxo_caixa"], x=10, w=190)
    else:
        pdf.cell(
            0, 50, "[Gráfico Fluxo de Caixa Acumulado]", border=1, align="C", ln=True
        )

    pdf.ln(10)

    # Cards de KPIs (Payback, TIR, Economia)
    # Vamos desenhar 3 caixas lado a lado
    y_kpi = pdf.get_y()
    largura_kpi = 60

    # KPI 1: Payback
    pdf.set_fill_color(*COR_VERDE)
    pdf.rect(10, y_kpi, largura_kpi, 25, "F")
    pdf.set_xy(10, y_kpi + 2)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(largura_kpi, 5, "Payback Estimado", align="C")
    pdf.set_xy(10, y_kpi + 10)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(largura_kpi, 10, dados.get("payback", ""), align="C")

    # KPI 2: Economia 1º Ano
    pdf.set_fill_color(*COR_CINZA)
    pdf.rect(10 + largura_kpi + 5, y_kpi, largura_kpi, 25, "F")
    pdf.set_xy(10 + largura_kpi + 5, y_kpi + 2)
    pdf.cell(largura_kpi, 5, "Economia 1º Ano", align="C")
    pdf.set_xy(10 + largura_kpi + 5, y_kpi + 10)
    pdf.cell(largura_kpi, 10, dados.get("economia_anual", ""), align="C")

    # KPI 3: Nova Conta
    pdf.set_fill_color(*COR_VERDE)
    pdf.rect(10 + (largura_kpi + 5) * 2, y_kpi, largura_kpi, 25, "F")
    pdf.set_xy(10 + (largura_kpi + 5) * 2, y_kpi + 2)
    pdf.cell(largura_kpi, 5, "Nova Conta Estimada", align="C")
    pdf.set_xy(10 + (largura_kpi + 5) * 2, y_kpi + 10)
    pdf.cell(largura_kpi, 10, dados.get("nova_conta", ""), align="C")

    pdf.ln(40)

    # Comparativo Poupança (Opcional, presente no PDF)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Taxa Interna de Retorno (TIR): {dados.get('tir', '99%')}", ln=True)
    pdf.cell(0, 5, "Comparativo Poupança: ~6-8% a.a vs Seu Sistema: ~30% a.a", ln=True)

    pdf.ln(20)

    # Assinatura
    pdf.line(10, pdf.get_y(), 100, pdf.get_y())
    pdf.cell(0, 5, "De acordo", ln=True)
    pdf.cell(0, 5, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)

    # Retorna o PDF como string de bytes para o Streamlit baixar
    return bytes(pdf.output())


# --- Fim do Arquivo de Geração ---
