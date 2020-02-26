import pandas as pd 

data = pd.read_csv('../data/extended_pizzas.csv', sep = ';')

print(';'.join(
            list(
                map(
                    lambda x : x.lower(),
                    data.name.tolist()
                )
        )
    )
)