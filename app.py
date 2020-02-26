# import flask dependencies
from flask import Flask, request, make_response, jsonify

# initialize the flask app
app = Flask(__name__)

# default route
@app.route('/')
def hello_world():
    return 'Hello World!'

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('parameters').get("pizza")

    # return a fulfillment response
    return {'fulfillmentText': u'La pizza qui vous intéresse est : '+str(action)}

# create a route for webhook
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    # return response
    return make_response(jsonify(results()))

# run the app
if __name__ == '__main__':
   app.run(debug=True)