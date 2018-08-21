import numpy as np
import pandas as pd
import dask.array as da
import string
import io
import os
import unicodedata
import sys
import random
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
        self.file_list = []
        self.n_files = None

    @property
    def sequences(self):
        return True

    def fit(self, raw_documents, y=None):
        if self.input == 'directorypath':
            if not os.path.isdir(raw_documents):
                raise ValueError("input is 'directorypath' but raw_documents is not a directory")
            
            for dirName, _, fileList in os.walk(raw_documents):
                #print('Found directory: %s' % dirName)
                for fname in fileList:
                    if fname.endswith(self.file_extension):
                        self.file_list.append(os.path.join(dirName, fname))
            self.n_files = len(self.file_list)

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
                yield unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        elif self.input == 'filepath':
            if os.path.isfile(raw_documents):
                with io.open(raw_documents, encoding=self.encoding) as f:
                    contents = f.read()
                for text in [contents]:
                    yield unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
            else:
                raise ValueError("input is 'filepath' but raw_documents filepath is not a file")
        elif self.input == 'directorypath':
            if os.path.isdir(raw_documents):
                for dirName, _, fileList in os.walk(raw_documents):
                    #print('Found directory: %s' % dirName)
                    for fname in fileList:
                        if fname.endswith(self.file_extension):
                            filepath = os.path.join(dirName, fname)
                            #print(filepath)
                            with io.open(filepath, encoding=self.encoding) as f:
                                text = f.read()
                            yield unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii', 'replace')
            else:
                raise ValueError("input is 'directorypath' but raw_documents is not a directory")
        else:
            raise ValueError("input must be string {'filepath', 'directorypath', 'content'}")

    def batch_generator(self, count=None, batch_size=512):
        '''Generate a batch of vectorized training data for each file'''
        while True:

            if count is None:
                count = self.n_files

            for _ in range(count):

                sequences = []
                next_chars = []
                file_path = random.sample(self.file_list, 1)[0]
                
                with io.open(file_path, encoding=self.encoding) as f:
                    text = f.read()

                text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii', 'replace')

                for i in range(0, len(text) - self.sequence_length, self.step_size):
                    sequences.append(text[i: i + self.sequence_length])
                    next_chars.append(text[i + self.sequence_length])
                
                #Create zeroed feature array shape number of sentences x max_length x 100
                X = np.zeros((len(sequences), self.sequence_length, len(string.printable)), dtype=np.bool)
                #Create zeroed target array shape number of sentences x 100
                y = np.zeros((len(sequences), len(string.printable)), dtype=np.bool)
                
                #Encode character with a True in the corresponsing index
                for i, sequence in enumerate(sequences):
                    for letter_ind, char in enumerate(sequence):
                        X[i, letter_ind, self.char_indices[char]] = True
                    y[i, self.char_indices[next_chars[i]]] = True


                for ix in range(0, len(X), batch_size):
                    print(file_path, len(X))
                    yield X[ix:batch_size,:,:], y[ix:batch_size,:]

                '''
                ix = 0
                print(len(X))
                while len(X) - ix >= batch_size:
                    yield X[ix:batch_size,:,:], y[ix:batch_size,:]
                    ix = ix + batch_size
                
                if len(X) - ix < batch_size:
                    yield X[ix,:,:], y[ix,:]
                '''