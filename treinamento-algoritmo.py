# -*- coding: utf-8 -*-
"""

Use esta classe para treinar um modelo básico de aprendizado de máquina. Ou modifique-o para incorporar seus próprios modelos de aprendizado de máquina ou pipelines
usando outras bibliotecas como XGBoost, Keras ou estratégias como Spiking Neural Networks!

"""

import numpy as np
from numpy import *
import pandas as pd

from binance.client import Client
from binance.enums import *


import CoreFunctions as cf

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from joblib import dump, load

#Você não precisa digitar sua chave / segredo para obter dados da troca, eles são necessários apenas para transações na classe TradingBot.py.
api_key = '#'
api_secret = '#'
client = Client(api_key, api_secret)

candles = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "01 Jan, 2019", "10 Jul, 2020")

#Converta os dados brutos da troca em um formulário mais amigável, com alguma criação básica de recursos
x = cf.FeatureCreation(candles)

#Criar nossas metas
y = cf.CreateTargets(candles,1)

#remove os principais elementos dos recursos e destinos - isso é para determinados recursos que não são compatíveis com os principais
# por exemplo, SMA27 teria 27 entradas que seriam incompatíveis / incompletas e precisariam ser descartadas
y = y[94:]
x = x[94:len(candles)-1]

# produzir conjuntos, evitando sobreposições!
# dados são separados temporariamente em vez de aleatoriamente
# isso evita que o modelo aprenda coisas que ele não saberia - também conhecido como vazamento - o que pode nos dar modelos de falsos positivos
trny = y[:9999]
trnx = x[:9999]

# O conjunto de validação não é usado neste modelo inicial, mas deve ser usado se você estiver usando outras bibliotecas que suportam parada antecipada.
valy = y[10000:12999]
valx = x[10000:12999]

tsty = y[13000:]
tstx = x[13000:]

model = GradientBoostingClassifier() 
model.fit(trnx,trny)

preds = model.predict(tstx)

# Alguns testes básicos para que saibamos o desempenho do nosso modelo em dados invisíveis - "modernos".
# Ajuda com recursos de ajuste fino e parâmetros do modelo
accuracy = accuracy_score(tsty, preds)
mse = mean_squared_error(tsty, preds)

print("Accuracy = " + str(accuracy))
print("MSE = " + str(mse))

falsePos = 0
falseNeg = 0
truePos = 0
trueNeg = 0
total = len(preds)

for i in range(len(preds)):
    
    if preds[i] == tsty[i] and tsty[i] == 1:
        truePos +=1
        
    elif preds[i] == tsty[i] and tsty[i] == 0:
        trueNeg +=1
        
    elif preds[i] != tsty[i] and tsty[i] == 1:
        falsePos +=1
        
    elif preds[i] != tsty[i] and tsty[i] == 0:
        falseNeg +=1
        
print("False Pos = " + str(falsePos/total))
print("False Neg = " + str(falseNeg/total))
print("True Pos = " + str(truePos/total))
print("True Neg = " + str(trueNeg/total))

# Qual a importancia dos recursos - ajuda na seleção e criação de recursos!
results = pd.DataFrame()
results['names'] = trnx.columns
results['importance'] = model.feature_importances_
print(results.head)


# salve nosso modelo no sistema para uso no bot
dump(model, open("Models/model.mdl", 'wb'))








