from flask import Flask, request, make_response, jsonify
import pandas as pd 
import numpy as np
from copy import deepcopy
from utils import creation_df_bool_presence, select_bool_column, pizza_without_ingredient, format_list_for_message_client, format_dict_booking, search_by_name, bool_pizza_in_list_pizza, set_plurial_singular

app = Flask(__name__)
DATA = pd.read_csv('data/pizzas.csv', sep = ';')

order = {}  # dict which stores the order of the client. Pizza names as keys and quantity as values. If the ingredients of the pizza are modified, the name of the pizza will be modified 'pizza bougar sans fromage'

def results():

    global order
    req = request.get_json(force=True)

    # --- GetPizzaComposition intent section

    if req.get('queryResult').get('intent').get('displayName') == 'GetPizzaComposition':
        pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')[0]
        db_pizza, code = search_by_name(DATA, pizza)

        if code == 404 :
            return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

        elif code == 400 : 
            return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

        elif code == 200 :
            db_pizza_name = db_pizza['name']
            db_pizza_ingredients = db_pizza['ingredients']
        
            return {'fulfillmentText' : u"Les ingrédients de la {name} sont les suivants : {ingredients}. Souhaitez-vous la commandée ?".format(name = db_pizza_name, ingredients = db_pizza_ingredients)}

    # --- GetPizzaWithIngredients intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaWithIngredients': 
        try :
            is_remover = req.get('queryResult').get('parameters').get('ingredient-modification')[0]   # several values ('avec', 'sans', 'enlever', 'ajouter') just the two first values are useful here
        except : 
            is_remover = "avec"
        ingredients = req.get('queryResult').get('outputContexts')[0].get('parameters').get('ingredients.original')
        quantity = req.get('queryResult').get('parameters').get('quantity') #string, not required entity, possible values : 'singulier', 'pluriel'
        list_pizza = []  # list of pizzas which will match to the request (with/without ingredients)
        gout = req.get('queryResult').get('parameters').get('gouts')
        print("gout", gout)
        if len(quantity)==0:  # case the quantity hasn't been tagged by dialogflow, it is set to plurial automatically
            quantity = ["pluriel"]
        

        elif ingredients == [] and gout ==[] : # So the client asks without specifing the ingredients ("quelles sont vos pizzas") so we reply with a list
            return {'fulfillmentText': u'Je n\'ai pas très bien compris sur quel ingrédient portait votre question. Nous avons différents types de pizzas : des pizzas avec de la viande comme la Carbonara ou la Royale; des pizzas végétariennes comme la\
                                        Pizza aux Artichauts ou encore des pizzas sucrées, notamment la Pizza Petite Fermière. Souhaitez-vous commander ?'}
        
        
        elif ingredients==[] and len(gout)==1 :  # if the client asks for a taste, like 'quelles sont vos pizzas sucrées ?'
            df_bool = creation_df_bool_presence('ingredients',gout, DATA)
            list_pizza = select_bool_column(df_bool, DATA, 'name', True) # call the function which 
            
            if len(list_pizza)==0 :
                return {'fulfillmentText': u'Nous n\'avons pas de pizza comme vous avez demandé. Mais nous faisons différents types de pizzas avec de la viande (Royale, Carbonara), végétariennes (Pizza Hawaïenne) ou encore sucrées (Petite Fermière). Souhaitez-vous commander ?'}

            elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                return {'fulfillmentText': u'La {} est {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], gout[0])}

            elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                return {'fulfillmentText': u'Nous avons uniquement la pizza {} qui est {}.\nSouhaitez-vous commander ?'.format(list_pizza[0], gout[0])}

            elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                return {'fulfillmentText': u'Les pizzas {} sont {}. \nSouhaitez-vous commander ?'.format(gout[0]+'s', format_list_for_message_client(list_pizza))}
                
        elif ingredients==[] and len(gout)>=2: #if the client asks for several tastes like 'pizzas sucrées et végétariennes'
            return {'fulfillmentText': u'N\'en demandez pas trop d\'un coup ! Choississez une seule caractéristique.'}


        elif len(ingredients)==1 and len(gout)==1 :  # if the client asks for a taste, like 'quelles sont vos pizzas sucrées ?'
            if is_remover=='avec' :
                df_bool = creation_df_bool_presence('ingredients',gout+ingredients, DATA)  
                list_pizza = select_bool_column(df_bool, DATA, 'name', True) # call the function which 
                
                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza comme vous avez demandé. Mais nous faisons différents types de pizzas avec de la viande (Royale, Carbonara), végétariennes (Pizza Hawaïenne) ou encore sucrées (Petite Fermière). Souhaitez-vous commander ?'}

                elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} est {} avec l\'ingrédient {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], gout[0], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} qui est {} avec l\'ingrédient {}.\nSouhaitez-vous commander ?'.format(list_pizza[0], gout[0], ingredients[0])}

                elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas qui sont {} avec l\'ingrédient {} sont {}. \nSouhaitez-vous commander ?'.format(gout[0]+'s', ingredients[0], format_list_for_message_client(list_pizza))}
                    
            elif is_remover=='sans' :
                df_bool = creation_df_bool_presence('ingredients',gout+ingredients, DATA)  #concat the 2 lists
                list_pizza = select_bool_column(df_bool, DATA, 'name', True) # call the function which 
                
                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza comme vous avez demandé. Mais nous faisons différents types de pizzas avec de la viande (Royale, Carbonara), végétariennes (Pizza Hawaïenne) ou encore sucrées (Petite Fermière). Souhaitez-vous commander ?'}

                elif quantity[0] =='singulier' and len(list_pizza)>=1:  #client wants to know just one pizza with the ingredient
                    random_pizza = np.random.randint(0, len(list_pizza)) #random int to not always have the first pizzas returned 
                    return {'fulfillmentText': u'La {} est {} et sans l\'ingrédient {}. Souhaitez-vous commander ?'.format(list_pizza[random_pizza], gout[0], ingredients[0])}

                elif len(list_pizza)==1 and quantity[0]=='pluriel': #just one pizza whereas the client asks for several pizzas
                    return {'fulfillmentText': u'Nous avons uniquement la pizza {} qui est {} sans l\'ingrédient {}.\nSouhaitez-vous commander ?'.format(list_pizza[0], gout[0], ingredients[0])}

                elif quantity[0] =='pluriel' and len(list_pizza)>=2:
                    return {'fulfillmentText': u'Les pizzas qui sont {} sans l\'ingrédient {} sont {}. \nSouhaitez-vous commander ?'.format(gout[0]+'s', ingredients[0], format_list_for_message_client(list_pizza))}
                            

        elif is_remover=='avec' and gout==[] : 
            if len(ingredients) == 1 : #just for one ingredient

                df_bool = creation_df_bool_presence('ingredients',ingredients, DATA)
                list_pizza = select_bool_column(df_bool, DATA, 'name', True) # call the function which 
                
                if len(list_pizza)==0 :
                    return {'fulfillmentText': u'Nous n\'avons pas de pizza avec l\'ingrédient demandé, mais nous faisons différents types de pizzas, par exemple avec de la viande (Royale, Carbonara), végétariennes (Pizza Hawaïenne) ou encore sucrées (Petite Fermière). Souhaitez-vous commander ?'}

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


        elif is_remover=='sans' and gout==[] :  #the client wants to know if there is pizza(s) without ingredient(s)
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
    

    # --- GetPizzaMenu intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'GetPizzaMenu':
        
        is_advice = req.get('queryResult').get('parameters').get('advices')
        is_pizza = req.get('queryResult').get('parameters').get('pizza-type')
        
        # User ask about best pizzas, or ask for an advice. We will consider this as the same situation.
        if is_advice and is_pizza : 
            return {'fulfillmentText' : u"Les pizzas les plus appréciées sont les suivantes : la Royale (un classique), la 4 Fromages (grâce à la qualité de nos fromages) et la Petite Fermière (osez vous verrez 😋). Nous vous les recommendons fortement ! Souhaitez-vous commander l'une de ses pizzas ?"}

        # User either ask for the menu, or ask which pizzas are available. This results in the same answer from us.
        elif (is_advice and not is_pizza) or (not is_advice and is_pizza) :
            return {'fulfillmentText' : u"53 pizzas sont disponibles dans notre restaurant. Voici une liste non exhaustive de nos pizzas favorites : la Royale, la Savoyarde, la Regina, la 4 Fromages, nos Calzones (Rustico ou au Prosciutto), et bien d'autres ! Rendez-vous dans l'onglet 'Menu' pour plus de détails."}

        else :    
            return {'fulfillmentText' : u"Je ne peux répondre à votre demande. Je n'ai pas encore été entraîné pour cela."}
        # Gestion des conseils


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
                res, code = search_by_name(DATA, pizza_type)

                if code == 404 :
                    return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

                elif code == 400 : 
                    return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

                elif code == 200 : 
                    return {'fulfillmentText': u'Parfaitement, nous proposons cette pizza !\n Voici sa description : {description}.\n\n Souhaitez-vous la commander ?'.format(description = res['description'])}

        else :
            return {'fulfillmentText': u'Malheureusement nous ne faisons pas ce type de plat ! Cependant, nous sommes spécialisés dans la confection de délicieuses pizzas !🍕Souhaitez-vous commander ?'}
    
    # --- Booking intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'Booking':
        order = {}
        list_pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        list_quantity_pizza = req.get('queryResult').get('parameters').get('number')
        unknown_quantity = req.get('queryResult').get('parameters').get('quantity')

        #if the client doesn't specify the pizza name, we need to ask him
        if bool_pizza_in_list_pizza(list_pizza)==True : 
            
            # "je veux commander 3 pizzas" or "je veux commander des pizzas" so we need to know the names of the pizzas and the number of each pizza-type
            if (len(list_quantity_pizza)>=1 and list_quantity_pizza[0]>1) or (len(list_quantity_pizza)==0 and unknown_quantity=='pluriel'): 
                return {'fulfillmentText': u'Très bien, quelles pizzas voulez-vous ?'}

            # "je veux commander 1 pizza" so we need to know the names of the pizzas
            elif (len(list_quantity_pizza)>=1 and list_quantity_pizza[0]==1) or ( len(list_quantity_pizza)==0 and unknown_quantity=='singulier'): 
                return {'fulfillmentText': u'Très bien, quelle pizza voulez commander?'}

        #if the client just asks "je veux commander"
        if len(list_pizza)==0 and len(list_quantity_pizza)==0:
            return {'fulfillmentText': u'Très bien, quelle sera votre commande ?'}

        elif len(list_pizza)==0 and len(list_quantity_pizza)>=1: #if the clients forgets to specify the pizza name
            return {'fulfillmentText': u'Pardon, je n\'ai pas bien compris, quelle pizza et combien en voulez-vous ?'}

        elif len(list_pizza)>=1 and len(list_quantity_pizza)==0: #if the clients forgets to specify the quantity
            if len(list_pizza)==1 and unknown_quantity=='singulier':
                list_quantity_pizza=[1]
            else:
                return {'fulfillmentText': u'Pardon, je n\'ai pas bien compris, quelle pizza et combien en voulez-vous ?'}
        
        #if the client has well specified the name of the pizza, we search them in the database
        if len(list_pizza)==len(list_quantity_pizza):
            for i, pizza in enumerate(list_pizza):
                db_pizza_name, code = search_by_name(DATA, pizza)
            
                if code == 404 :
                    return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

                elif code == 400 : 
                    return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

                elif code == 200 : 
                    db_pizza_name = db_pizza_name['name']
                    try :
                        if list_quantity_pizza[i]>=1: #to avoid float or negative number
                            order[db_pizza_name] = int(list_quantity_pizza[i])
                        else :
                            return {'fulfillmentText': u'Veuillez entrer un nombre entier compris entre 1 et le nombre de pizzas que vous êtes capable de manger !'}

                    except : 
                        return {'fulfillmentText': u'Veuillez vous assurer que le(s) nom(s) des éléments de votre commande sont corrects. Essayez de nouveau !'}
                    
            print("Order", order)
            return {'fulfillmentText': u'Très bien, nous avons enregistré votre commande, qui est {}. Souhaitez-vous modifier la composition de pizza(s) ?'.format(format_dict_booking(order))}

        elif len(list_pizza)!=len(list_quantity_pizza): #not the same size of the lists
            return {'fulfillmentText': u'Pardon mais je n\'ai pas très bien compris votre commande. Pouvez-vous répéter ?'}

    # --- AddIngredients intent section

    elif req.get('queryResult').get('intent').get('displayName') == 'AddIngredients':
        ingredient_to_add = req.get('queryResult').get('outputContexts')[0].get('parameters').get('ingredients.original')
        pizza_to_modify = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')

        pizza_to_modify, code = search_by_name(DATA, pizza_to_modify)

        if code == 404 :
            return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

        elif code == 400 : 
            return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

        elif code == 200 : 
            pizza_to_modify = pizza_to_modify['name']
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

        pizza_to_modify, code = search_by_name(DATA, pizza_to_modify)

        if code == 404 :
            return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

        elif code == 400 : 
            return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

        elif code == 200 :  
            pizza_to_modify = pizza_to_modify['name']
            try :
                order[pizza_to_modify] -= 1
                if order[pizza_to_modify] == 0 :
                    del order[pizza_to_modify]

                order[pizza_to_modify + ' sans %s'%ingredient_to_remove] = 1

                print('Modification applied : {}'.format(order))

                return {'fulfillmentText': u"Vous venez de modifier une {}. Souhaitez-vous modifier la composition d'une autre pizza (si oui précisez le type de modification, le nom de la pizza et l'ingrédient en question) ou bien passer à la validation de votre commande.".format(pizza_to_modify)}

            except :
                return {'fulfillmentText': u"Votre commande ne contient pas la {}. Veuillez sélectionner une pizza déjà présente dans votre commande.".format(pizza_to_modify)}

    
    # --- BookingValidation

    elif req.get('queryResult').get('intent').get('displayName') == 'BookingValidation':

        return {'fulfillmentText': u"Votre commande actuelle est : {}. Voulez-vous la valider ? ".format(format_dict_booking(order))}

    
    # --- AddPizza

    elif req.get('queryResult').get('intent').get('displayName') == 'AddPizza':
        
        modified_order = deepcopy(order) #copy of the order, this allows to not modify the order if it fails during the process 
        list_pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        list_quantity_pizza = req.get('queryResult').get('parameters').get('number')
        unknown_quantity = req.get('queryResult').get('parameters').get('quantity')

        print("add pizza", len(list_pizza), list_pizza, list_quantity_pizza)

        if bool_pizza_in_list_pizza(list_pizza)==True : #if the client doesn't specify the name of the pizza "je veux ajouter une pizza"
            print("pas le nom")
            # "je veux ajouter 1 pizza" or "je veux ajouter la pizza" so we need to know the names of the pizzas
            if (len(list_quantity_pizza)>=1 and list_quantity_pizza[0]==1) or (len(list_quantity_pizza)==0 and unknown_quantity=='singulier') : 
                return {'fulfillmentText' : u'Quelle pizza souhaitez-vous ajouter ?'}

            ## "je veux ajouter 3 pizzas"  so we need to know the names of the pizzas and the number 
            else: 
                return {'fulfillmentText': u'Très bien, quelles pizzas voulez-vous ajouter ?'}

        elif len(list_pizza)>=1 and len(list_quantity_pizza)==0: #if the clients forgets to specify the quantity
            if len(list_pizza)==1 and unknown_quantity=='singulier':
                list_quantity_pizza=[1]
            else:
                return {'fulfillmentText': u'Pardon, je n\'ai pas bien compris, quelle pizza et combien en voulez-vous ?'}
            
        #"je veux ajouter 1 " forgets to add the pizza name
        elif len(list_pizza)==0 and (len(list_quantity_pizza)<=1 or unknown_quantity=='singulier' or (len(list_quantity_pizza)!=0 and list_quantity_pizza[0]==1)): #add a pizza (just ONE)
            return {'fulfillmentText': u'Quelle est le nom de la pizza que vous voulez ajouter ?'}
            
        #"je veux ajouter des" forgets to add the pizza name
        elif len(list_pizza)==0 and (len(list_quantity_pizza)>=2 or unknown_quantity=='pluriel' or (len(list_quantity_pizza)!=0 and list_quantity_pizza[0]>=2)): #add several pizzas
            return {'fulfillmentText': u'Quelles sont les pizza que vous voulez ajouter ?'}


        elif len(list_pizza)==len(list_quantity_pizza) and len(list_pizza)>=1: # need to have the same length so a quantity for each pizza

            for i, pizza in enumerate(list_pizza) :
                quantity = list_quantity_pizza[i]
                db_pizza_name, code = search_by_name(DATA, pizza)

                if code == 404 :
                    return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

                elif code == 400 : 
                    return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

                elif code == 200 : 
                    db_pizza_name = db_pizza_name['name']
                    try :
                        if db_pizza_name in modified_order.keys():
                            if list_quantity_pizza[i]>=1 : #to avoid negative number
                                modified_order[db_pizza_name] += int(list_quantity_pizza[i])
                            else : 
                                return {'fulfillmentText': u'Veuillez rentrer un nombre entier entre 1 et le nombre de pizzas que vous pouvez manger !'}
                        else :
                            if list_quantity_pizza[i]>=1 : #to avoid negative number
                                modified_order[db_pizza_name] = int(list_quantity_pizza[i])
                            else : 
                                return {'fulfillmentText': u'Veuillez rentrer un nombre entier entre 1 et le nombre de pizzas que vous pouvez manger !'}
                    except : 
                        return {'fulfillmentText': u'Veuillez vous assurer que le nom de la pizza est correct. Essayez de nouveau !'}
                
            #it has worked
            order = deepcopy(modified_order)
            return {'fulfillmentText': u'Très bien, nous avons mis à jour votre commande qui est donc : {}. Souhaitez-vous modifier la composition d\'une pizza ?'.format(format_dict_booking(order))}
            
        elif len(list_pizza)!=len(list_quantity_pizza):  
            return {'fulfillmentText': u'Nous avons du mal à comprendre la quantité de pizzas que vous voulez ajouter. Pouvez-vous être plus explicit ?'}

    
    # --- RemovePizza

    elif req.get('queryResult').get('intent').get('displayName') == 'RemovePizza':
        
        modified_order = deepcopy(order)
        list_pizza = req.get('queryResult').get('outputContexts')[0].get('parameters').get('pizza-type.original')
        list_quantity_pizza = req.get('queryResult').get('parameters').get('number')
        unknown_quantity = req.get('queryResult').get('parameters').get('quantity')

        if bool_pizza_in_list_pizza(list_pizza)==True : #if the client doesn't specify the name of the pizza "je veux retirer une pizza"
            
            ## "je veux retirer 1 pizza"  so we need to know the name of the pizza and the number 
            if (len(list_quantity_pizza)>=1 and list_quantity_pizza[0]==1) or (len(list_quantity_pizza)==0 and unknown_quantity=='singulier') : 
                return {'fulfillmentText' : u'Quelle pizza souhaitez-vous retirer ?'}

            ## "je veux ajouter 3 pizzas"  so we need to know the names of the pizzas and the number 
            else: 
                return {'fulfillmentText': u'Très bien, quelles pizzas voulez-vous retirer ?'}
        
        elif len(list_pizza)>=1 and len(list_quantity_pizza)==0: #if the clients forgets to specify the quantity
            if len(list_pizza)==1 and unknown_quantity=='singulier':
                list_quantity_pizza=[1]
            else:
                return {'fulfillmentText': u'Pardon, je n\'ai pas bien compris, quelle pizza et combien voulez-vous en retirer ?'}

        #"je veux retirer 1 " forgets to add the pizza name
        elif len(list_pizza)==0 and (len(list_quantity_pizza)<=1 or unknown_quantity=='singulier' or (len(list_quantity_pizza)!=0 and list_quantity_pizza[0]==1)): #add a pizza (just ONE)
            return {'fulfillmentText': u'Quelle est le nom de la pizza que vous voulez retirer ?'}
            
        #"je veux retirer des" forgets to add the pizza name
        elif len(list_pizza)==0 and (len(list_quantity_pizza)>=2 or unknown_quantity=='pluriel' or (len(list_quantity_pizza)!=0 and list_quantity_pizza[0]>=2)): #add several pizzas
            return {'fulfillmentText': u'Quelles sont les pizza que vous voulez enlever ?'}

        elif len(list_pizza)==len(list_quantity_pizza) and len(list_pizza)>=1:
            
            for i, pizza in enumerate(list_pizza) :
                quantity = list_quantity_pizza[i]
                db_pizza_name, code = search_by_name(DATA, pizza)

                if code == 404 :
                    return {'fulfillmentText' : u"Aucune pizza ne correspond à votre recherche. Asssurez vous que la pizza apparaisse sur notre carte, ou que vous avez bien orthographié son nom. Essayez de nouveau."}

                elif code == 400 : 
                    return {'fulfillmentText' : u"Plusieurs pizzas correspondent à votre recherche, veuillez spécifier votre demande"}

                elif code == 200 : 
                    db_pizza_name = db_pizza_name['name']
                    try :
                
                        if db_pizza_name in modified_order.keys():  #if the pizza is in the order

                            if  list_quantity_pizza[i]>=1: # if the quantity to remove is positive,  to avoid 0 or negative numbers

                                if list_quantity_pizza[i]>modified_order[db_pizza_name] or modified_order[db_pizza_name]-list_quantity_pizza[i]==0: #the client asks to delete more pizzas than he ordered so we just set it to 0
                                    del modified_order[db_pizza_name]
                                    
                                elif modified_order[db_pizza_name] - list_quantity_pizza[i] >=1:   # several pizzas of this type in the order so we decrease the order
                                    modified_order[db_pizza_name] -= list_quantity_pizza[i]
                                
                            else : #number is not good (negative or float)
                                return {'fulfillmentText': u'Veuillez entrer un nombre entier.'}

                        elif db_pizza_name not in modified_order.keys():
                            return {'fulfillmentText': u'La {} n\'est pas dans votre commande. Votre commande actuelle est : {}. Souhaitez-vous valider cette commande ? '.format(db_pizza_name, format_dict_booking(order))}

                    except : 
                        return {'fulfillmentText': u'Veuillez vous assurer que le nom de la pizza est correct. Essayez de nouveau !'}

            #it has worked
            order = deepcopy(modified_order)
            return {'fulfillmentText': u'Très bien, nous avons mis à jour votre commande qui est donc : {}. Souhaitez-vous la valider ?'.format(format_dict_booking(order))}

        elif len(list_pizza)!=len(list_quantity_pizza):  
            return {'fulfillmentText': u'Nous avons du mal à comprendre les pizzas que vous voulez supprimer. Pouvez-vous répéter plus explicitement ?'}


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    return make_response(jsonify(results()))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
