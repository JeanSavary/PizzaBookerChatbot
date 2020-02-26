# import flask dependencies
from flask import Flask, request, make_response, jsonify
import pandas as pd 

# initialize the flask app
app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    if req.get('queryResult').get('intent').get('displayName') == 'GetPizzaWithIngredients':
        is_remover = req.get('queryResult').get('parameters').get('adder') == 'avec'
        ingredients = req.get('queryResult').get('parameters').get('ingredients')
        res = DATA[DATA.is_sugar == is_remover].name.tolist()
        return {'fulfillmentText': u'Les pizzas souhaitées sont : {}'.format(', '.join(res))}

# create a route for webhook
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():

    return make_response(jsonify(results()))

# run the app
if __name__ == '__main__':
    app.run(debug=True)