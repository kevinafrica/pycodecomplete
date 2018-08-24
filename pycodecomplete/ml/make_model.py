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
    parser.add_argument('step_size', type=int, action='store',
                        help='')
    parser.add_argument('layers', type=int, action='store',
                        help='')
    parser.add_argument('nodes_per_layer', type=int, action='store',
                        help='')
    parser.add_argument('epochs', type=int, action='store',
                        help='Number of Epochs to train the model')
    parser.add_argument('steps_per_epoch', type=int, action='store',
                        help='Steps per Epochs')
    parser.add_argument('-i', type=int, action='store', dest='initial_epoch',
                        help='Set initial epoch < epochs')
    parser.add_argument('-m', action='store', dest='initial_model',
                        help='Continue training an existing model')                       
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    settings = parser.parse_args()

    if not os.path.isdir(settings.destination):
        arg_error(parser, 'error: Invalid destination folder')
    
    if not os.path.isdir(settings.source):
        arg_error(parser, 'error: Invalid source folder')

    if settings.initial_model and not os.path.isfile(settings.initial_model):
        arg_error(parser, 'error: Initial model file not found')

    print('Creating Vectorizer...')
    ch_vec = CharVectorizer(sequence_length=settings.sequence_length,
                            step_size=settings.step_size)

    if settings.initial_model:
        print('Loading Model...')
        pretrained_model = load_model(settings.initial_model)
    else:
        pretrained_model = None

    print('Creating Model Trainer...')
    model_builder = pyCodeRNNBuilder(settings.sequence_length,
                                     settings.destination,
                                     settings.source,
                                     n_layers=settings.layers,
                                     hidden_layer_dim=nodes_per_layer,
                                     model=pretrained_model)

    


    

    print(settings.destination)

def arg_error(parser, message):
    parser.print_usage()
    print(f'{os.path.basename(__file__)}: {message}')
    sys.exit()


if __name__ == '__main__':
    main()
