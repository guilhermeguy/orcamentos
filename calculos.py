# calculos.py
# separando a lógica matemática e financeira do app e do gerador de pdf

import math
import pandas as pd


def calcular_cenario_solar():
    resultados = calcular_cenario_solar(
        consumo=consumo_medio,
        tarifa=tarifa_cemig,
        potencia_kit=potencia_kit,
        custo_total=custo_total_projeto,
        margem=margem_lucro,
    )
