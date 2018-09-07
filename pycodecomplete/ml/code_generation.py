'''code_generation.py

Generate python code with a trained RNN. Class CodeGenerator is composed
of an RNN model and a vectorizer. Takes a string and generates a sequence
of Python code

Todo:
    * 
'''
import random
import string
import sys

import numpy as np

from keras.models import Sequential

from .process_text import CharVectorizer

import tensorflow
import keras


class CodeGenerator():
    '''CodeGenerator object that generates Python code with a supplied model

    Parameters:
        sequence_length -- The number of characters in a sequence
        save_pickle_folder -- location to save the pickled model after each epoch
        pycode_directory -- location of the data

    Attributes:
        predict_n -- Predict the next n charaters
        predict_n_with_previous -- return string with the predicted code appended to the input
    '''

    def __init__(self, model, char_vectorizer):
        '''Create a CodeGenerator Object'''
        self.model = model
        self.char_vectorizer = char_vectorizer
        self.char_vectorizer.shuffle_files()

    def sample(self, preds, temperature=1.0):
        '''Helper function to sample an index from a probability array'''
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def predict_n(self, prev_text, n, diversity=1.0):
        '''Predict the next n charaters'''
        generated = ''
        sentence = prev_text

        for _ in range(n):
            x_pred = self.char_vectorizer.vectorize(sentence)

            preds = self.model.predict(x_pred, verbose=0)[0]

            next_index = self.sample(preds, diversity)
            next_char = self.char_vectorizer.indices_char[next_index]

            generated += next_char
            sentence += next_char

        return generated

    def predict_n_with_previous(self, prev_text, n, diversity=1.0):
        '''Return a string with the predicted code appended to the input'''
        return prev_text + self.predict_n(prev_text, n, diversity=diversity)
