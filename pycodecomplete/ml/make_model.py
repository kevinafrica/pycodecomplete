# -*- coding: utf-8 -*-
'''make_model.py

This module allows the user to create and train a RNN model. The user can
specifiy a RNN architecture, data file location, pickled model save 
location, and training options.

Example:

    To create and train a new RNN model with 100 character long sequences, 512 
    LSTM nodes per layer, 4 layers, in batches of 512, for 20 epochs, run the
    command:

     $ python make_model.py /path/to/save/pickled/models /path/to/cloned/repos 100 512 1 4 512 20 1

    The arguments are:
        1. Path to save serialized RNN models. A trained model is saves after the completion of each epoch.
        2. Path to the cloned GitHub repositories from which to train the model on
        3. Sequence length (100 character long sequence)
        4. Number of layers (4 layers of LSTM nodes)
        5. Number of nodes per layer (512 nodes per layer)
        6. Number of Epochs to train
        7. Max Queue Size (Number of batches to queue in RAM)

    Additionally you can continue training an existing model with the addition of the -m option:

     $ -m /path/to/existing/model

    and train on a number of GPUs with the -g option:

     $ -g 4

    for a computer with 4 GPUs

Attributes:
    None

Todo:
    * 
'''
import os
import sys
from argparse import ArgumentParser

from keras.models import load_model

from rnn import pyCodeRNNBuilder
from process_text import CharVectorizer


def main():
    parser = ArgumentParser(description='PyCodeComplete model generator')
    parser.add_argument('destination', action='store',
                        help='Destination folder for the trained RNN model')
    parser.add_argument('source', action='store',
                        help='Source folder of .py files that will be used to train the model')
    parser.add_argument('sequence_length', type=int, action='store',
                        help='')
    parser.add_argument('batch_size', type=int, action='store',
                        help='Set batch size')                   
    parser.add_argument('step_size', type=int, action='store',
                        help='')
    parser.add_argument('layers', type=int, action='store',
                        help='')
    parser.add_argument('nodes_per_layer', type=int, action='store',
                        help='')
    parser.add_argument('epochs', type=int, action='store',
                        help='Number of Epochs to train the model')
    parser.add_argument('max_queue_size', type=int, action='store',
                        help='Max queue size')
    parser.add_argument('-s', type=int, action='store', dest='steps_per_epoch',
                        help='Steps per Epochs')                    
    parser.add_argument('-i', type=int, action='store', dest='initial_epoch',
                        help='Set initial epoch < epochs')
    parser.add_argument('-g', type=int, action='store', dest='n_gpu',
                        help='Number of GPUs')
    parser.add_argument('-w', type=int, action='store', dest='n_workers', default=1,
                        help='Number of Workers')                                                       
    parser.add_argument('-m', action='store', dest='initial_model',
                        help='Continue training an existing model')
    parser.add_argument('--multiprocessing', action='store_true',
                        help='Enable Multiprocessing')                                           
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    settings = parser.parse_args()

    if not os.path.isdir(settings.destination):
        arg_error(parser, 'error: Invalid destination folder')
    
    if not os.path.isdir(settings.source):
        arg_error(parser, 'error: Invalid source folder')

    if settings.initial_model:
        if os.path.isfile(settings.initial_model):
            print('Loading Model...')
            pretrained_model = load_model(settings.initial_model)
        else:
            arg_error(parser, 'error: Initial model file not found')
    else:
        pretrained_model = None

    print('Creating Model Trainer...')
    model_builder = pyCodeRNNBuilder(settings.sequence_length,
                                     settings.destination,
                                     settings.source,
                                     n_layers=settings.layers,
                                     hidden_layer_dim=settings.nodes_per_layer,
                                     step_size=settings.step_size,
                                     n_gpu=settings.n_gpu,
                                     model=pretrained_model)

    model_builder.fit(steps_per_epoch=settings.steps_per_epoch,
                      batch_size=settings.batch_size,
                      epochs=settings.epochs,
                      shuffle_source_files=True,
                      max_queue_size=settings.max_queue_size,
                      workers=settings.n_workers)
                      #multiprocessing=settings.multiprocessing)
                      #initial_epoch=settings.initial_epoch)

    
def arg_error(parser, message):
    parser.print_usage()
    print('%s: %s' % (os.path.basename(__file__), message))
    sys.exit()


if __name__ == '__main__':
    main()
