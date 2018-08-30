import os
import sys
from argparse import ArgumentParser
import string

from keras.models import load_model
from keras.models import Sequential
from keras.utils import multi_gpu_model

from rnn import pyCodeRNNBuilder
from process_text import CharVectorizer

pycode_directory = '/home/ubuntu/repos'


char_vectorizer = CharVectorizer(tokens=string.printable,
                                 sequence_length=100,
                                 input='directorypath', encoding='utf-8',
                                 step_size=10)

char_vectorizer.fit(pycode_directory)

X, y = char_vectorizer.transform(pycode_directory)

print(X.shape, y.shape)

model_builder = pyCodeRNNBuilder(100,
                                 '/home/ubuntu/models',
                                 '/home/ubuntu/repos',
                                 n_layers=4,
                                 hidden_layer_dim=1001,
                                 step_size=1,
                                 n_gpu=8,
                                 model=None)

model = model_builder.model

print('Using', 8, 'GPUs')
parallel_model = multi_gpu_model(model, gpus=8)
parallel_model.compile(loss='categorical_crossentropy', optimizer="adam")

parallel_model.fit(X, y, batch_size=5000, epochs=100)
                            
