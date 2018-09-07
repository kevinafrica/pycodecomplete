# -*- coding: utf-8 -*-
'''codetovec.py

PyCodeVectors converts Python code to encoded vectors using multiprocessing

Todo:
    * 
'''
import glob
import io
import os
import numpy as np
import string
import multiprocessing


class PyCodeVectors():
    '''PyCodeVectors object that converts Python code to one-hot-encoded vectors

    Parameters:
        source_directory -- directory of the Python code data
        encoding -- text file encoding (default ascii)
        decode_errors -- decoding error handling (default ignore)
        vocabulary -- string containing characters to consider (default string.printable)
        sequence_length -- length of each sequence (default 100)
        step_size -- number of characters to step to create the next sequence (default 1)
        file_extension -- the file extension of teh fiels to use as data (default .py)
        pad_token -- token to use as padding (default \x0c)

    Attributes:
        vocabulary_length -- number of characters in vocabulary
        char_to_idx -- dictionary that maps character to one-hot-encoding index
        idx_to_char -- dictionary that maps one-hot-encoding index to character
        file_list -- list of all files used as data
        n_files -- number of files used
        source_length -- total number of characters in all the files
    '''

    def __init__(self,
                 encoding='ascii',
                 decode_errors='ignore',
                 vocabulary=string.printable,
                 sequence_length=100,
                 step_size=1,
                 file_extension='.py',
                 pad_token='\x0c'):
        '''Create a PyCodeVectors object'''
        self.source_directory = None
        self.encoding = encoding
        self.decode_errors = decode_errors
        self.vocabulary = vocabulary
        self.sequence_length = sequence_length
        self.step_size = step_size
        self.file_extension = file_extension
        self.pad_token = pad_token

        self.vocabulary_length = len(self.vocabulary)
        self.char_to_idx, self.idx_to_char = self._generate_mapping(
            self.vocabulary)

        self.file_list = None
        self.n_files = None
        self.source_length = None

    def fit(self, source_directory):
        '''Set the object's data directory'''
        self.file_list = self._generate_filelist(source_directory)
        self.n_files = len(self.file_list)
        self.source = self.concatenate_source_code_parallel(self.file_list)
        self.source_length = len(self.source)

    def transform(self, source_directory, outfile=None, p=1.0):
        '''Convert .py files in source directory to feature and target numpy arrays
           Save serialized numpy arrays to specified outfile'''
        self.source_directory = source_directory
        self.file_list = self._generate_filelist(self.source_directory)
        # self.n_files = len(self.file_list)
        self.n_files = int(p * len(self.file_list))

        code_string = self.concatenate_source_code(
            self.file_list[:self.n_files])

        self.source_length = len(code_string)

        X, y = self.generate_dataset(code_string)

        if outfile:
            if os.path.isdir(os.path.dirname(outfile)):
                np.save(outfile + '_X', X)
                np.save(outfile + '_y', y)

        return X, y

    def _generate_filelist(self, directory):
        '''Create list of .py files in a specified directory'''
        if os.path.isdir(directory):
            file_list = glob.iglob(os.path.join(
                directory, '**', '*' + self.file_extension), recursive=True)
        else:
            raise FileNotFoundError(
                0, 'Folder %s does not exist' % (directory))
        return [f for f in file_list if os.path.isfile(f)]

    def _generate_mapping(self, vocab):
        '''Create mapping of character to index and index to character'''
        idx_to_char = dict(zip(range(len(vocab)), vocab))
        char_to_idx = dict(zip(vocab, range(len(vocab))))

        return char_to_idx, idx_to_char

    def concatenate_source_code(self, file_list):
        '''Concatenate all .py files into a single string'''
        code_string = ''
        for file in file_list:
            with io.open(file, 'r', encoding=self.encoding, errors=self.decode_errors) as infile:
                code_string += self.pad_token * self.sequence_length + infile.read()

        return code_string

    def read_source_code_parallel(self, file):
        '''Helper for parallel concatenation of all .py files into a single string'''
        code_string = ''
        with io.open(file, 'r', encoding=self.encoding, errors=self.decode_errors) as infile:
            code_string += self.pad_token * self.sequence_length + infile.read()
            # return infile.read()
        return code_string

    def concatenate_source_code_parallel(self, file_list):
        '''Concatenate all .py files into a single string using multiple processors'''
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        return ''.join(pool.map(self.read_source_code_parallel, file_list))

    def vectorize(self, code_string):
        '''Non parallel, encode all files as feature and target numpy arrays'''
        source_length = len(code_string)
        n_samples = source_length - self.sequence_length

        X = np.zeros((n_samples, self.sequence_length,
                      self.vocabulary_length), dtype=bool)
        y = np.zeros((n_samples, self.vocabulary_length), dtype=bool)

        for sample_idx in range(n_samples):
            for char_idx in range(self.sequence_length):
                X[sample_idx, char_idx,
                    self.char_to_idx[code_string[sample_idx + char_idx]]] = True
            y[sample_idx, self.char_to_idx[code_string[sample_idx + self.sequence_length]]] = True

        return X, y

    def _vectorize_code_parallel_helper(self, file):
        '''Helper for vectorize_code_parallel'''
        return self.vectorize(self.read_source_code_parallel(file))

    def vectorize_code_parallel(self, file_list):
        '''Use multiple CPUs to encode all files as feature and target numpy arrays'''
        pool = multiprocessing.Pool(multiprocessing.cpu_count())

        Xs, ys = zip(
            *pool.map(self._vectorize_code_parallel_helper, file_list))

        return np.concatenate(Xs, axis=0), np.concatenate(ys, axis=0)

    def generate_dataset(self, code_string):
        source_length = len(code_string)
        n_samples = source_length - self.n_files * self.sequence_length

        X = np.zeros((n_samples, self.sequence_length,
                      self.vocabulary_length), dtype=bool)
        y = np.zeros((n_samples, self.vocabulary_length), dtype=bool)

        sample_idx = 0
        source_idx = 0
        # for sample_idx in range(0, n_samples, step_size):
        while sample_idx < n_samples:  # and source_idx < source_length - seq_length:
            # print(source_idx)
            if code_string[source_idx + self.sequence_length] != self.pad_token:
                for char_idx in range(self.sequence_length):
                    X[sample_idx, char_idx,
                        self.char_to_idx[code_string[source_idx + char_idx]]] = True
                y[sample_idx, self.char_to_idx[code_string[source_idx +
                                                           self.sequence_length]]] = True

                sample_idx += 1
                source_idx += self.step_size
            else:
                source_idx += self.step_size

        return X, y

    def data_generator(self, batch_size, batch_count=None, ignore=['\x0c']):
        '''Batch generator for Keras fit_generator'''
        if batch_count is None:
            batch_count = (self.source_length -
                           self.sequence_length) // batch_size

        print('Generating Data with Batch Size:',
              batch_size, 'Batch Count:', batch_count)

        while True:
            char_idx = 0
            for batch_idx in range(batch_count):
                X = np.zeros((batch_size, self.sequence_length,
                              self.vocabulary_length), dtype=bool)
                y = np.zeros((batch_size, self.vocabulary_length))

                sample_idx = 0
                while sample_idx < batch_size:

                    if self.source[char_idx + self.sequence_length] not in ignore:
                        for seq_pos in range(self.sequence_length):
                            X[sample_idx, seq_pos,
                                self.char_to_idx[self.source[char_idx + seq_pos]]] = True
                        y[sample_idx, self.char_to_idx[self.source[char_idx +
                                                                   self.sequence_length]]] = True
                        sample_idx += 1

                    if char_idx == self.source_length - self.sequence_length - 1:
                        char_idx = 0
                    else:
                        char_idx += 1

                yield X, y
