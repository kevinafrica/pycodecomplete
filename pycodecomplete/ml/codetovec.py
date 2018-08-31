import glob
import io
import os
import numpy as np
import string


class PyCodeVectors():

    def __init__(self,
                 encoding='ascii',
                 decode_errors='ignore',
                 vocabulary=string.printable,
                 sequence_length=100,
                 step_size=1,
                 file_extension='.py',
                 pad_token='\x0c'):

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

    def fit(self):
        return self

    def transform(self, source_directory, p=0.5, outfile=None):
        self.source_directory = source_directory
        self.file_list = self._generate_filelist(self.source_directory)
        self.n_files = len(self.file_list)

        print(len(self.file_list[:int(p*self.n_files)]))

        code_string = self.concatenate_source_code(self.file_list[:int(p*self.n_files)])

        self.source_length = len(code_string)

        X, y = self.generate_dataset(code_string)

        if outfile:
            if os.path.isdir(os.path.dirname(outfile)):
                np.save(outfile + '_X', X)
                np.save(outfile + '_y', y)
        
        return X, y
        
    def _generate_filelist(self, directory):
        if os.path.isdir(directory):
            file_list = glob.iglob(os.path.join(
                directory, '**', '*' + self.file_extension), recursive=True)
        else:
            raise FileNotFoundError(
                0, 'Folder %s does not exist' % (directory))
        return [f for f in file_list if os.path.isfile(f)]

    def _generate_mapping(self, vocab):
        idx_to_char = dict(zip(range(len(vocab)), vocab))
        char_to_idx = dict(zip(vocab, range(len(vocab))))

        return char_to_idx, idx_to_char

    def concatenate_source_code(self, file_list):
        code_string = ''
        for file in file_list:
            with io.open(file, 'r', encoding=self.encoding, errors=self.decode_errors) as infile:
                code_string += self.pad_token * self.sequence_length + infile.read()

        return code_string

    def generate_dataset(self, code_string):

        #n_samples = source_length - n_files*seq_length - seq_length
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
