import sys
import pdb
sys.path.append('..')

from flask import Flask, request, render_template, jsonify

from keras.models import load_model
from keras import Sequential

from pycodecomplete.ml.process_text import CharVectorizer
from pycodecomplete.ml.code_generation import CodeGenerator

from argparse import ArgumentParser

app = Flask(__name__.split('.')[0])

parser = ArgumentParser(description='PyCodeComplete WebApp')
parser.add_argument('model_file', action='store',
                    help='Trained RNN model file')
parser.add_argument('predict_n', type=int, action='store',
                    help='Number of characters to predict')
settings = parser.parse_args()

char_vec = None
model = None
code_gen = None


@app.before_first_request
def load_objects():
    global char_vec
    global code_gen
    global model
    char_vec = CharVectorizer(sequence_length=100)
    model = load_model(settings.model_file)
    code_gen = CodeGenerator(model, char_vec)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/pycodecomplete', methods=['GET'])
def pycodecomplete():
    return render_template('index.html')

@app.route('/submit')
def submit():
    return '''
        <!DOCTYPE html><html><head></head>
            <form action="/predict" method='POST' >
                <input type="text" name="user_input" />
                <input type="submit" />
            </form>
        </html>
        '''


@app.route('/predict', methods=['POST'])
def sub_pre_ajax():
    user_data = request.json
    text = str(user_data['text'])

    prediction_1 = code_gen.predict_n_with_previous(
        text, settings.predict_n, diversity=0.1)
    # code_gen.predict_n_with_previous(text, 20, diversity=0.2)
    prediction_2 = None
    # code_gen.predict_n_with_previous(text, 20, diversity=0.5)
    prediction_3 = None
    # code_gen.predict_n_with_previous(text, 20, diversity=1.0)
    prediction_4 = None
    print('predict')
    # return jsonify({'prediction': prediction})
    return jsonify({'prediction_1': prediction_1,
                    'prediction_2': prediction_2,
                    'prediction_3': prediction_3,
                    'prediction_4': prediction_4})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=False)
