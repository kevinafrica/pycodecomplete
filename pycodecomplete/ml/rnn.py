import numpy as np
import os
import random
import sys
import io
import string
import time
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Activation, Dense
from process_text import CharVectorizer
from keras.callbacks import LambdaCallback, ModelCheckpoint
from keras.optimizers import RMSprop, Adam
from keras.utils.data_utils import get_file

class pyCodeRNNBuilder():

    def __init__(self, sequence_length, save_pickle_folder, pycode_directory, 
                 vocabulary=string.printable,
                 n_layers=1, hidden_layer_dim=128,
                 dropout=True, dropout_rate=.2, model=None):
        self.sequence_length = sequence_length
        self.vocabulary = vocabulary
        self.vocabulary_size = len(vocabulary)
        self.n_layers = n_layers
        self.hidden_layer_dim = hidden_layer_dim
        self.dropout = dropout
        self.dropout_rate = dropout_rate
        self.save_pickle_folder = save_pickle_folder
        self.save_pickle_path = os.path.join(
            self.save_pickle_folder,
            ('%dx%d_%d-nlayers_%d-hiddenlayerdim_%f-dropout_epoch{epoch:03d}-loss{loss:.4f}-val-loss{val_loss:.4f}_weights'))
        self.model = model

        self.char_vectorizer = CharVectorizer(tokens=self.vocabulary,
                sequence_length=self.sequence_length,
                input='directorypath', encoding='utf-8')
        self.char_vectorizer.fit(pycode_directory)

        self.checkpoint = ModelCheckpoint(
            self.save_pickle_path % (self.sequence_length, self.vocabulary_size,
                        self.n_layers, self.hidden_layer_dim,
                        self.dropout_rate),
            save_weights_only=False
        )

    def build_model(self):
        """Build a Keras sequential model for training the char-rnn"""
        model = Sequential()
        for i in range(self.n_layers):
            model.add(
                LSTM(
                    self.hidden_layer_dim, 
                    return_sequences = True if (i != (self.n_layers - 1)) else False,
                    input_shape=(self.sequence_length, self.vocabulary_size)
                )
            )
            if self.dropout:
                model.add(Dropout(self.dropout_rate))
        
        model.add(Dense(self.vocabulary_size))
        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy', optimizer="adam")

        self.model = model

        return model

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def on_epoch_end(self, epoch, logs):
        # Function invoked at end of each epoch. Prints generated text.

        text=' '
        print()
        print('----- Generating text after Epoch: %d' % epoch)

        start_index = random.randint(0, len(text) - self.char_vectorizer.sequence_length - 1)
        for diversity in [0.2, 0.5, 1.0, 1.2]:
            print('----- diversity:', diversity)

            generated = ''
            sentence = text[start_index: start_index + self.char_vectorizer.sequence_length]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(400):
                x_pred = np.zeros((1, self.char_vectorizer.sequence_length, len(self.char_vectorizer.tokens)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, self.char_vectorizer.char_indices[char]] = 1.

                preds = self.model.predict(x_pred, verbose=0)[0]
                next_index = self.sample(preds, diversity)
                next_char = self.char_vectorizer.indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()


    def fit(self, steps_per_epoch=None, max_queue_size=1,
            epochs=5, initial_epoch=0, validation_steps=None):

        if steps_per_epoch is None:
            steps_per_epoch = self.char_vectorizer.steps_per_epoch
        
        if validation_steps is None:
            validation_steps = 1

        self.model.fit_generator(
            generator=self.char_vectorizer.batch_generator(),
            steps_per_epoch=steps_per_epoch,
            max_queue_size=max_queue_size,
            epochs=epochs,
            initial_epoch=initial_epoch,
            verbose=1,
            validation_data=self.char_vectorizer.batch_generator(),
            validation_steps=validation_steps,
            callbacks=[self.checkpoint])


    