from sklearn import *
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import graphviz #https://graphviz.org/download/
from alive_progress import alive_bar

def parseJson():
    data_train = pd.read_json("./devices_IA_clases.json")
    X_train = data_train[['servicios','servicios_inseguros']]
    y_train = data_train['peligroso']

    data_test = pd.read_json("./devices_IA_predecir_v2.json")
    X_test = data_test[['servicios','servicios_inseguros']]
    y_test = data_test['peligroso']

    return data_test['id'], (X_train, X_test, y_train, y_test)

def plotPredictions(real, predictions, ids):
    fig = plt.figure(figsize = (20, 10))
    plt.bar() # ids, prediccion, peligro

def decisionTreeClassifier(data, test_ids):
    print("-----------------")
    print("ÁRBOL DE DECISIÓN")
    print("-----------------")
    (X_train, X_test, y_train, y_test) = data
    
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Predicción de número de dispositivos peligrosos:",sum(y_pred))
    print("Número de dispositivos peligrosos real:",sum(y_test))
    print("Precisión de las predicciones:",metrics.accuracy_score(y_test, y_pred))

    #Print plot
    tree_data = tree.export_graphviz(clf, out_file=None, feature_names=['servicios','servicios_inseguros'], class_names=['no peligroso','peligroso'], filled=True, rounded=True, special_characters=True)
    graph = graphviz.Source(tree_data)
    graph.render('test.gv', view=True).replace('\\', '/')
    return y_pred

def linearRegresion(data, test_ids):
    print("\n----------------")
    print("REGRESIÓN LINEAL")
    print("----------------")
    (X_train, X_test, y_train, y_test) = data
    
    get_ratio = lambda x: [x['servicios_inseguros'][i]/x['servicios'][i] if x['servicios'][i]!=0 else 0 for i in range(len(x['servicios']))]
    X_train = np.array(get_ratio(X_train)).reshape(-1, 1)
    X_test = np.array(get_ratio(X_test)).reshape(-1, 1)

    regr = linear_model.LinearRegression()
    regr.fit(X_train, y_train)
    y_pred = regr.predict(X_test)
    print("Predicción de número de dispositivos peligrosos:",sum(y_pred))
    print("Error cuadrático medio: %.2f" % mean_squared_error(y_test, y_pred))
    # Plot outputs
    plt.scatter(X_test, y_test, color="black")
    plt.plot(X_test, y_pred, color="blue", linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()
    return y_pred

def randomForest(data, test_ids):
    print("\n-------------")
    print("RANDOM FOREST")
    print("-------------")
    (X_train, X_test, y_train, y_test) = data
    clf = RandomForestClassifier(max_depth=2, random_state=0,n_estimators=10)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("Predicción de número de dispositivos peligrosos:",sum(y_pred))
    print("Precisión de las predicciones:",metrics.accuracy_score(y_test, y_pred))

    print("Generando archivos gráficos...\n")
    with alive_bar(len(clf.estimators_)) as bar:
        for i in range(len(clf.estimators_)):
            bar()
            estimator = clf.estimators_[i]
            export_graphviz(estimator,
                            out_file='tree.dot',
                            feature_names=['servicios','servicios_inseguros'],
                            class_names=['no peligroso','peligroso'],
                            rounded=True, proportion=False,
                            precision=2, filled=True)
            call(['dot', '-Tpng', 'tree.dot', '-o', 'tree'+str(i)+'.png', '-Gdpi=600'])
    print("\nArchivos guardados como tree<numero>.png")
    return y_pred

if __name__ == '__main__':
    test_ids, data = parseJson()
    predictions = {'decision tree':[],'linear regresion':[],'random forest':[]}
    predictions['decision tree'] = decisionTreeClassifier(data, test_ids)
    predictions['linear regresion'] = linearRegresion(data, test_ids)
    predictions['random forest'] = randomForest(data, test_ids)
    plotPredictions(data[3], predictions, test_ids)