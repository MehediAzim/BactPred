# -*- coding: utf-8 -*-
"""Antimicrobial_New_Model_independent.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UMSs_S0Q7Lm1QKjCX2pspfxGPZAd7yLG
"""

from google.colab import drive
drive.mount('/content/drive',force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
# %cd 'drive/My Drive/Antimicrobial_peptide/code'
# %cd 'drive/My Drive/Research/Antimicrobial_peptide/code'

# Deep Neural Networks:
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import (Input, Dense, Dropout, Flatten, BatchNormalization,
                                     Conv1D, Conv2D, MaxPooling1D, MaxPooling2D,
                                     LSTM, GRU, Embedding, Bidirectional, Concatenate)
from tensorflow.keras.regularizers import (l1, l2, l1_l2)
from tensorflow.keras.optimizers import (RMSprop, Adam, SGD)
from tensorflow.keras.models import (Sequential, Model)

# Core:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Performance:
from sklearn.metrics import (confusion_matrix, classification_report, matthews_corrcoef, precision_score)
from sklearn.model_selection import (StratifiedKFold, KFold, train_test_split)

#Utilities:
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical as labelEncoding   # Usages: Y = labelEncoding(Y, dtype=int)
from tensorflow.keras.utils import plot_model                        # Usages: plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=False, expand_nested=True)
from sklearn import preprocessing # Feature Scaling

from sklearn.metrics import average_precision_score
from sklearn.metrics import plot_precision_recall_curve
#end-import

# Commented out IPython magic to ensure Python compatibility.
# %ls

terminus_length = 100

#if you have three representations, you are going to have threee heads and so on
X1 = np.load("primarySPIDER.npy")
X2 = np.load("antimicrobial_pssm.npy")
#X_train_three = np.load("/content/drive/My Drive/Colab Notebooks/kmer_k_3_ACP240_PCA_20.npy")


X1 = X1[:,0:terminus_length,0:]
X2 = X2[:,0:terminus_length,0:]


#Make y
Y = list(np.ones(346))
Y[346:692]= np.zeros(346)
Y = np.array(Y)


print("Maximum Value in SPIDER Encoding: {}".format(np.amax(X1)))

#normalize SPIDER head values

X1[:,:,0] = X1[:,:,0] / 180
X1[:,:,1] = X1[:,:,1] / 180
X1[:,:,2] = X1[:,:,2] / 180
X1[:,:,3] = X1[:,:,3] / 180
X1[:,:,4] = X1[:,:,4] / 180 

for peptide in X1:
  for amino_acid in peptide:
    max_property_value = np.amax(amino_acid)
    if max_property_value > 10:
      print(amino_acid)

print(X1.shape)
print(X2.shape)
print(Y.shape)

def calculate_performance(test_num, pred_y, labels):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for index in range(test_num):
        if labels[index] == 1:
            if labels[index] == pred_y[index]:
                tp = tp + 1
            else:
                fn = fn + 1
        else:
            if labels[index] == pred_y[index]:
                tn = tn + 1
            else:
                fp = fp + 1

    # entering any of the else statement means that the evaluation etric is invalid
    acc = float(tp + tn) / test_num
    
    if((tp + fp) != 0):
      precision = float(tp) / (tp + fp)
    else:
      precision = 0

    if((tp + fp) != 0):
      sensitivity = float(tp) / (tp + fn)
    else:
      sensitivity = 0

    if((tn + fp) != 0):
      specificity = float(tn) / (tn + fp)
    else:
      specificity = 0

    MCC = float(tp * tn - fp * fn) / (np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    F1 = 2 * (precision * sensitivity) / (precision + sensitivity)
    return acc, precision, sensitivity, specificity, MCC , F1

def lossPlot(results):
    plt.title(label='Loss: Training and Validation')
    plt.plot(results.history['loss'], label='Training Loss')
    plt.plot(results.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
#end-def

def accuracyPlot(results):
    plt.title(label='Accuracy: Training and Validation')
    plt.plot(results.history['accuracy'], label='Training Accuracy')
    plt.plot(results.history['val_accuracy'], label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()
#end-def

# Model-240 (Original)

def Network():

    branch_one_dense_outputs = []
    branch_two_dense_outputs = []

    ### Head-1:
    input1 = Input(shape=X1[0].shape)

    x = Conv1D(filters=25, kernel_size=3, padding='same', activation='relu', kernel_regularizer=l2(l=0.03))(input1)
    x = Dropout(rate=0.65)(x)
    temp = x
    
    #temp = MaxPooling1D(pool_size=2,strides=2)(temp)
    for filter_index in range(x.shape[-1]):
      branch_one_dense_outputs.append(Dense(units = 2,activation=tf.nn.relu)(temp[:,:,filter_index]))


    x = Conv1D(filters=50, kernel_size=3, padding='same', activation='relu', kernel_regularizer=l2(l=0.03))(x)
    x = Dropout(rate=0.65)(x)
    temp = x
    
    #temp = MaxPooling1D(pool_size=2,strides=2)(temp)
    for filter_index in range(x.shape[-1]):
      branch_one_dense_outputs.append(Dense(units = 2,activation=tf.nn.relu)(temp[:,:,filter_index]))


    ### Head-2:
    input2 = Input(shape=X2[0].shape)

    x = Conv1D(filters=25, kernel_size=3, padding='same', activation='relu', kernel_regularizer=l2(l=0.03))(input2)
    x = Dropout(rate=0.65)(x)
    temp = x
    
    #temp = MaxPooling1D(pool_size=2,strides=2)(temp)
    for filter_index in range(x.shape[-1]):
      branch_two_dense_outputs.append(Dense(units = 2,activation=tf.nn.relu)(temp[:,:,filter_index]))


    x = Conv1D(filters=50, kernel_size=3, padding='same', activation='relu', kernel_regularizer=l2(l=0.03))(x)
    x = Dropout(rate=0.65)(x)
    temp = x
    
    #temp = MaxPooling1D(pool_size=2,strides=2)(temp)
    for filter_index in range(x.shape[-1]):
      branch_two_dense_outputs.append(Dense(units = 2,activation=tf.nn.relu)(temp[:,:,filter_index]))


    dense_outputs_from_all_branches = branch_one_dense_outputs + branch_two_dense_outputs
    merge = Concatenate()(dense_outputs_from_all_branches)
    output = Dropout(rate=0.50)(merge)

    output = Dense(units=1, activation='sigmoid')(output)

    return Model(inputs=[input1, input2], outputs=output)
#end-def

model = Network()
model.summary()
plot_model(model, to_file='model-240.png', show_shapes=True, show_layer_names=False, expand_nested=True)

# epoch_value = 50

# model = Network()
# optimizer = Adam(lr=0.00019)

# model.compile(optimizer=optimizer, loss='binary_crossentropy',metrics=['accuracy'])
# model.fit(x=[X1[:,:,:],X2[:,:,:]],y=Y, epochs=epoch_value, batch_size=15)

#Loading independent set
X_test_one = np.load("IndependentSPIDER.npy")
X_test_two = np.load("independentPSSM.npy")


#X_train_three = X_train_three[:,:,0:terminus_length]
X_test_one = X_test_one[:,0:terminus_length,0:]
X_test_two = X_test_two[:,0:terminus_length,0:]

print(X_test_one.shape)
print(X_test_two.shape)
# print(X_train_three.shape)

y_test = list(np.ones(74))
y_test[74:]= np.zeros(74)
y_test = np.array(y_test)


print(y_test.shape)
y_test

# X_test_one[:][:][0:5]=X_test_one[:][:][0:5]/180.0
X_test_one[:,:,0] = X_test_one[:,:,0] / 180
X_test_one[:,:,1] = X_test_one[:,:,1] / 180
X_test_one[:,:,2] = X_test_one[:,:,2] / 180
X_test_one[:,:,3] = X_test_one[:,:,3] / 180
X_test_one[:,:,4] = X_test_one[:,:,4] / 180

# scores = model.evaluate([X_test_one[:,:,:],X_test_two[:,:,:]], y_test, verbose=0)
# probabilities = model.predict([X_test_one[:,:,:],X_test_two[:,:,:]])


# prob = list(probabilities)
# predicted_classes = probabilities >= 0.5
    
# apur = average_precision_score(y_test , probabilities)
    
# predicted_classes = predicted_classes.astype(int)

# acc, precision, sensitivity, specificity, MCC , F1 = calculate_performance(len(y_test), predicted_classes, y_test)

# print('accuracy',acc, end =", ")
# print('MCC',MCC, end =", ")
# print('precision',precision, end =", ")
# print('sensitivity',sensitivity, end =", ")
# print('specificity',specificity)

learning_rate = 0.0019

kf =  StratifiedKFold(n_splits = 5,shuffle=True)

all_accuracies = []
all_acc = []
all_precision = []
all_sensitivity = []
all_specificity = []
all_MCC = []
all_F1 = []

prob = []
all_apur = []
result=[]
 
#lrate = LearningRateScheduler(step_decay)

callbacks_list = []

epoch_value = 400

for train_index,test_index in kf.split(X1,Y):
    
    model = Network()

    optimizer = Adam(lr=learning_rate)

    model.compile(optimizer=optimizer, loss='binary_crossentropy',metrics=['accuracy'])

    # result.append(model.fit(x=[X_train_one[train_index,:,0:terminus_length]],y=y_train[train_index],validation_data=([X_train_one[test_index,:,0:terminus_length]],y_train[test_index]), epochs=epoch_value, batch_size=15))                                                  
    result.append(model.fit(x=[X1[train_index,:,:],X2[train_index,:,:]],y=Y[train_index],validation_data=([X_test_one[:,:,:],X_test_two[:,:,:]],y_test), epochs=epoch_value, batch_size=15,callbacks=callbacks_list))
    
    # scores = model.evaluate([X_train_one[test_index,:,:],X_train_two[test_index,:,:],X_train_three[test_index,:,:]], y_train[test_index], verbose=0)
    scores = model.evaluate([X1[test_index,:,:],X2[test_index,:,:]], Y[test_index], verbose=0)
    # scores = model.evaluate([X_train_one[test_index,:,:]], y_train[test_index], verbose=0)

    # probabilities = model.predict([X_train_one[test_index,:,:],X_train_two[test_index,:,:],X_train_three[test_index,:,:]])
    probabilities = model.predict([X1[test_index,:,:],X2[test_index,:,:]])
    # probabilities = model.predict([X_train_one[test_index,:,:]])

    prob.extend(list(probabilities))
    predicted_classes = probabilities >= 0.5
    
    all_apur.append(average_precision_score(Y[test_index], probabilities))
    
    predicted_classes = predicted_classes.astype(int)

    acc, precision, sensitivity, specificity, MCC, F1 = calculate_performance(len(test_index), predicted_classes, Y[test_index])

    all_accuracies.append(scores)
    all_acc.append(acc)
    all_MCC.append(MCC)
    all_F1.append(F1)
    if(sensitivity != 0):
      all_sensitivity.append(sensitivity)
    if(specificity != 0):
      all_specificity.append(specificity)
    if(precision != 0):
      all_precision.append(precision)

total_accuracy = 0
for i in range(5) :
    loss,accuracy = all_accuracies[i]
    #print(accuracy)
    total_accuracy = total_accuracy + accuracy


for i in range(5):
  print('fold -',i,'accuracy',all_acc[i])

print('accuracy',sum(all_acc)/5, end =", ")
print('MCC',sum(all_MCC)/5, end =", ")
print('precision',sum(all_precision)/5, end =", ")
print('sensitivity',sum(all_sensitivity)/5, end =", ")
print('specificity',sum(all_specificity)/5, end =", ")
print('f1 score',sum(all_F1)/5)

print(np.sum((np.array(prob)>0.95).astype(int)),"sequence has probability more than 95%")
print("AUPR score :- ",apur)

def loss_plot(result):
  fig=plt.figure(figsize=(25,12))
  columns = 5
  rows = 2

  for i in range(len(result)):
      fig.add_subplot(rows, columns, i+1)
      plt.title(label='Loss: Training and Validation')
      plt.plot(result[i].history['loss'], label='loss')
      plt.plot(result[i].history['val_loss'], label='val_loss')
      plt.xlabel('Epoch - '+str(i+1))
      plt.ylabel('Loss')
      plt.legend()  
  plt.show()
def accuracy_plot(result):
    fig=plt.figure(figsize=(25,12))
    columns = 5
    rows = 2 
    for i in range(len(result)):
      fig.add_subplot(rows, columns, i+1)   
      plt.title(label='Accuracy: Training and Validation')
      plt.plot(result[i].history['accuracy'], label='accuracy')
      plt.plot(result[i].history['val_accuracy'], label='val_accuracy')
      plt.xlabel('Epoch - '+str(i+1))
      plt.ylabel('Accuracy')
      plt.legend()
    plt.show()

#ploting the figures
loss_plot(result)
accuracy_plot(result)