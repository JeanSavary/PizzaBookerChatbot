lines_to_write = []
with open('../data/pizzas.txt', 'r') as file :
    next(file)
    for line in file:    
        list_to_write = line.split(',')
        str_to_write = '{name};"{description}";"{ingredients}";{others}'.format(
            name = list_to_write[0],
            description = list_to_write[1],
            ingredients = ', '.join(list_to_write[2:-4]),
            others = ', '.join(list_to_write[-4:]).replace(',', ';')
        )

        lines_to_write.append(str_to_write)

    file.close()

with open('../data/corrected_pizzas.txt', 'w') as file :

    for line in lines_to_write :
        file.write(line)

    file.close()

