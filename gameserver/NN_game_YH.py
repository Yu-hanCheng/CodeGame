# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 21:46:48 2019

@author: scream
"""

import pickle
import numpy as np

with open('GameInfor_test.pickle', 'rb') as file:
    infor=pickle.load(file)

#%%
ballpos=infor[0]
platform=infor[1]
instruct=infor[3]
#%%

x=np.hstack([ballpos[0:len(instruct), :], platform[0:len(instruct), 1][:, np.newaxis]])
y=instruct


from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
#%% svm
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
svm=SVC(gamma=0.0001, C=1000)
svm.fit(x_train, y_train)

yp_svm=svm.predict(x_test)
acc=accuracy_score(yp_svm, y_test)
acc
#%% random forest
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
# split train and test data into 0.8:0.2
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
RFC=RandomForestClassifier(n_estimators=20, random_state=10) # using 10 trees in Random forest
RFC.fit(x_train, y_train)

# calculate accuracy for evaluating the results
y_pred_RF=RFC.predict(x_test)
acc=accuracy_score(y_pred_RF, y_test)
acc
#%% KNN
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
neigh = KNeighborsClassifier(n_neighbors=5)
neigh.fit(x_train, y_train)

y_knn=neigh.predict(x_test)

# calculate accuracy
acc=accuracy_score(y_knn, y_test)
#%% KNN +Bagging
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier

# setting of bagging classifier 
bagging = BaggingClassifier(KNeighborsClassifier(), n_estimators=100,
                            max_samples=0.5, max_features=0.5)
# train classifier, then make prediction
bagging.fit(x_train, y_train)
y_bag=bagging.predict(x_test)
# calculate accuracy
acc=accuracy_score(y_bag, y_test)
#%% nn
# Setup NN
from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(5,7,7,5), max_iter=10000, random_state=2)

mlp.fit(x_train, y_train)
print("Training set score: %f" % mlp.score(x_train, y_train))


yp_nn=mlp.predict(x_test)
acc=accuracy_score(yp_nn, y_test)
#%% save model -- nn
import pickle

filename="nn_model_YHPF_0328.sav"
pickle.dump(mlp, open(filename, 'wb'))

# load model
l_model=pickle.load(open(filename,'rb'))
yp_l=l_model.predict(x_test)
print("acc load: %f " % accuracy_score(yp_l, y_test))
#%% save model --Random Forest
import pickle

filename="RFC_model_YHPF_0328.sav"
pickle.dump(RFC, open(filename, 'wb'))

# load model
l_model=pickle.load(open(filename,'rb'))
yp_l=l_model.predict(x_test)
print("acc load: %f " % accuracy_score(yp_l, y_test))