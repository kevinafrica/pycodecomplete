import numpy as np
import pandas as pd
import string
import io
import os
from sklearn.base import BaseEstimator, TransformerMixin

class CharVectorizer(BaseEstimator, TransformerMixin):
    
    def __init__(self, input='content', encoding='utf-8', decode_error='ignore',
                 tokens=string.printable, sequence_length=50, step_size=1,
                 file_extension='.py'):
        '''
        
        Parameters
        ----------
        input : string {'filepath', 'directorypath', 'content'}
            If 'filename', the sequence passed as an argument to fit is
            expected to be a list of filenames that need reading to fetch
            the raw content to analyze.
        '''
        self.input = input
        self.encoding = encoding
        self.decode_error = decode_error
        self.tokens = tokens
        self.sequence_length = sequence_length
        self.step_size = step_size
        self.char_indices = dict((c, i) for i, c in enumerate(tokens))
        self.indices_char = dict((i, c) for i, c in enumerate(tokens))
        self.file_extension = file_extension

    @property
    def sequences(self):
        return True

    def fit(self, raw_documents, y=None):
        return self

    def transform(self, raw_documents, copy=True):
        '''Converts string to two boolean encoded vectors X and y. X contains max_length
        number of characters and the target y contains the next character in that sequence.

        Args:
            text (str): The text to be encoded.
            max_length (int): The length of each sequence
            step_size (str): The number of steps taken before starting the next sequence

        Returns:
            X: The feature array of shape (# sequences x max_length x 100)
            y: The target array of shape (# sequences x 100)
            sentences
        '''
        sequences = []
        next_chars = []
        X_output = []
        y_output = []
        
        for document in self.documents_to_strings(raw_documents):

            for i in range(0, len(document) - self.sequence_length, self.step_size):
                sequences.append(document[i: i + self.sequence_length])
                next_chars.append(document[i + self.sequence_length])
            
            #Create zeroed feature array shape number of sentences x max_length x 100
            X = np.zeros((len(sequences), self.sequence_length, len(string.printable)), dtype=np.bool)
            #Create zeroed target array shape number of sentences x 100
            y = np.zeros((len(sequences), len(string.printable)), dtype=np.bool)
            
            #Encode character with a True in the corresponsing index
            for i, sequence in enumerate(sequences):
                for letter_ind, char in enumerate(sequence):
                    X[i, letter_ind, self.char_indices[char]] = True
                y[i, self.char_indices[next_chars[i]]] = True

            X_output.append(X)
            y_output.append(y)

        return np.vstack(X_output), np.vstack(y_output)

    def documents_to_strings(self, raw_documents):

        if self.input == 'content':
            for text in [raw_documents]:
                yield text
        elif self.input == 'filepath':
            if os.path.isfile(raw_documents):
                with io.open(raw_documents, encoding='utf-8') as f:
                    contents = f.read()
                for text in [contents]:
                    yield text
            else:
                raise ValueError("input is 'filepath' but raw_documents filepath is not a file")
        elif self.input == 'directorypath':
            if 1 == 1:
                for dirName, _, fileList in os.walk(raw_documents):
                    #print('Found directory: %s' % dirName)
                    for fname in fileList:
                        if fname.endswith(self.file_extension):
                            filepath = os.path.join(dirName, fname)
                            #print(filepath)
                            with io.open(filepath, encoding=self.encoding) as f:
                                yield f.read()
            else:
                raise ValueError("input is 'directorypath' but raw_documents is not a directory")
        else:
            raise ValueError("input must be string {'filepath', 'directorypath', 'content'}")
