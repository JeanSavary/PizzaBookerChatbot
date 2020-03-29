import pandas as pd
import numpy as np
from copy import deepcopy  #the use of deepcopy can be debated !!

def creation_df_bool_presence(col,list_elements, df, conjonction='addition'):
    """ This function creates a dataFrame with booleans, True if the element (string) is inthe column col (string) of the dataframe d, else false
    It is used for to check is ingredients are within a pizza or not for example """
    nb_element = len(list_elements)
    df_temp = pd.DataFrame(index=df.index)
    for element in list_elements:
        if col=='ingredients':  #because in the csv the first letter is upper, it doesn't apply for the case it s pizza
            element = element.lower()
            element = element[0].upper()+element[1:] 
            print("element", element)
            if "Viande" in element:
                df_temp[element] = df["is_meat"]
            elif element =="Alcool" or element =="Alcohol":
                df_temp[element] = df["is_acohol"]
            elif "Sucre" in element or "Sucré" in element:  #formulation "in" instead of == to cope with conjugaison 'sucrée'
                df_temp[element]=df["is_sugar"]
            elif "Salé" in element or "Sale" in element :  #it s a special ingredient, opposite of "sucré" but not in the list of ingredients
                df_temp[element] = ~df["is_sugar"]
            elif "Végétarienne" in element or "Vegetarienne" in element :
                df_temp[element] = ~df["is_meat"]      #the opposite 
            elif "Calzone" in element :
                df_temp[element] = df["is_calzone"]
            elif "Crème fraîche" in element or "Base crème" in element or "Creme fraiche" in element or "Base creme" in element:
                df_temp[element]= df['is_cream_base']
            elif "Base tomate" in element or "Base sauce tomate" in element:
                df_temp[element] = ~df["is_cream_base"]
            elif "Pimenté" in element or "Piment" in element :
                df_temp[element]= df["is_spicy"]
            else :
                print("case else", element)
                df_temp[element]=df[col].apply(lambda x: True if (element in x or element[:-1] in x) else False) #element[:-1] for the case it s a plurial in the question

        elif col=='name' : #case it s GetPizzaComposition
            if ' ' in element:
                element = element.split(' ')[-1] #case it s 'pizza chipo', we keep just 'chipo'
            element = element[0].upper()+element[1:]
            df_temp[element]=df[col].apply(lambda x: True if (element in x or element[:-1] in x) else False) #element[:-1] for the case it s a plurial in the question
    print('df_temmmmp', df_temp.shape, df_temp)
    df_temp['sum'] = df_temp.sum(axis=1)
    if conjonction =='addition':
        df_return = pd.DataFrame(df_temp['sum'].apply(lambda x:True if x==nb_element else False)) #all the ingredients are needed to select the pizza
    elif conjonction =='ou':
        df_return = pd.DataFrame(df_temp['sum'].apply(lambda x:True if x>=1 else False))  #ou inclusif, at least one of the ingredients
    print("df_return", df_return)
    return(df_return)

def select_bool_column(df_bool, df_data, col_data, bool):
    """ This function takes a df_bool (dataframe, one column with boolean values) and return the list of the values of a selected 
     column of an other dataframe where the row is True in df_bool
     It is used """
    list_return = []
    list_return = [ df_data.loc[i,col_data] for i, element in enumerate (df_bool.iloc[:,0]) if df_bool.iloc[i,0]==bool] 
    return (list_return)

def pizza_without_ingredient(self, ingredient, DATA):
    list_pizza = []
    df_copy = deepcopy(DATA)
    df_copy['pizza_ingre'] = df_copy['ingredients'].apply(lambda x: True if ingredient in x else False)
    list_pizza = [ df_copy.loc[i,'name'] for i, element in enumerate (df_copy['pizza_ingre']) if df_copy.loc[i,'pizza_ingre']==False]
    df_copy = df_copy.drop(['pizza_ingre'], axis=1)
    return(list_pizza)

def format_list_for_message_client(list_data):
    list_data_string = str(list_data).replace('[','')
    list_data_string = list_data_string.replace(']','')
    list_data_string = list_data_string.replace('\'','')
    list_data_string = list_data_string.replace('\"','')
    return (str(list_data_string))