# calculos.py
# separando a lógica matemática e financeira do app e do gerador de pdf

import math
import pandas as pd


def consumo_medio(df_consumo: pd.DataFrame, dict_disponibilidades: dict):
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


def geracao_mensal(
    potencia_kit: float, ganho_perda: float, potencia_referencia: float
) -> float:
    """Calcula a geração média mensal com base em uma geração de referencia. Como referencia se considera uma geração de 1000 kWh/mês para a 'potencia_referencia.
    Ex. 7,8 kWp geram 1000 kWh/mês na inclinação 0° na região de Belo Horizonte. Estimativa conservadora.
    """
    geracao_mensal = ((potencia_kit * 1000) / potencia_referencia) * (
        (ganho_perda / 100) + 1
    )
    return geracao_mensal


def custo_projeto(
    potencia_kit: float, df_projeto: pd.DataFrame, adicional_projeto: float
) -> float:
    mask = (potencia_kit > df_projeto["de"]) & (potencia_kit <= df_projeto["ate"])
    preco_projeto = df_projeto.loc[mask, "preco (R$)"].iloc[0]
    return (1 + adicional_projeto / 100) * preco_projeto


def custo_total(dict_custos: dict) -> dict:
    dict_return = {}
    custo_proj = custo_projeto(
        dict_custos["potencia_kit"],
        dict_custos["df_projeto"],
        dict_custos["adicional_projeto"],
    )
    df_preco = dict_custos["df_preco"]
    df_preco["valor_total"] = df_preco["Qtd"] * df_preco["Valor Unit (R$)"]
    sub_total = df_preco["valor_total"].sum() + custo_proj
    lucro_inovasol = (dict_custos["lucro_inovasol"] / 100) * sub_total
    comissao = (dict_custos["comissao"] / 100) * sub_total
    valor_impostos = dict_custos["df_impostos"]["Valor"].sum() / 100
    dict_return["total_nf"] = (sub_total + lucro_inovasol + comissao) / (
        1 - valor_impostos
    )
    dict_return["total_projeto"] = dict_return["total_nf"] + dict_custos["custo_kit"]
    return dict_return


def retorno_financeiro(dict_custos: dict, tma: float, prazo_vpl: int) -> dict:
    dict_retorno = {}
    return dict_retorno


if __name__ == "__main__":
    print(
        "Geracao mensal para kit de 4 kWp, 5 % de perda e 7,8 kwp de potencia de referencia: "
    )
    print(geracao_mensal(4, 5, 7.8))
