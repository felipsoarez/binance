"""
Use essa classe como seu pipeline, use-a para todas as suas funcionalidades de manipulação de dados / criação de recursos.
As funções aqui são usadas nas classes de bot e treinamento!
"""
from binance.client import Client
import pandas as pd 
import numpy as np

#Obter o saldo de uma moeda especificada
def getCoinBalance(client, currency):
    balance = float(client.get_asset_balance(asset=currency)['free'])
    return balance

#Compra no mercado
def executeBuy(client, market, qtyBuy):

    order = client.order_market_buy(symbol=market,quantity=qtyBuy)

#Venda no mercado
def executeSell(client, market, qtySell):

    order = client.order_market_sell(symbol=market, quantity=qtySell)

#formata os dados corretamente para uso posterior
def CreateOpenHighLowCloseVolumeData(indata):

    out = pd.DataFrame()

    d = []
    o = []
    h = []
    l = []
    c = []
    v = []
    for i in indata:
        #print(i)
        d.append(float(i[0]))
        o.append(float(i[1]))
        h.append(float(i[2]))
        c.append(float(i[3]))
        l.append(float(i[4]))
        v.append(float(i[5]))

    out['date'] = d
    out['open'] = o
    out['high'] = h
    out['low'] = l
    out['close'] = c
    out['volume'] = v

    #print(out)

    return out

#Esta é a principal função para criação e manipulação de recursos. Modifique-o adicionando suas próprias funções e criação de recursos.
# prehaps tente usar bibliotecas de análise técnica para RSI ou
# Dados de sentimentos de bitfinex ou dados de medo e ganância
def FeatureCreation(indata):

    convertedData = CreateOpenHighLowCloseVolumeData(indata)
    FeatureData = pd.DataFrame()
    FeatureData['o'] = convertedData['open']
    FeatureData['h'] = convertedData['high']
    FeatureData['l'] = convertedData['low']
    FeatureData['c'] = convertedData['close']
    FeatureData['v'] = convertedData['volume']
    candleRatios(FeatureData)
    StepData(FeatureData['c'],FeatureData)
    GetChangeData(FeatureData)

    return FeatureData

# Crie metas para o nosso modelo machine learning. Isso é feito prevendo se o preço de fechamento da próxima vela será
# maior ou menor que o atual.
def CreateTargets(data, offset):

    y = []


    for i in range(0, len(data)-offset):
        current = float(data[i][3])
        comparison = float(data[i+offset][3])

        if current<comparison:
            y.append(1)

        elif current>=comparison:
            y.append(0)

    return y

# EXEMPLOS DE RECURSOS
# Calcular a alteração nos valores de uma coluna
def GetChangeData(x):

    cols = x.columns

    for i in cols:
        j = "c_" + i

        try:
            dif = x[i].diff()
            x[j] = dif
        except Exception as e:
            print(e)

# EXEMPLOS DE RECURSOS
# Calcular a variação percentual entre esta barra e as barras x anteriores
def ChangeTime(x, step):

    out = []

    for i in range(len(x)):
        try:
            a = x[i]
            b = x[i-step]

            change = (1 - b/a)
            out.append(change)
        except Exception as e:
            out.append(0)

    return out

# EXEMPLOS DE RECURSOS
# Automatize a criação de alterações percentuais para 48 velas.
def StepData(x, data):

    for i in range(1,48):

        data[str(i)+"StepDifference"] = ChangeTime(x, i)


# EXEMPLOS DE RECURSOS
# Recursos que levam em conta as relações entre os valores da vela
def candleRatios(data):
    data['v_c'] = data['v'] / data['c']
    data['h_c'] = data['h'] / data['c']
    data['o_c'] = data['o'] / data['c']
    data['l_c'] = data['l'] / data['c']

    data['h_l'] = data['h'] / data['l']
    data['v_l'] = data['v'] / data['l']
    data['o_l'] = data['o'] / data['l']

    data['o_h'] = data['o'] / data['h']
    data['v_h'] = data['v'] / data['h']

    data['v_o'] = data['v'] / data['o']
