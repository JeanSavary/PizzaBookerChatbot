from flask import Flask, request, make_response, jsonify
import pandas as pd 
import numpy as np
from copy import deepcopy
from utils import creation_df_bool_presence, select_bool_column, pizza_without_ingredient, format_list_for_message_client, format_dict_booking, search_by_name

app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

order = {}  # dict which stores the order of the client. Pizza names as keys and quantity as values. If the ingredients of the pizza are modified, the name of the pizza will be modified 'pizza bougar sans fromage'

def results():

    global order
    req = request.get_json(force=True)

    # --- GetPizzaComposition intent section

    if req.get('queryResult').get('intent').get('displayName') == 'GetPizzaComposition':
        pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        df_bool = creation_df_bool_presence('name', pizza, DATA )
        
        if len(df_bool['sum'].unique())==1: #only false, so the name of the pizza doesn t exist
            return {'fulfillmentText': u'Nous sommes désolé, n\'avons pas cette pizza. mais nous faisons différents types de pizzas. Voulez-vous commander ?'}

        elif len(df_bool['sum'].unique())==2: #there are True and False so the pizza is in the menu
            index_pizza = df_bool.loc[df_bool['sum']==True].index[0]    
            str_ingredients = DATA.loc[index_pizza, "ingredients"]
            
            return {'fulfillmentText': u'La {} contient les ingrédients {}. Voulez-vous commander ?'.format(format_list_for_message_client(pizza),str_ingredients)}
    
    # --- GetPizzaWithIngredients intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaWithIngredients': 
        try:
            is_remover = req.get('queryResult').get('parameters').get('ingredient-modification')[0]   # several values ('avec', 'sans', 'enlever', 'ajouter') just the two first values are useful here
        except : 
            is_remover = "avec"
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
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'ingrédient demandé. Mais nous faisons différents types de pizzas, souhaitez-vous commander ?'}

                elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} contient l\'ingrédient {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec l\'ingrédient {}.\nSouhaitez-vous commander ?'.format(list_pizza[0], ingredients[0])}

                elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}. \nSouhaitez-vous commander ?'.format(ingredients[0], format_list_for_message_client(list_pizza))}
                
            elif len(ingredients)>1: #there are several ingredients in the list
                conjonction = req.get('queryResult').get('parameters').get('conjonction')

                if conjonction==[] or conjonction[0] == 'addition' :  #case 'je veux pizza avec salade ET tomate'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                    list_pizza = select_bool_column(df_bool, DATA, 'name', True)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza avec les ingrédients demandés, mais nous faisons différents types de pizzas. Voulez-vous commander ?'}

                    elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient les ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec les ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas avec l\'ingrédient {} sont {}. Souhaitez-vous commander ?'.format(format_list_for_message_client(ingredients), format_list_for_message_client(list_pizza))}

                elif conjonction[0]== 'ou':  #case 'je veux pizza avec salade OU tomates'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA, conjonction='ou')
                    list_pizza = select_bool_column(df_bool, DATA, 'name', True)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'un des ingrédients demandés mais nous faisons différents types de pizzas. Voulez-vous commander ?'}

                    elif quantity[0]=='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} contient au moins un des ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} avec un des ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas avec au moins un des ingrédients {} sont {}. Souhaitez-vous commander ?'.format(format_list_for_message_client(ingredients), format_list_for_message_client(list_pizza))}

        elif is_remover=='sans' :  #the client wants to know if there is pizza(s) without ingredient(s)
            if len(ingredients)==1: #just for one ingredient

                df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                list_pizza = select_bool_column(df_bool, DATA, 'name', False) # call the function which selects the rows(pizzas) where there isn't the ingredient

                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza sans l\'ingrédient demandé mais nous faisons différents types de pizzas. Voulez-vous commander ?'}

                elif quantity[0]=='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza without the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} ne contient pas l\'ingrédient {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} sans l\'ingrédient {}. Souhaitez-vous commander ?'.format(list_pizza[0], ingredients[0])}

                elif quantity[0]=='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas sans l\'ingrédient {} sont {}. Souhaitez-vous commander ?'.format(ingredients[0], format_list_for_message_client(list_pizza))}
                
            elif len(ingredients)>1: #there are several ingredients in the list
                conjonction = req.get('queryResult').get('parameters').get('conjonction') 
                # We supposed there is no possibility that the conjonction would be 'ou' : 'je veux des pizzas sans tomates ou poivrons'
                
                if conjonction== [] or conjonction[0] == 'addition' :  #case 'je veux pizza sans salade ET tomate'
                    df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                    list_pizza = select_bool_column(df_bool, DATA, 'name', False)

                    if len(list_pizza)==0 :
                        return {'fulfillmentText': u'Nous n\'avons pas de pizza sans les ingrédients demandés mais nous faisons différents types de pizzas. Voulez-vous commander ?'}

                    elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                        random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                        return {'fulfillmentText': u'La {} ne contient pas les ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], format_list_for_message_client(ingredients))}

                    elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                        return {'fulfillmentText': u'Nous avons uniquement la pizza {} sans les ingrédients {}. Souhaitez-vous commander ?'.format(list_pizza[0], format_list_for_message_client(ingredients))}

                    elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                        return {'fulfillmentText': u'Les pizzas sans l\'ingrédient {} sont {}. Souhaitez-vous commander ?'.format(format_list_for_message_client(ingredients),format_list_for_message_client(list_pizza))}
    
    # --- GetPizzaInfo intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaInfo': 

        req_parameters = req.get('queryResult').get('parameters')
        req_output_contexts = req.get('queryResult').get('outputContexts')[0].get('parameters')

        req_is_pizza = len(req_parameters.get('meals')) == 0

        if req_is_pizza : 
            if req_output_contexts.get('pizza-type.original')[0] in ['pizza', 'pizzas'] :
                return {'fulfillmentText': u'Oui biensûr ! Nous sommes spécialisés dans les pizzas 🍕Souhaitez-vous commander ?'}
            
            else :
                pizza_type = req_output_contexts.get('pizza-type.original')[0]
                res = search_by_name(DATA, pizza_type)
                return {'fulfillmentText': u'Parfaitement, nous proposons cette pizza !\n Voici sa description : {description}.\n\n Souhaitez-vous la commander ?'.format(description = res.description.tolist()[0])}

        else :
            return {'fulfillmentText': u'Malheureusement nous ne faisons pas ce type de plat ! Cependant, nous sommes spécialisés dans la confection de délicieuses pizzas !🍕Souhaitez-vous commander ?'}
    
    # --- Booking intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'Booking':
        order = {}
        list_pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        list_quantity_pizza = req.get('queryResult').get('parameters').get('number')
        
        print(list_quantity_pizza)

        for i, pizza in enumerate(list_pizza):
            try : 
                db_pizza_name = search_by_name(DATA, pizza).name.tolist()[0]
                order[db_pizza_name] = int(list_quantity_pizza[i])
            
            except : 
                return {'fulfillmentText': u'Veuillez vous assurer que le(s) nom(s) des éléments de votre commande sont corrects. Essayez de nouveau !'}
        
        print("Order → ", order)

        return {'fulfillmentText': u'Très bien, nous avons enregistré votre commande, qui est {}. Souhaitez-vous modifier la composition de pizza(s) ?'.format(format_dict_booking(order))}

    # --- AddIngredients intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'AddIngredients':
        ingredient_to_add = req.get('queryResult').get('outputContexts')[0].get('parameters').get('ingredients.original')
        pizza_to_modify = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')

        print(pizza_to_modify, ingredient_to_remove)

        pizza_to_modify = search_by_name(DATA, pizza_to_modify).name.tolist()[0]

        try :
            order[pizza_to_modify] -= 1
            if order[pizza_to_modify] == 0 :
                del order[pizza_to_modify]

            order[pizza_to_modify + ' avec %s'%ingredient_to_add] = 1

            print('Modification applied : {}'.format(order))

            return {'fulfillmentText': u"Vous venez de modifier une {}. Souhaitez-vous modifier la composition d'une autre pizza (si oui précisez le type de modification, le nom de la pizza et l'ingrédient en question) ou bien passer à la validation de votre commande.".format(pizza_to_modify)}

        except :
            return {'fulfillmentText': u"Votre commande ne contient pas la {}. Veuillez sélectionner une pizza déjà présente dans votre commande.".format(pizza_to_modify)}
        
    # --- RemoveIngredients intent section
    
    elif req.get('queryResult').get('intent').get('displayName') == 'RemoveIngredients':
        
        ingredient_to_remove = req.get('queryResult').get('outputContexts')[0].get('parameters').get('ingredients.original')
        pizza_to_modify = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')

        print(pizza_to_modify, ingredient_to_remove)

        pizza_to_modify = search_by_name(DATA, pizza_to_modify).name.tolist()[0]

        try :
            order[pizza_to_modify] -= 1
            if order[pizza_to_modify] == 0 :
                del order[pizza_to_modify]

            order[pizza_to_modify + ' sans %s'%ingredient_to_add] = 1

            print('Modification applied : {}'.format(order))

            return {'fulfillmentText': u"Vous venez de modifier une {}. Souhaitez-vous modifier la composition d'une autre pizza (si oui précisez le type de modification, le nom de la pizza et l'ingrédient en question) ou bien passer à la validation de votre commande.".format(pizza_to_modify)}

        except :
            return {'fulfillmentText': u"Votre commande ne contient pas la {}. Veuillez sélectionner une pizza déjà présente dans votre commande.".format(pizza_to_modify)}

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    return make_response(jsonify(results()))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
