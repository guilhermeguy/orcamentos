# calculos.py
# separando a lógica matemática e financeira do app e do gerador de pdf

import math
import pandas as pd


def consumo_medio(df_consumo, dict_disponibilidades):
    consumo1 = df_consumo["imv1"].mean(skipna=False)
    consumo2 = df_consumo["imv2"].mean(skipna=False)
    consumo3 = df_consumo["imv3"].mean(skipna=False)
    consumo4 = df_consumo["imv4"].mean(skipna=False)

    if consumo2 + consumo3 + consumo4 < 1:
        return consumo1 - dict_disponibilidades["disp_imv1"]
    else:
        return (
            consumo1
            + consumo2
            - dict_disponibilidades["disp_imv2"]
            + consumo3
            - dict_disponibilidades["disp_imv3"]
            + consumo4
            - dict_disponibilidades["disp_imv4"]
        )


def geracao_mensal(potencia_kit, ganho_perda, potencia_referencia):
    """Calcula a geração média mensal com base em uma geração de referencia. Como referencia se considera uma geração de 1000 kWh/mês para a 'potencia_referencia.
    Ex. 7,8 kWp geram 1000 kWh/mês na inclinação 0° na região de Belo Horizonte. Estimativa conservadora.
    """
    geracao_mensal = ((potencia_kit * 1000) / potencia_referencia) * (
        (ganho_perda / 100) + 1
    )
    return geracao_mensal


def custo_projeto():
    pass


def custo_total():
    pass


if __name__ == "__main__":
    print(
        "Geracao mensal para kit de 4 kWp, 5 % de perda e 7,8 kwp de potencia de referencia: "
    )
    print(geracao_mensal(4, 5, 7.8))
