from flask import Flask, request, render_template, jsonify
from keras.models import load_model
import pickle

app = Flask(__name__)

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

@app.route('/submit-predict', methods=['POST'])
def sub_pre_ajax():
    user_data = request.json
    text = str(user_data['text'])

    #with open('model.pkl', 'rb') as f:
    #    model = pickle.load(f)
        
    #prediction = str(model.predict([text])[0])

    return jsonify({'prediction': text})

@app.route('/predict', methods=['POST'])
def predict():
    text = str(request.form['user_input'])

    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    prediction = model.predict([text])[0] 

    return f'''
        <!DOCTYPE html>
        <html>
            <head>
            </head>
            <body>
                {prediction}
            </body>
        </html>'''
        

def welcome_page():
    return '''
        <!DOCTYPE html>
        <html>
            <head>
            </head> 
            <body>
                <a href="/submit">Submit text data</a>
                <a href="/submit-predict">Submit text data with Ajax!</a>
            </body>
        </html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
