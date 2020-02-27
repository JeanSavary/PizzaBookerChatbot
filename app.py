# import flask dependencies
from flask import Flask, request, make_response, jsonify
import pandas as pd 
import Util


# initialize the flask app
app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

# To move into another file within a class
def pizza_with_ingredient(self, ingredient, DATA):
        list_pizza = []
        df_copy = deepcopy(DATA)
        df_copy['pizza_ingre'] = df_copy['ingredients'].apply(lambda x: True if ingredient in x else False)
        list_pizza = [ df_copy.loc[i,'name'] for i, element in enumerate (df_copy['pizza_ingre']) if df_copy.loc[i,'pizza_ingre']==True]
        df_copy = df_copy.drop(['pizza_ingre'], axis=1)
    return(list_pizza)

    def pizza_without_ingredient(self, ingredient, DATA):
        list_pizza = []
        df_copy = deepcopy(DATA)
        df_copy['pizza_ingre'] = df_copy['ingredients'].apply(lambda x: True if ingredient in x else False)
        list_pizza = [ df_copy.loc[i,'name'] for i, element in enumerate (df_copy['pizza_ingre']) if df_copy.loc[i,'pizza_ingre']==False]
        df_copy = df_copy.drop(['pizza_ingre'], axis=1)
        return(list_pizza)


# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    if req.get('queryResult').get('intent').get('displayName') == 'GetPizzaWithIngredients':  #If the client ask for a pizza which conatains a list of ingredients
        is_remover = req.get('queryResult').get('parameters').get('ingredient-modification')   # several values ('avec', 'sans', 'enlever', 'ajouter') just the two first values are useful here
        #ingredients_ = req.get('queryResult').get('parameters').get('ingredients')  #list of string, required entity
        ingredients = req.get('queryResult').get('outputContexts').get('ingredients.original') #list of string
        quantity = req.get('queryResult').get('parameters').get('quantity') #string, not required entity, possible values : 'singulier', 'pluriel'
        list_pizza = []  # list of pizzas which will match to the request (with/without ingredients)
        print(ingredients)
        if is_remover=='avec' :
            if len(ingredients)==1: #just for one ingredient
                list_pizza = pizza_with_ingredient(ingredients)
                if quantity =='singulier':  #client wants to know just one pizza with the ingredients
                    try:
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient l\'ingrédient {}.'.format(list_pizza[random_pizza], ingredients[0])}
                    except:
                        return {'fulfillmentText': u'Il n\'y a pas de pizza avec cet ingrédient.'}
                elif quantity =='pluriel':
                    list_pizza_string = list_pizza.replace('[','')
                    list_pizza_string = list_pizza_string.replace(']','')
                    list_pizza_string = list_pizza_string.replace('\'','')
                    return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}'.format(ingredients[0], list_pizza_string)}
            


# create a route for webhook
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():

    return make_response(jsonify(results()))

# run the app
if __name__ == '__main__':
    app.run(debug=True)