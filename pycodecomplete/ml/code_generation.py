'''Predict code using a trained RNN model and a
   fit character vectorizer'''

# Author: Kevin Africa
# License: MIT

import random
import string
import sys

import numpy as np

from keras.models import Sequential

from process_text import CharVectorizer

class CodeGenerator():

    def __init__(self, model, char_vectorizer):
        self.model = model
        self.char_vectorizer = char_vectorizer
        self.char_vectorizer.shuffle_files()

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def predict_n(self, prev_text, n, diversity=1.0):

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
        return prev_text + self.predict_n(prev_text, n, diversity=diversity)
