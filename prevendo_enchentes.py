# -*- coding: utf-8 -*-
import MySQLdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model,svm
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier
import os
import csv
from itertools import product 
from sklearn.linear_model import LogisticRegression, LinearRegression
import time
import json
from calculos import AjusteCurva
from matplotlib.pyplot import step, xlim, ylim, show
from sklearn.metrics import r2_score
import os, time, shutil, sys
from collections import OrderedDict



class MachineLearning:
    def get_data(self,file_name):
            '''
            Método que separa a metade do csv para treinamento e a outra para testar as predições.
            Utiliza três variaveis(temperatura minima, preciptação e velocidade do vento) e o boolean de chuva.
            '''
            data = pd.read_csv(file_name)

            

            data = data.iloc[np.random.permutation(len(data))]
            climate_data_fit = []
            flood_data_fit = []
            #Dados da primeira linha até 1373
            for climate_data,flood in zip(data['json_data'],data['flood']):
                #import ipdb;ipdb.set_trace()
                #if flood==1:
                x = climate_data.replace("'",'"')
                try:
                    json_after = json.loads(x)
                    if json_after.get('history'):
                        json_dailly = json_after['history']['dailysummary']
                        if json_dailly and json_dailly[0]['mintempm'] != '-55573':
                            climate_data_fit.append(climate_data)
                            flood_data_fit.append(flood)   
                except Exception as e:
                    print(str(e))
            return climate_data_fit,flood_data_fit
    def calculando_ajuste_curva(self,list_var,content):
        dict_result = {}
        list_x = []
        list_y = []
        for json_data in content:
            try:        
                json_data = json_data.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
               
                if json_dailly != []:
                    try:
                        for key in json_dailly[0].keys():
                            if key in list_var:
                                #print(key)
                                try:
                                    param = float(json_dailly[0][key]) if json_dailly[0][key] != '-999' else 0
                                except:
                                    param = 0
                                if param == '':
                                    param = 0
                                
                                if key == list_var[0]:
                                    list_x.append(param)
                                if key == list_var[1]:
                                    list_y.append(param)
                        
                    except Exception as e:
                        print(e)
                        import ipdb;ipdb.set_trace()
                    
            except:
                pass
        # plt.plot(list_x, list_y,'ro')
        # #plt.axis([0,50,0,100])
        # plt.show()  


        #import ipdb;ipdb.set_trace()   
        b0,b1,sum_y_square, sum_y = AjusteCurva.modelo_mmq(list_x,list_y)

        desvio = AjusteCurva.desvio(b0,b1,list_x,list_y)

        coeficiente = AjusteCurva.coeficiente_determinacao(desvio,sum_y_square,sum_y,len(list_x))

        variancia = AjusteCurva.variancia_residual(desvio,len(list_x))
        lista_string = [str(list_var),desvio,coeficiente,variancia]
        

        return lista_string
   
    def treinamento():
        # Open database connection
        db = MySQLdb.connect("localhost","root","root","flood_db" )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        list_all = []
        list_flood = []
        cursor.execute("select * from data_climate where json_data is not Null order by id_event;")
        data_ = list(cursor.fetchall())
        count = 0
        for dt in data_[:44582]:
            try:
                json_data = dt[3]
                flood = dt[4]
                
                json_data = json_data.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                list_temp = []
                # if json_dailly:
                #     try:
                if json_dailly != []:
                    try:
                        for key in json_dailly[0].keys():
                            #import ipdb;ipdb.set_trace()
                            #if key in ('maxtempm','mintempm','minhumidity','maxhumidity','maxpressurei','minpressurem','maxwspdi','precipi'):
                            if key in ('mintempm','minhumidity','minpressurem','maxwspdi','precipi'):
                                #print(key)
                                try:
                                    param = float(json_dailly[0][key])
                                except:
                                    param = 0
                                if param == '':
                                    param = 0
                                list_temp.append(param)
                        list_flood.append(float(flood))        
                        #print(list_temp)
                    except Exception as e:
                        print(e)
                        import ipdb;ipdb.set_trace()
                    #import ipdb;ipdb.set_trace()
                    list_all.append(list_temp)
            except:
                pass

        #model = DecisionTreeClassifier()
        #model = KNeighborsClassifier()
        #model = svm.SVC()
        #model = GaussianNB()
        model = LogisticRegression()

        nome_algoritmo = model.__class__.__name__

        model.fit(np.array(list_all), np.array(list_flood))
        #import ipdb;ipdb.set_trace()
        result = []
        cont = 30001
        num = 0


        list_all = []
        list_flood = []
        flood = ''
        json_data = ''
        json_dailly = ''
        json_content = ''
        param = ''
        list_temp = []

        for dt in data_[44582:]:

            try:
                json_data = dt[3]
                flood = dt[4]
                
                json_data = json_data.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                list_temp = []
                # if json_dailly:
                #     try:
                if json_dailly:
                    try:
                        for key_ in json_dailly[0].keys():
                            #import ipdb;ipdb.set_trace()
                            if key_ in ('mintempm','minhumidity','minpressurem','maxwspdi','precipi'):
                                try:
                                    param = float(json_dailly[0][key_])
                                except:
                                    param = 0
                                if key_ == '':
                                    param = 0
                                list_temp.append(param)
                                #print(list_temp)
                        list_flood.append(float(flood))        
                    # print(list_temp)
                    except Exception as e:
                        print(e)
                        import ipdb;ipdb.set_trace()
                if list_temp:
                    predicted = model.predict(np.array([list_temp]))
                    result.append([cont,flood,predicted[0]]) # .append(nº da linha .csv, boolean real, boolean previsto)

                num+=1
                cont+=1
            except Exception as e:
                print(str(e))
                pass

        return result,nome_algoritmo

    def treinamento_csv(self,data,flood):
        cont = 0
        list_all = []
        list_flood = []
        count = 0
        num_train = int((len(data)*0.8))
        #import ipdb;ipdb.set_trace()
        num_test = num_train+1
        #import ipdb;ipdb.set_trace()
        for dt in data[:num_train]:
            try:
                json_data = dt.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                list_temp = []
                # if json_dailly:
                #     try:
                if json_dailly != []:
                    try:
                        for key in json_dailly[0].keys():
                            #import ipdb;ipdb.set_trace()
                            #if key in ('maxtempm','mintempm','minhumidity','maxhumidity','maxpressurei','minpressurem','maxwspdi','precipi'):
                            #if key in ('mintempm','minhumidity','minpressurem','maxwspdi','precipi'):
                            if key in ('minpressurem', 'precipi'):
                                #print(key)
                                try:
                                    param = float(json_dailly[0][key])
                                except:
                                    param = 0
                                if param == '':
                                    param = 0
                                list_temp.append(param)
                        list_flood.append(float(flood[cont]))  
                        
                        cont+=1
                    except Exception as e:
                        print(e)
                        import ipdb;ipdb.set_trace()
                    #import ipdb;ipdb.set_trace()
                    list_all.append(list_temp)
                    #print(list_all)
            except:
                pass

        #model = DecisionTreeClassifier()
        #model = KNeighborsClassifier()
        #model = svm.SVC()
        #model = GaussianNB()
        #model = LogisticRegression()

        nome_algoritmo = model.__class__.__name__

        model.fit(np.array(list_all), np.array(list_flood))
        #import ipdb;ipdb.set_trace()
        result = []
        
        num = 0

        result = []
        list_all = []
        list_flood = []
        
        json_data = ''
        json_dailly = ''
        json_content = ''
        param = ''
        list_temp = []
        acertos = 0
        erros = 0
        cont = 0
        cont_itens = num_test
        for dt in data[num_test:]:

            try:
                
                
                json_data = dt.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                list_temp = []
                # if json_dailly:
                #     try:
                if json_dailly:
                    try:
                        for key_ in json_dailly[0].keys():
                            #import ipdb;ipdb.set_trace()
                            #if key_ in ('mintempm','minhumidity','minpressurem','maxwspdi','precipi'):
                            if key_ in ('minpressurem', 'precipi'):
                                try:
                                    param = float(json_dailly[0][key_])
                                except:
                                    param = 0
                                if key_ == '':
                                    param = 0
                                list_temp.append(param)
                                #print(list_temp)
                        
                    except Exception as e:
                        print(e)
                        #import ipdb;ipdb.set_trace()
                print(list_temp)
                if list_temp:
                    #import ipdb;ipdb.set_trace()
                    #predicted = model.predict(np.array([list_temp]))
                    predicted
                    if predicted == flood[cont]:
                        acertos +=1
                    else:
                        #import ipdb;ipdb.set_trace()
                        erros +=1

                    result.append([cont_itens,flood[cont],predicted[0]]) # .append(nº da linha .csv, boolean real, boolean previsto)
                #import ipdb;ipdb.set_trace()
                num+=1
                cont+=1
                cont_itens+=1
            except Exception as e:
                print(str(e))
                pass

        return result,nome_algoritmo,acertos,erros
  

    def calcular_ajustes_curva_csv(self):
        #for _,_,arquivo in os.walk('/home/lucas-desenv/workspace-machine/machine-learning/data_bases/America/'):
        for _,_,arquivo in os.walk('/home/lucas/workspace-ml/machine-learning/data_bases/America/'):
            list_param = ['mintempm','minhumidity','minpressurem','maxwspdi','precipi']
            list_combinado = list(product(list_param,repeat=2))
            for name_arquivo in arquivo:
                #import ipdb;ipdb.set_trace()
                content_data = ''
                try:
                    content_data,flood = self.get_data('data_bases/America/'+str(name_arquivo))
                except Exception as e:
                    print(str(e))
                    print(name_arquivo) 
                #import ipdb;ipdb.set_trace()      
                lista_final = []
                nome_arquivo_resultado = str('ajuste_curva/'+name_arquivo.replace(".csv","")+'_ajuste_curva.csv')
                with open(nome_arquivo_resultado, 'w') as csvfile:
                    fieldnames = ['variaveis', 'desvio','coeficiente','variancia']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()    
                    for dupla in list_combinado:
                        print(dupla)
                        resultado = self.calculando_ajuste_curva(dupla,content_data)
                        writer.writerow({'variaveis': resultado[0],'desvio': resultado[1],'coeficiente': resultado[2],'variancia': resultado[3]})

    def get_model_mmq(self,x,y):
            b0,b1,sum_y_square, sum_y = AjusteCurva.modelo_mmq(x,y)

            desvio = AjusteCurva.desvio(b0,b1,x,y)

            coeficiente = AjusteCurva.coeficiente_determinacao(desvio,sum_y_square,sum_y,len(x))

            variancia = AjusteCurva.variancia_residual(desvio,len(x))

            print(desvio, coeficiente, variancia)
            return b0,b1

    def treinando_variaveis(self,variaveis,data,flood):
        cont = 0
        list_all = []
        list_flood = []
        count = 0

        num_train = int((len(data)*0.8))
        #import ipdb;ipdb.set_trace()
        num_test = num_train+1
        #import ipdb;ipdb.set_trace()
        parametros_1 = ''
        parametros_2 = ''
        flood_fit = []
        parametros_treinamento = []
        for dt in data[:num_train]:
            try:

                json_data = dt.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                # parametros_1 = []
                # parametros_2 = []
                
                if json_dailly != []:
                    try:
                        #import ipdb;ipdb.set_trace()
                        for key in json_dailly[0].keys():
                            if key in variaveis:
                                #print(key)

                                try:
                                    param = float(json_dailly[0][key])
                                except:
                                    param = 0
                                if param == '':
                                    param = 0
                                #import ipdb;ipdb.set_trace()
                                
                                if 'temp' in key and param > 48:
                                    pass
                                else:
                                    if key == variaveis[0]:
                                        parametros_1 = param
                                    if key == variaveis[1]:
                                        parametros_2 = param
                        #import ipdb;ipdb.set_trace()            
                        parametros_treinamento.append([float(parametros_1),float(parametros_2)])
                        if flood[count] == 1:
                            print(str(parametros_1),str(parametros_2),flood[count])
                        flood_fit.append(flood[count])
                        cont+=1
                    except Exception as e:
                        print(e)
                        import ipdb;ipdb.set_trace()
                    #import ipdb;ipdb.set_trace()
                    #list_all.append(list_temp)
                count+=1

            except:
                pass
        #CLASSIFICACAO        
        #model = DecisionTreeClassifier()
        #model = KNeighborsClassifier()
        model = svm.SVC()
        #model = GaussianNB()
        #model = LogisticRegression()

        #REGRESSAO
        #model = LinearRegression()
        #model = DecisionTreeRegressor()

        nome_algoritmo = model.__class__.__name__
        #import ipdb;ipdb.set_trace()
        #model.fit(np.transpose(np.matrix(parametros_1)),np.transpose(np.matrix(parametros_2)))
        #model.fit(np.transpose(np.matrix(parametros_1)),np.transpose(np.matrix(parametros_2)))
        model.fit(parametros_treinamento,flood_fit)

        
        result = []
        #print('##### FIT ######')
        num = 0

        result = []
        list_all = []
        list_flood = []
        
        json_data = ''
        json_dailly = ''
        json_content = ''
        param = ''
        list_temp = []
        acertos = 0
        erros = 0
        cont = 0
        cont_itens = num_test
        parametros_base = []
        parametros_reais = []
        parametros_treinamento = []
        p1= ''
        p2=''
        flood_real = []
        for dt in data[num_test:]:

            try:
                #import ipdb;ipdb.set_trace()
                
                json_data = dt.replace("'",'"')
                json_content = json.loads(json_data)

                json_dailly = json_content['history']['dailysummary']
                #import ipdb;ipdb.set_trace()
                list_temp = []
                # if json_dailly:
                #     try:
               
                if json_dailly:
                    try:
                        for key_ in json_dailly[0].keys():
                            #print(key_)
                            #import ipdb;ipdb.set_trace()
                            #if key_ in ('mintempm','minhumidity','minpressurem','maxwspdi','precipi'):
                            if key_ in variaveis:
                                #import ipdb;ipdb.set_trace()
                                try:
                                    param = float(json_dailly[0][key_])
                                except:
                                    param = float(0)
                                if param == '':
                                    param = float(0)

                                if 'temp' in key_ and param > 48:
                                    pass
                                else:
                                    if key_ == variaveis[0]:
                                        p1=param
                                    if key_ == variaveis[1]:
                                        p2=param
                        
                        parametros_treinamento.append([float(p1),float(p2)])  
                        flood_real.append(flood[cont_itens])       
                    except Exception as e:
                        print(e)

                cont_itens+=1
            except Exception as e:
                print(str(e))
                pass           
        if parametros_treinamento:
            #import ipdb;ipdb.set_trace()
            contador = 0
            for parametros_previsao in parametros_treinamento:
                predicted = model.predict([parametros_previsao])
                teste = []
                
                result.append([parametros_previsao,flood_real[contador],predicted[0]]) # .append(nº da linha .csv, boolean real, boolean previsto)
                contador+=1

                

        return result,nome_algoritmo

    def salvando_graficos(self,nome_pasta,grafico_valores_base,grafico_valores_reais,grafico_valores_previstos,parametros):
            #import ipdb;ipdb.set_trace()
            fig = plt.figure(figsize=(12, 7.195), dpi=100)
            nome_arq = 'graficos/America/'+nome_pasta+'/'+str(parametros)+'.png'

            plt.plot(grafico_valores_base,grafico_valores_reais,'bo',label='Reais')
            plt.plot(grafico_valores_base,grafico_valores_previstos,'ro',label='Previstos')
        
            
            plt.ylabel(dict_for_name.get(str(parametros[1])))
            plt.xlabel(dict_for_name.get(str(parametros[0])))
            plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
            fig.savefig(nome_arq, dpi=500, format='png')
            plt.close()

  
        
  
mac_lg = MachineLearning()
#list_param = ['maxtempm', 'minpressurem']

list_param = ['maxpressurem','mintempm']
#list_param = ['maxhumidity','maxpressurem']
#list_param = ['precipm','minhumidity']


list_combinado = list(product(list_param,repeat=2))
for comb in list_combinado:
    if comb[0]==comb[1]:
        list_combinado.remove(comb)
#list_combinado.insert(0,'cidade')
# with open('variancia.csv', 'w') as csvfile:
#     fieldnames = list_combinado
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()    
base_url='/home/lucas-desenv/workspace-machine/machine-learning/data_bases/America/'
base_url_graficos='/home/lucas-desenv/workspace-machine/machine-learning/graficos/America/'
for _,_,arquivo in os.walk(base_url):
    for name_arquivo in arquivo:
        nome_pasta_grafico = name_arquivo.split('.')
        nome_pasta_grafico = nome_pasta_grafico[0]
        if name_arquivo == 'Indianapolis.csv':
            print(name_arquivo)
            dados,flood = mac_lg.get_data('data_bases/America/'+str(name_arquivo))         
            # resultado, nome_algoritmo,acertos,erros = mac_lg.treinamento_csv(lista_parametros,flood)
            
            #list_param = ['mintempm','minhumidity','minpressurem','maxwspdi','precipi']

            dict_for_name = {
                'maxtempm': 'TEMPERATURA MAX (°C)',
                'mintempm': 'TEMPERATURA MIN (°C)',
                'minhumidity': 'UMIDADE MIN (%)',
                'maxhumidity': 'UMIDADE MAX (%)',
                'maxpressurem': 'PRESSAO MAX (mm)',
                'minpressurem': 'PRESSAO MIN (mm)',
                'maxwspdm': 'VELOC. VENTO (kph)',
                'precipm': 'PRECIPTACAO (mm)',

            }
            
            dict_csv = {}
            dict_csv.update({'cidade':name_arquivo})
            #for parametros in list_combinado:
            try:
                diferentes = 0
                iguais = 0
                resultado, nome_algoritmo = mac_lg.treinando_variaveis(list_param,dados,flood)       
                for r in resultado:
                    if r[1] == r[2] and r[1] == 1:
                        iguais+=1
                    else:
                        diferentes+=1
                print("DIFERENTES: ",diferentes)
                print("IGUAIS: ",iguais)
            except:
                pass

                #writer.writerow(dict_csv)  
                     




