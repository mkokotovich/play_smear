import os

def to_representation(longvalue, longsuit):
    value = {
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        '9': '9',
        '10': '0',
        'jack': 'J',
        'queen': 'Q',
        'king': 'K',
        'ace': 'A',
    }.get(longvalue.lower(), None)

    suit = {
        'spades': 'S',
        'hearts': 'H',
        'clubs': 'C',
        'diamonds': 'D',
    }.get(longsuit.lower(), None)

    return value + suit


for filename in os.listdir('.'):
    if filename.startswith('English'):
        name = filename.split('.')[0]
        extension = filename.split('.')[1]
        parts = name.split('_')
        value = parts[2]
        suit = parts[4]
        rep = to_representation(value, suit)

        new_name = f"{rep}.{extension}"
        print(f"{filename} to {new_name}")

        os.rename(filename, new_name)
