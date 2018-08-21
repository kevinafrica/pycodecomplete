import numpy as np
import os
#import multi_gpu
import string
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Activation, Dense

def batch_generator(directorypath):
    if os.is


def build_model(sequence_length, vocabulary_size, n_layers=1,
                hidden_layer_dim=128, dropout_rate=.2):
    """Build a Keras sequential model for training the char-rnn"""
    model = Sequential()
    for i in range(n_layers):
        model.add(
            LSTM(
                hidden_layer_dim, 
                return_sequences = True if (i != (n_layers - 1)) else False,
                input_shape=(sequence_length, vocabulary_size)
            )
        )
        model.add(Dropout(dropout_rate))
    
    model.add(Dense(vocabulary_size))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy', optimizer="adam")

    return model