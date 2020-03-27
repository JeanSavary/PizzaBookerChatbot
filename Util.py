import pandas as pd
import numpy as np
from copy import deepcopy  #the use of deepcopy can be debated !!

# A retravailler !! 

class Util ():

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

