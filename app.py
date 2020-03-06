# import flask dependencies
from flask import Flask, request, make_response, jsonify
import pandas as pd 
import Util


# initialize the flask app
app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

# To move into another file within a class


def creation_df_bool_presence(col,list_elements, df, conjonction='addition'):
    """ This function creates a dataFrame with booleans, True if the element (string) is inthe column col (string) of the dataframe d, else false
    It is used for to check is ingredients are within a pizza or not for example """
    nb_element = len(list_elements)
    df_temp = pd.DataFrame(index=df.index)
    for element in list_elements:
        df_temp[element]=df[col].apply(lambda x: True if element in x else False)
    df_temp['sum'] = df_temp.sum(axis=1)
    if conjonction =='addition'
        df_return = pd.DataFrame(df_temp['sum'].apply(lambda x:True if x==nb_element else False)) #all the ingredients are needed to select the pizza
    elif conjonction =='ou':
        df_return = pd.DataFrame(df_temp['sum'].apply(lambda x:True if x==1 else False))  #only one ingredient (to discuss if we gonna switch 'ou' with two sentences 'et')
    return(df_return)

def select_true_column(df_bool, df_data, col_data):
    """ This function takes a df_bool (dataframe, one column with boolean values) and return the list of the values of a selected 
     column of an other dataframe where the row is True in df_bool
     It is used """
    list_return = []
    list_return = [ df_data.loc[i,col_data] for i, element in enumerate (df_bool.iloc[:,0]) if df_bool.iloc[i,0]==True] 
    return (list_return)

def pizza_without_ingredient(self, ingredient, DATA):
    list_pizza = []
    df_copy = deepcopy(DATA)
    df_copy['pizza_ingre'] = df_copy['ingredients'].apply(lambda x: True if ingredient in x else False)
    list_pizza = [ df_copy.loc[i,'name'] for i, element in enumerate (df_copy['pizza_ingre']) if df_copy.loc[i,'pizza_ingre']==False]
    df_copy = df_copy.drop(['pizza_ingre'], axis=1)
    return(list_pizza)

def format_list_for_message_client(list_data):
    list_data_string = list_data.replace('[','')
    list_data_string = list_data_string.replace(']','')
    list_data_string = list_data_string.replace('\'','')
    return (str(list_data_string))

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

                df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                list_pizza = select_true_column(df_bool, DATA, 'ingredients') # call the function which 

                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'ingrédient demandé'}
                elif quantity =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} contient l\'ingrédient {}.'.format(list_pizza[random_pizza], ingredients[0])}

                elif len(list_pizza)==1 and quantity=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec l\'ingrédient {}'.format(list_pizza[0], ingredients[0]}
                elif quantity =='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}'.format(ingredients[0], format_list_for_message_client(list_pizza))}
                
            elif len(ingredients)>1: #there are several ingredients in the list
                conjonction = req.get('queryResult').get('parameters').get('conjonction')
                if conjonction == 'addition' :  #case 'je veux pizza avec salade ET tomate'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                    list_pizza = select_true_column(df_bool, DATA, 'ingredients')

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza avec les ingrédients demandés'}
                    elif quantity =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient les ingrédients {}.'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec les ingrédients {}'.format(list_pizza[0], format_list_for_message_client(ingredients)}
                    elif quantity =='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}'.format(format_list_for_message_client(ingredients), format_list_for_message_client(list_pizza)}

                #elif conjonction == 'ou':  #case 'je veux pizza avec salade OU tomates'


                

                
            


# create a route for webhook
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():

    return make_response(jsonify(results()))

# run the app
if __name__ == '__main__':
    app.run(debug=True)