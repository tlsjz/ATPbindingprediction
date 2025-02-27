import numpy as np
import os
import pickle
import tensorflow as tf
import keras
from keras import backend as K
from keras.backend.tensorflow_backend import set_session
from keras.models import Model, load_model
from keras.layers import Concatenate
from keras import regularizers
import keras.layers.core as core
from keras.layers import Dense,Activation,Convolution2D, Convolution1D, MaxPool2D, Flatten, BatchNormalization, Dropout, Input, Bidirectional, MaxPool1D, AveragePooling1D, AveragePooling2D, GlobalAveragePooling2D, Add
from keras.optimizers import Adam
from keras.utils import np_utils
from sklearn import metrics
from keras.callbacks import ModelCheckpoint
import math
import lightgbm as lgb
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

class roc_callback(keras.callbacks.Callback):
    def __init__(self,training_data, validation_data):

        self.x = training_data[0]
        self.y = training_data[1]
        self.x_val = validation_data[0]
        self.y_val = validation_data[1]


    def on_train_begin(self, logs={}):
        return

    def on_train_end(self, logs={}):
        return

    def on_epoch_begin(self, epoch, logs={}):
        return

    def on_epoch_end(self, epoch, logs={}):        
        y_pred = self.model.predict(self.x)
        roc = metrics.roc_auc_score(self.y, y_pred)      

        y_pred_val = self.model.predict(self.x_val)
        roc_val = metrics.roc_auc_score(self.y_val, y_pred_val)      

        print('\rroc-auc: %s - roc-auc_val: %s' % (str(round(roc,4)),str(round(roc_val,4))),end=100*' '+'\n')
        return

    def on_batch_begin(self, batch, logs={}):
        return

    def on_batch_end(self, batch, logs={}):
        return   
    
def conv2d_bn(x,
              filters,
              num_row,
              num_col,
              padding='same',
              strides=(1, 1),
              name=None):
    x = Convolution2D(filters, (num_row, num_col),
        kernel_initializer= 'glorot_normal',
        strides=strides,
        padding=padding,
        data_format='channels_first',
        use_bias=False)(x)
    x = BatchNormalization(axis=1, scale=False)(x)
    x = Activation('relu')(x)
    #x = Dropout(0.3)(x)
    return x

def conv1d_bn(x,
              filters,
              num_row,
              padding='same',
              strides=1,
              name=None):
    x = Convolution1D(filters, num_row,
        kernel_initializer= 'glorot_normal',
        strides=strides,
        padding=padding,
        data_format='channels_first',
        use_bias=False)(x)
    x = BatchNormalization(axis=1, scale=False)(x)
    x = Activation('relu')(x)
    #x = Dropout(0.3)(x)
    return x    


def module(part):
    #traindatapickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/train.pickle','rb')
    #traindatapickle = open('/home/songjiazhi/atpbinding/atp227/feature15.pickle','rb')
    traindatapickle = open('/home/songjiazhi/atpbinding/traindata/denseincep_label.pickle','rb')
    #traindata = pickle.load(traindatapickle)
    #label_train = traindata[0]
    label_train = pickle.load(traindatapickle)
    #pssmfeature_train_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/pssmfeature.pickle','rb')
    #pssmfeature_train_pickle = open('/home/songjiazhi/atpbinding/evaluate/pssmfeature.pickle','rb')
    pssmfeature_train_pickle = open('/home/songjiazhi/atpbinding/traindata/pssmfeature.pickle','rb')
    pssmfeature_train = pickle.load(pssmfeature_train_pickle)
    #psipredfeature_train_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/psipredfeature.pickle','rb')
    #psipredfeature_train_pickle = open('/home/songjiazhi/atpbinding/evaluate/psipredfeature.pickle','rb')
    psipredfeature_train_pickle = open('/home/songjiazhi/atpbinding/traindata/psipredfeature.pickle','rb')
    psipredfeature_train = pickle.load(psipredfeature_train_pickle)
    #chemicalfeature_train_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/chemicalfeature.pickle','rb')
    #chemicalfeature_train_pickle = open('/home/songjiazhi/atpbinding/evaluate/chemicalfeature.pickle','rb')
    chemicalfeature_train_pickle = open('/home/songjiazhi/atpbinding/traindata/chemicalfeature.pickle','rb')
    chemicalfeature_train = pickle.load(chemicalfeature_train_pickle)
    
    #testdatapickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/test.pickle','rb')
    testdatapickle = open('/home/songjiazhi/atpbinding/atp41/newfeature15.pickle','rb')
    testdata = pickle.load(testdatapickle)
    label_test = testdata[0]
    #pssmfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/pssmfeature_test.pickle','rb')
    pssmfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp388/pssmfeature_test.pickle','rb')
    pssmfeature_test = pickle.load(pssmfeature_test_pickle)
    #psipredfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/psipredfeature_test.pickle','rb')
    psipredfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp388/psipredfeature_test.pickle','rb')
    psipredfeature_test = pickle.load(psipredfeature_test_pickle)
    #chemicalfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp227/fivefold/'+str(part)+'/chemicalfeature_test.pickle','rb')
    chemicalfeature_test_pickle = open('/home/songjiazhi/atpbinding/atp388/chemicalfeature_test.pickle','rb')
    chemicalfeature_test = pickle.load(chemicalfeature_test_pickle)
    
    pssmfeature_train = np.array(pssmfeature_train)
    pssmfeature_train = pssmfeature_train.reshape(-1,1,15,20)
    psipredfeature_train = np.array(psipredfeature_train)
    psipredfeature_train = psipredfeature_train.reshape(-1,1,15,3)
    chemicalfeature_train = np.array(chemicalfeature_train)
    chemicalfeature_train = chemicalfeature_train.reshape(-1,1,15,7)
    label_train_one = np_utils.to_categorical(label_train, num_classes=2)
    
    pssmfeature_test = np.array(pssmfeature_test)
    pssmfeature_test = pssmfeature_test.reshape(-1,1,15,20)
    psipredfeature_test = np.array(psipredfeature_test)
    psipredfeature_test = psipredfeature_test.reshape(-1,1,15,3)
    chemicalfeature_test = np.array(chemicalfeature_test)
    chemicalfeature_test = chemicalfeature_test.reshape(-1,1,15,7)
    label_test_one = np_utils.to_categorical(label_test, num_classes=2)
    
    pssminput = Input((1,15,20))
    psipredinput = Input((1,15,3))
    chemicalinput = Input((1,15,7))    
    
    chemical_x_branch1 = conv2d_bn(chemicalinput, 64, 1, 1)
    chemical_x_branch3 = conv2d_bn(chemicalinput, 64, 1, 1)
    chemical_x_branch3 = conv2d_bn(chemical_x_branch3, 96, 3, 3)
    chemical_x_branch3 = conv2d_bn(chemical_x_branch3, 96, 3, 3)
    chemical_x_branch5 = conv2d_bn(chemicalinput, 64, 1, 1)
    chemical_x_branch5 = conv2d_bn(chemical_x_branch5, 64, 5, 5)
    
    chemical_x = Concatenate(axis=1)([chemical_x_branch1, chemical_x_branch3, chemical_x_branch5])
    chemical_x = Flatten()(chemical_x)
    chemical_x = BatchNormalization(axis=1, scale=False)(chemical_x)
    chemical_x = Dense(256, activation='relu')(chemical_x)
    chemical_x = Dropout(0.5)(chemical_x)
    chemical_x = Dense(128, activation='relu')(chemical_x)    
    
    psipred_x_branch1 = conv2d_bn(psipredinput, 64, 1, 1)
    psipred_x_branch3 = conv2d_bn(psipredinput, 64, 1, 1)
    psipred_x_branch3 = conv2d_bn(psipred_x_branch3, 96, 3, 3)
    psiperd_x_branch3 = conv2d_bn(psipred_x_branch3, 96, 3, 3)
    
    psipred_x = Concatenate(axis=1)([psipred_x_branch1, psipred_x_branch3])
    psipred_x = Flatten()(psipred_x)
    psipred_x = BatchNormalization(axis=1, scale=False)(psipred_x)
    psipred_x = Dense(64, activation='relu')(psipred_x)   
    
    pssm_x_branch1 = conv2d_bn(pssminput, 64, 1, 1)  
    pssm_x_branch3 = conv2d_bn(pssminput, 64, 1, 1)  
    pssm_x_branch3 = conv2d_bn(pssm_x_branch3, 96, 3, 3)
    pssm_x_branch3 = conv2d_bn(pssm_x_branch3, 96, 3, 3)
    pssm_x_branch5 = conv2d_bn(pssminput, 64, 1, 1)
    pssm_x_branch5 = conv2d_bn(pssm_x_branch5, 64, 5, 5)
     
    pssm_x = Concatenate(axis=1)([pssm_x_branch1, pssm_x_branch3, pssm_x_branch5])
    pssm_x = Flatten()(pssm_x)
    pssm_x = BatchNormalization(axis=1)(pssm_x)
    pssm_x = Dense(256, activation='relu')(pssm_x)
    pssm_x = Dropout(0.5)(pssm_x)
    pssm_x = Dense(128,activation='relu')(pssm_x)
    
    
    featurecombination = Concatenate(axis = 1)([chemical_x, psipred_x, pssm_x])
    
    #output = Flatten()(conv_out)
    #output = Concatenate(axis=1)([psipred_x, pssm])    
    output = Dense(128, activation='relu')(featurecombination)
    output = Dropout(0.5)(output)
    output = Dense(64, activation='relu')(output)
    output = Dense(2,activation='softmax')(output)    
    
    testmodel = Model([pssminput, psipredinput, chemicalinput], output)
    adam = Adam(lr=0.0001,epsilon=1e-08)
    testmodel.compile(optimizer=adam, loss='binary_crossentropy',metrics=['binary_accuracy'])   
    
    print('Training------')
    filepath = '/home/songjiazhi/atpbinding/models/denseincepmodel/weights-{epoch:02d}.hdf5'
    checkpoint = ModelCheckpoint(filepath, save_best_only=False, save_weights_only=False)     
    class_weight = {0:0.5205,1:12.7113}
    #testmodel.fit([pssmfeature_train, psipredfeature_train, chemicalfeature_train], label_train_one, epochs=15, batch_size=256, class_weight=class_weight, shuffle=True, callbacks=[roc_callback(training_data=([pssmfeature_train, psipredfeature_train, chemicalfeature_train], label_train_one), validation_data=([pssmfeature_test, psipredfeature_test, chemicalfeature_test], label_test_one))])    
    testmodel.fit([pssmfeature_train, psipredfeature_train, chemicalfeature_train], label_train_one, epochs=60, batch_size=256, class_weight=class_weight, shuffle=True, callbacks=[roc_callback(training_data=([pssmfeature_train, psipredfeature_train, chemicalfeature_train], label_train_one), validation_data=([pssmfeature_test, psipredfeature_test, chemicalfeature_test], label_test_one)), checkpoint])     
    
if __name__=="__main__":  
    module('1')
    #for i in range(1,6):
        #print(i)
        #module(i)