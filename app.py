from flask import Flask, request, make_response, jsonify
import pandas as pd 
import numpy as np
from copy import deepcopy
from utils import creation_df_bool_presence, select_bool_column, pizza_without_ingredient, format_list_for_message_client

app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

def results():

    req = request.get_json(force=True)

    # --- GetPizzaComposition intent section

    if req.get('queryResult').get('intent').get('displayName') == 'GetPizzaComposition':
        pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        df_bool = creation_df_bool_presence('name', pizza, DATA )
        
        if len(df_bool['sum'].unique())==1: #only false, so the name of the pizza doesn t exist
            return {'fulfillmentText': u'Nous sommes désolé, n\'avons pas cette pizza.'}

        elif len(df_bool['sum'].unique())==2: #there are True and False so the pizza is in the menu
            index_pizza = df_bool.loc[df_bool['sum']==True].index[0]    
            str_ingredients = DATA.loc[index_pizza, "ingredients"]
            
            return {'fulfillmentText': u'La {} contient les ingrédients {}.'.format(format_list_for_message_client(pizza),str_ingredients)}
    
    # --- GetPizzaWithIngredients intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaWithIngredients': 
        is_remover = req.get('queryResult').get('parameters').get('ingredient-modification')[0]   # several values ('avec', 'sans', 'enlever', 'ajouter') just the two first values are useful here
        ingredients = req.get('queryResult').get('outputContexts')[0].get('parameters').get('ingredients.original')
        quantity = req.get('queryResult').get('parameters').get('quantity') #string, not required entity, possible values : 'singulier', 'pluriel'
        list_pizza = []  # list of pizzas which will match to the request (with/without ingredients)
        
        if len(quantity)==0:  # case the quantity hasn't been tagged by dialogflow, it is set to plurial automatically
            quantity = ["pluriel"]
        
        if is_remover=='avec' : 
            if len(ingredients) == 1: #just for one ingredient

                df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                list_pizza = select_bool_column(df_bool, DATA, 'name', True) # call the function which 
                
                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'ingrédient demandé'}

                elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} contient l\'ingrédient {}.'.format(list_pizza[random_pizza], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec l\'ingrédient {}'.format(list_pizza[0], ingredients[0])}

                elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}'.format(ingredients[0], format_list_for_message_client(list_pizza))}
                
            elif len(ingredients)>1: #there are several ingredients in the list
                conjonction = req.get('queryResult').get('parameters').get('conjonction')

                if conjonction[0] == 'addition' :  #case 'je veux pizza avec salade ET tomate'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                    list_pizza = select_bool_column(df_bool, DATA, 'name', True)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza avec les ingrédients demandés'}

                    elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient les ingrédients {}.'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec les ingrédients {}'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}'.format(format_list_for_message_client(ingredients), format_list_for_message_client(list_pizza))}

                elif conjonction[0]== 'ou':  #case 'je veux pizza avec salade OU tomates'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA, conjonction='ou')
                    list_pizza = select_bool_column(df_bool, DATA, 'name', True)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'un des ingrédients demandés'}

                    elif quantity[0]=='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient au moins un des ingrédients {}.'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec un des ingrédients {}'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas avec au moins un des ingrédients {} sont {}'.format(format_list_for_message_client(ingredients), format_list_for_message_client(list_pizza))}

        elif is_remover=='sans' :  #the client wants to know if there is pizza(s) without ingredient(s)
            if len(ingredients)==1: #just for one ingredient

                df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                list_pizza = select_bool_column(df_bool, DATA, 'name', False) # call the function which selects the rows(pizzas) where there isn't the ingredient

                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza sans l\'ingrédient demandé'}

                elif quantity[0]=='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza without the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} ne contient pas l\'ingrédient {}.'.format(list_pizza[random_pizza], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} sans l\'ingrédient {}'.format(list_pizza[0], ingredients[0])}

                elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas sans l\'ingrédient {} sont {}'.format(ingredients[0], format_list_for_message_client(list_pizza))}
                
            elif len(ingredients)>1: #there are several ingredients in the list
                conjonction = req.get('queryResult').get('parameters').get('conjonction') 
                # We supposed there is no possibility that the conjonction would be 'ou' : 'je veux des pizzas sans tomates ou poivrons'
                
                if conjonction[0] == 'addition' :  #case 'je veux pizza sans salade ET tomate'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                    list_pizza = select_bool_column(df_bool, DATA, 'name', False)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza sans les ingrédients demandés'}

                    elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} ne contient pas les ingrédients {}.'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} sans les ingrédients {}'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas sans l\'ingrédient {} sont {}'.format(format_list_for_message_client(ingredients),format_list_for_message_client(list_pizza))}
    
    # --- GetPizzaInfo intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaInfo': 
        
        req_parameters = req.get('queryResult').get('parameters')
        req_output_contexts = req.get('queryResult').get('outputContexts')[0].get('parameters')

        req_is_pizza = len(req_parameters.get('meals')) == 0
        print(req_is_pizza)

        if req_is_pizza : 
            if req_output_contexts.get('pizza-type.original')[0] in ['pizza', 'pizzas'] :
                return {'fulfillmentText': u'Oui biensûr ! Nous sommes spécialisés dans les pizzas 🍕Souhaitez-vous commander ?'}
            
            else :
                pizza_type = req_output_contexts.get('pizza-type.original')[0]
                print(' '.join(map(lambda x : x.capitalize() , pizza_type.split())))
        else :
            return {'fulfillmentText': u'Malheureusement nous ne faisons pas ce type de plat ! Cependant, nous sommes spécialisés dans la confection de délicieuses pizzas !🍕Souhaitez-vous commander ?'}

    # --- PizzaModification intent section

    # to do : update du dictionnaire order, afin de tenir compte des modifications d'ingrédients
        

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    return make_response(jsonify(results()))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

    #curl -X POST -H ': ' -H 'Content-Type: application/json' -d '{"responseId":"e6b8e926-a90c-4e12-87db-934f604933f1-dd2bbea9","queryResult":{"queryText":"Faites vous des pizzas 4 fromages","parameters":{"pizza-type":["pizzas 4 fromages"],"question":["Faites vous"],"number":"","meals":[]},"allRequiredParamsPresent":true,"outputContexts":[{"name":"projects/imta-256108/agent/sessions/0d91c908-c202-dd53-a51a-a6cccab52cc6/contexts/getpizzainfo-followup","lifespanCount":2,"parameters":{"question":["Faites vous"],"question.original":["Faites vous"],"meals":[],"meals.original":[],"number":"","number.original":"","pizza-type":["pizzas 4 fromages"],"pizza-type.original":["pizzas 4 fromages"]}},{"name":"projects/imta-256108/agent/sessions/0d91c908-c202-dd53-a51a-a6cccab52cc6/contexts/initial-customer-needs","lifespanCount":4,"parameters":{"question":["Faites vous"],"question.original":["Faites vous"],"meals":[],"meals.original":[],"number":"","number.original":"","pizza-type":["pizzas 4 fromages"],"pizza-type.original":["pizzas 4 fromages"]}},{"name":"projects/imta-256108/agent/sessions/0d91c908-c202-dd53-a51a-a6cccab52cc6/contexts/__system_counters__","parameters":{"no-input":0,"no-match":0,"pizza-type":["pizzas 4 fromages"],"pizza-type.original":["pizzas 4 fromages"],"question":["Faites vous"],"question.original":["Faites vous"],"number":"","number.original":"","meals":[],"meals.original":[]}}],"intent":{"name":"projects/imta-256108/agent/intents/226477a4-941d-4d7f-9766-ffe4517e4425","displayName":"GetPizzaInfo"},"intentDetectionConfidence":0.83716905,"languageCode":"fr"},"originalDetectIntentRequest":{"payload":{}},"session":"projects/imta-256108/agent/sessions/0d91c908-c202-dd53-a51a-a6cccab52cc6"}' http://127.0.0.1:5000/webhook