import sys
import pdb
sys.path.append('..')

from flask import Flask, request, render_template, jsonify

from keras.models import load_model
from keras import Sequential

from pycodecomplete.ml import CharVectorizer
from pycodecomplete.ml import CodeGenerator

app = Flask(__name__.split('.')[0])

char_vec = None
model = None
code_gen = None


@app.before_first_request
def load_objects():
    global char_vec
    global code_gen
    global model

    char_vec = CharVectorizer(sequence_length=100)
    model = load_model('../pycodecomplete/trained-models/rnn')
    code_gen = CodeGenerator(model, char_vec)


@app.route('/', methods=['GET'])
def index():
    return render_template('template.html')


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

    # with open('model.pkl', 'rb') as f:
    #    model = pickle.load(f)

    #prediction = code_gen.predict_n_with_previous(text, 10)
    print('predict')
    return jsonify({'prediction': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
