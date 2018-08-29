import os
import sys
from argparse import ArgumentParser
import string

from keras.models import load_model

from rnn import pyCodeRNNBuilder
from process_text import CharVectorizer

pycode_directory = '/media/kevin/KEVINAFRICA/scraped-repos'


char_vectorizer = CharVectorizer(tokens=string.printable,
                                 sequence_length=100,
                                 input='directorypath', encoding='utf-8',
                                 step_size=1)

char_vectorizer.fit(pycode_directory)

X, y = char_vectorizer.transform(pycode_directory)

print(X.shape, y.shape)

