# -*- coding: utf-8 -*-
"""

Use esta classe para negociar usando o modelo treinado usando a classe "treinamento.py". Este modelo é carregado na pasta "Modelos".
"""
from numpy import *
import numpy as np
import pandas as pd
import time

from binance.client import Client
from binance.enums import *

import datetime
import CoreFunctions as cf
from joblib import dump, load

#%%

api_key = '#'
api_secret = '#'

client = Client(api_key, api_secret)

model = load("Models/model.mdl")

firstRun = True
makeTrade = False

state = 0
prevTime = 0

data = []
MLData = []

currentBtc = cf.getCoinBalance(client, 'btc')
print(currentBtc)
currentUSDT = cf.getCoinBalance(client, 'USDT')
print(currentUSDT)

hasToken = False
currentTokenBalance = 0

market = "BTCUSDT"
trade = "BTC"
sellToBuyTransition = True

buyPrice = 0
bestPrice = 0
sinceBest = 0

while(True):
    
    # verifique o carimbo de data e hora, se for diferente, adicione à lista e mude de estado
    if state == 0:
        
        candles = client.get_klines(symbol=market, interval=Client.KLINE_INTERVAL_1HOUR)
        
        if firstRun == True:
            prevTime = datetime.datetime.fromtimestamp(candles[498][0]/ 1e3)
            
            firstRun = False
            makeTrade = False
            for i in range(499):
                data.append(candles[i])
            
        else:
            currTime = datetime.datetime.fromtimestamp(candles[498][0]/ 1e3)
            
            if prevTime != currTime:
                if candles[498] not in data:
                    data.append(candles[498])
                    prevTime = currTime
                    makeTrade = True
                
            else:
                
                makeTrade = False
                
        print(makeTrade)
        state = 1
        
   # Trailing Stoploss a 1% do preço mais alto desde que entrou no comércio. Verificar o valor mais alto a cada 10 segundos ajuda a prevenir contra grandes lixões ou previsões ruins
     #na hora
    if state == 1:

        if hasToken == True:
            try:
                
                prices =  client.get_order_book(symbol=market)
                price = prices['bids'][0][0]
                
                if float(price) > float(bestPrice):
                    
                    bestPrice = price
                    
                elif bestPrice * 0.99 > price:
                    
                    print("Selling")                    
                    
                    sellAmt = cf.getCoinBalance(client, trade)
                    currentBtc = str(sellAmt)
                    qty = ""
                    
                    for q in range(8):
                        qty += currentBtc[q]
                    
                    currentBtc = qty
                    
                    cf.executeSell(client, market, currentBtc)
                    currentTokenBalance = 0
                    hasToken = False
                    sellToBuyTransition = False
                    buyPrice = 0
                    bestPrice = 0
                    sinceBest = 0
                    currentBtc = cf.getCoinBalance(client, 'btc')
                    print("Trailing Stop Trigger")        
                    state = 0
                    time.sleep(10)
                                    
            except Exception as e:
                print(e)
        
        # se o timestamp for diferente, atualizamos o
        if makeTrade == True:
            state = 2
            makeTrade = False
        else:
            state = 0
            time.sleep(10)
            
   # criar dados de recursos usados para fazer previsões
    if state == 2:
        #data = cf.makeTrainingData(data)
        MLData = cf.FeatureCreation(data)
        print(1)
        state = 3
    
    #fazer negócios com base no sinal previsto
    if state == 3:
        
        pred = model.predict_proba(MLData[len(MLData)-1:len(MLData)])
        print(pred[0])
        signal = np.argmax(pred[0])
        print(signal)
        
        #Se o modelo comprar, a compra no mercado será mantida, desde que não tenhamos o BTC no momento e contenha um sinal de venda anteriormente,
         #para um sinal de compra agora
        if signal == 1:
            print("Buy Signal")
            
            if hasToken == False and sellToBuyTransition == True:
                try:
                    print("Buying")
                    currentUSDT = cf.getCoinBalance(client, 'USDT')
                    
                    prices =  client.get_order_book(symbol=market)
                    price = prices['asks'][0][0]
                    buyPrice = price
                    bestPrice = buyPrice
                    buyAmt =  currentUSDT/float(price)
                    buyAmt = str(buyAmt)
                    qty = ""
                    for q in range(8):
                        qty += buyAmt[q]
                    
                    buyAmt = qty
                    cf.executeBuy(client, market, buyAmt)
                    currentTokenBalance = buyAmt
                    hasToken = True
                    
                    state = 0
                    time.sleep(10)
                    
                except Exception as e:
                    print(e)
            else:
                state = 0
                time.sleep(10)
        
        #Só vende quando na verdade temos BTC para vender no mercado!
        if signal == 0:
            print("Sell Signal")
            
            if sellToBuyTransition == False:
                sellToBuyTransition = True
                
            if hasToken == True:
                try:
                    print("Selling")                    
                    currentBtc = cf.getCoinBalance(client, 'BTC') 
                    
                    currentBtc = str(currentBtc)
                    qty = ""
                    
                    for q in range(8):
                        qty += currentBtc[q]
                    
                    currentBtc = qty
                    cf.executeSell(client, market, currentBtc)
                    currentTokenBalance = 0
                    hasToken = False
                    
                    state = 0
                    time.sleep(10)
                    
                except Exception as e:
                    print(e)
            else:
                state = 0
                time.sleep(10)
                
