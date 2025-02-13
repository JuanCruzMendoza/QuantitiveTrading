"""
En este script encontraremos un algoritmo evolutivo
"""
import numpy as np
import backtrader as bt
import random
from tkinter import simpledialog
import matplotlib.pyplot as plt

class Genetic:
    def __init__(self):
        self.size = simpledialog.askinteger("Tamaño poblacion inicial", "Ingrese el tamaño de la poblacion inicial:")
        self.parametersCount = simpledialog.askinteger("Cantidad de parametros", "Indique cuantos parametros tiene su estrategia:")
        self.ranges = self.rangesParameters()
        self.elitistPercentage = simpledialog.askinteger("Elitista", "Ingrese el porcentaje elitista que quiere seleccionar: ")
        self.stocasticPercentaje = simpledialog.askinteger("Estocastico", "Ingrese el porcentaje estocastico que quiere seleccionar: ")
        self.mutationRate = simpledialog.askfloat("Rate mutation", "Ingrese rartio de mutacion: ")
        self.comision = simpledialog.askfloat("Comision", "Ingrese la comision")
        self.politic = simpledialog.askstring("Criterio", "R: ratio de sharpe\nD: drowdon\nP: profit")  
        self.maxGeneraciones = simpledialog.askinteger("Generaciones", "Ingrese el maximo de generaciones: ")

    def rangesParameters(self):
        #creamos lista de rangos en tuplas para los parametros
        ranges = []
        for i in range(self.parametersCount):
            tupla = []*2
            parametro = 0
            for _ in range(2):
                # Pedimos los parámetros de las tuplas de a uno
                parametro = simpledialog.askinteger("Parametro", f"Agregue límite del parámetro {i+1}:")
                tupla.append(parametro) # Agregamos los parámetros a una mini lista
            tupla = tuple(tupla) # Convertimos la mini lista en una tupla
            #print("tupla: ", tupla)
            ranges.append(tupla) # Agregamos la tupla a la lista rangos
        print("rangos: ", ranges)
        return ranges

    def roulette(self, stocasticCount, resultFitness):
        profits = [netProfit for individual, netProfit in resultFitness]
        #Muevo los profits para que todos sean mayores que 0, pero mantengan la proporcio   
        if min(profits) < 0:
            minProfit = min(profits) #encuentro el minimo de todos los profits
            print(minProfit)
            for i in range(len(profits)): #recorro los profits modificandolos para que todos sean >0
                profits[i] = profits[i] - minProfit 

        profitTotal = sum(profits)
        if profitTotal == 0:
            profitTotal = 1  # Para evitar la división por cero

        #Calculamos la frecuencia relativa de cada profit
        frecuencies = []
        frecuencies = [(individual, netProfit/profitTotal) for individual, netProfit in resultFitness]

        # Calcular la frecuencia acumulada
        cumulatedFrecuency = []
        cumulated = 0
        cumulatedFrecuency = [
            (individual, (cumulated := cumulated + relativityFrecuency)) 
            for individual, relativityFrecuency in frecuencies
        ]

        #seleccionamos los individuos de manera aleatoria
        slected = []
        i = 0
        for i in range(0, stocasticCount):
            randomNumber = np.random.rand() #numero entre 0 y 1 que nos ayudara a seleccionar nuestro individuo
            for individual, cumulated in cumulatedFrecuency:
                if randomNumber <= cumulated:
                    slected.append(individual)
                    break
        return slected

    #funcion que selecciona los individuos con mejores fitness
    def bestAverages(self, elitistCount, resultFitness):
        profits = []
        profits = [netProfit for individual, netProfit in resultFitness]
        fitnessAverage = sum(profits)/len(profits)

        bigest = 0
        bigest = sum(1 for resultado in profits if resultado > fitnessAverage)
        
        elitistCount = bigest if bigest < elitistCount else elitistCount
        
        bests = []
        bests = [individual for individual, netProfit in resultFitness if netProfit > fitnessAverage and individual not in bests]
        
        bests.sort(reverse=True) #reverse=True .sort default ordena de menor a mayor, el True hace que ordene de mayor a menor
        bests = bests[:elitistCount] #seleccionamos de los mejores la cantidad de individuos elitistas. Son los mejores porque "mejores" esta ordenado de mayor a menor   
        return bests

    def toDictionary(self, individual):
        parameters = {}
        parameters = {'param'+str(i): individual[i] for i in range(0, len(individual))}
        print("parametros: ", parameters)
        return parameters

    def startPopulation(self, size, ranges):
        population = []
        population = [[np.random.randint(minValue, maxValue) for (minValue, maxValue) in ranges] for i in range(size)]
        return population

    def dataBacktrader(self, data):
        print("entramos a databacktrader")
        # Crear una clase personalizada para el DataFeed. Esta clase mapea las columnas del df para que backtrader interprete todo correctamente
        class CustomPandasData(bt.feeds.PandasData): #Normalizamos los datos
            params = (
                ('datetime', None),  # `datetime` será usado como índice, así que se deja como None
                ('open', data.columns[0]),
                ('high', data.columns[1]),
                ('low', data.columns[2]),
                ('close', data.columns[3]),
                ('volume', data.columns[4]),
                ('openinterest', None),
            )
        # Convertir el DataFrame a DataFeed
        datafeed = CustomPandasData(dataname=data) #Decimos que data va a ser de la clase CustomPandasData para normalizar los datos y que backtrader reciba lo que espera
        print("devolvi el datafeed")
        return datafeed
    
    def fitness(self, strategy, data, poblacion, comision, politic):
        results = []
        for individual in poblacion:
            cerebro = bt.Cerebro()
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Minutes, compression=1, annualize=True)

            datafeed = self.dataBacktrader(data)
            cerebro.adddata(datafeed)
            cerebro.broker.setcash(10000)
            cerebro.broker.setcommission(commission=comision)  # Por ejemplo, una comisión del 0.1%
            parameters = self.toDictionary(individual)
            cerebro.addstrategy(strategy, **parameters) #Los parametros debemos pasarlos en forma de diccionario
            # Agregamos los analizadores: analizador de Trades, Drawdown y SharpeRatio
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='sharperatio_a', riskfreerate=0.02, convertrate=True, timeframe=bt.TimeFrame.Days)
        
            result = cerebro.run()

            if politic == "R":
                print("optimizamos por Ratio de Sharpe")
                # Obtener el Sharpe Ratio
                sharpeRatio = result[0].analyzers.sharperatio_a.get_analysis()
                sharpeValue = sharpeRatio['sharperatio']  # Usar 0 como valor por defecto
                print("ratio de sharpe: ", sharpeValue)
                res = (individual, sharpeValue)
            
            elif politic == "D":
                print("optimizamos por Drowdon")
                # Obtener el analizador de drawdown
                drawdownAnalyzer = result[0].analyzers.drawdown.get_analysis()
                maxDrawdown = drawdownAnalyzer.max.drawdown 
                drawdonInverso = 100 - maxDrawdown # Calculamos el inverso para mantener logica de maximizacion
                print("Drawdon: ", maxDrawdown)
                print("Inverso: ", drawdonInverso)
                res = (individual, drawdonInverso)

            
            elif politic == "P":
                print("optimizamos por profit")
                # Acceder al analyzer desde los resultados
                tradeAnalyzer = result[0].analyzers.trades.get_analysis()
                netProfit = tradeAnalyzer['pnl']['net']['total'] 
                print("Profit: ", round(netProfit, 2))
                res = [individual, round(netProfit, 2)]
     
            results.append(tuple(res))
        return results        

    def selection(self, elitistPercentage, stocasticPercentage, population, resultFitness):
        #print("seleccion")
        """
        En seleccion haremos lo siguiente:
        - Tomaremos un porcentaje de la poblacion inicial.
            - Este porcentaje se va a componer de:
                - Mejores que el promedio (parte elitista)
                - Un grupo de seleccion por ruleta (nos asegura diversidad y continuar explorando)
        """
        elitistCount = int((elitistPercentage*len(population))/100) #defino la cantidad de individuos elitistas (lo que mellega al principio esun porcentaje)
        stocasticCount = int((len(population)*stocasticPercentage)/100) #defino la cantidad de individuos estocasticos
        elitistPopulation = self.bestAverages(elitistCount, resultFitness)

        for individual, resultado in resultFitness:
            if individual in elitistPopulation:
                resultFitness.remove((individual, resultado))
        
        stocasticPopulation = self.roulette(stocasticCount, resultFitness)
        
        # Crear la población restante eliminando los elitistas y estocásticos
        remainingPopulation = [individual for individual in population if individual not in elitistPopulation and individual not in stocasticPopulation]

        poblacion_hijos = self.cruzamiento(remainingPopulation, len(population)-len(elitistPopulation)-len(stocasticPopulation))
        #mi cantidad de hijos esta dada porpoblacion - elitistas - esocasticos

        print("poblacion estocastica: ", stocasticPopulation)
        print("cant  de estocasticos: ", len(stocasticPopulation))
        print("poblacion elitista: ", elitistPopulation)
        print("cant de  elitistas: ", len(elitistPopulation))
        print("canthijos:", len(poblacion_hijos))

        nextPopulation = elitistPopulation + stocasticPopulation + poblacion_hijos
        return nextPopulation

    def cruzamiento(self, stocasticPopulation, childCount):
        #obligamos a que siempre podamos hacer 2 hijos para que no sobren genes de los padres
        if childCount%2 != 0:
            childCount = childCount+1
        
        #mezclo de manera aleatoria la poblacion 
        random.shuffle(stocasticPopulation)
        childs = []
        for i in range(0, childCount//2):
            #selecciono los padres
            individual1 = np.random.randint(0, len(stocasticPopulation))
            individual2 = np.random.randint(0, len(stocasticPopulation))

            while individual1 == individual2: #si selecciona a los mismos individuos, entonces vuelve a seleccionar el 2
                individual2 = np.random.randint(0, len(stocasticPopulation))
            
            individual1 = stocasticPopulation[individual1]
            individual2 = stocasticPopulation[individual2]
            
            #Seleccionamos donde cortar
            cut1 = np.random.randint(0, len(individual1))
            cut2 = np.random.randint(0, len(individual2))

            while cut1 > cut2: # verifico que el corte 1 sea antes que el corte 2
                cut2 = np.random.randint(0, len(individual1))

            #creamos los hijos con los pedazos de los padres. (Un hijo es el inverso del otro)
            child1 = individual1[:cut1] + individual2[cut1:cut2] + individual1[cut2:]
            childs.append(child1)
            child2 = individual2[:cut1] + individual1[cut1:cut2] + individual2[cut2:]
            childs.append(child2)

        return childs

    def mutation(self, mutationRate, population, rangos):
        mutationRate = mutationRate*1000
        for individual in population:
            number = np.random.randint(0,1000)
            if number < mutationRate:
                gen = np.random.randint(0, len(individual))
                individual[gen] = np.random.randint(rangos[gen][0], rangos[gen][1]) #rangos[gen][0], rangos[gen][1] (son la tupla con el rango deese parametro)
        
        return population

    def envolve(self, strategy, data):
        #creamos la poblacion inicial
        startPopulation = self.startPopulation(self.size, self.ranges)
        print("cant individuospoblacion inicial: ", startPopulation)
        
        generaciones = 0
        resultFitness = []
        bestGlobalIndividual = [None, None]  # Almacena el mejor individuo general


        while (generaciones <= self.maxGeneraciones):
            if generaciones == 0: #si estamos en la primera generacion mandamos a fitness a la poblacion inicial  
                #evaluamos la aptitud de cada individuo (fitness)
                resultFitness = self.fitness(strategy, data, startPopulation, self.comision, self.politic)
            else: #si no estamos en la primera poblacion, mandamos a fitness a la poblacion mutada (pblacion final de la iteracion anterior)
                #evaluamos la aptitud de cada individuo (fitness)
                startPopulation = mutatedPopulation #cambiamos la  poblacion inicial por la poblacion mutada
                resultFitness = self.fitness(strategy, data, startPopulation, self.comision, self.politic)
                print("ya hice el fitness de la nueva poblacion")
            
            #Seleccionamos de nuestra poblacion
            nextPopulation = self.selection(self.elitistPercentage, self.stocasticPercentaje, startPopulation, resultFitness)
            # Mutamos nuestra poblacion
            mutatedPopulation = self.mutation(self.mutationRate, nextPopulation, self.ranges)

            bestIndividual = [None, None]
            #recorremos los resultados  del fitness en busca de un individuo apto   
            for individual, fitness in resultFitness:
                if bestIndividual[1] is None or fitness > bestIndividual[1]: #vemos si todavia no se cargo ningun fitness y le cargamois uno. Tambien verificamos y actualizamos si hay un fitness mejor
                    bestIndividual = individual, fitness #obtenemos el mejor individuo de una poblacion

                    #best = [individuo, fitness] #borrar
            
            print("generacion: ", generaciones)
            print("Mejor individuo: ", bestIndividual)

            #verificamos si el mejor individuo de las generaciones pasadas es peor que el mejor de la generacion actual
            if bestGlobalIndividual[1] is None or bestGlobalIndividual[1] < bestIndividual[1]:
                bestGlobalIndividual = bestIndividual

            generaciones += 1 #actualizo la generacion

        print("El mejor es: ", bestGlobalIndividual)
        #print("Resultado del mejor: ", best) #borrar
        return self.toDictionary(bestGlobalIndividual[0])


#... ESTA SECCION ES PARA PROBAR EL ALGORITMO SOLO ...# 
"""
if __name__ == "__main__":
    probador = Probador()
    algoritmo = Evolution()
    data = probador.get_data()
    estrategia = probador.get_strategy()
    algoritmo.envolve(estrategia, data)
"""