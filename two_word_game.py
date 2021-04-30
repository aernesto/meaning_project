# -*- coding: utf-8 -*-
import numpy as np
MAX_FOOD_PLAYER = 4
MAX_WATER_PLAYER = 4
MAX_WATER_PLANT = 4
P_WATER = 0.5
INTRO = ':) :) :) Welcome to the 2-word language game!!! :) :) :)'
EXIT = 'exitting game'
RULES = f"""
you must take care of yourself and of your plant\n
\nto survive, your food and water reserves must not hit 0\n
Your maximum food and water reserves are {MAX_FOOD_PLAYER}
and {MAX_WATER_PLAYER}, and for your plant {MAX_WATER_PLANT}.
\nyou can only drink "pure water", and you can only hold \n
two objects at a time.\n
Your plant can drink any type of water, and it dies if its\n
water reserves go to 0. If your plant dies, you die.\n
If you drink "impure water", you die.\n
At every turn, you must take one of the following action:\n
1. eat\n
2. drink \n
3. water plant\n
4. order "pure water" to get pure water and 1 food unit\n
5. order "only water" to get 1 unit of each kind of water. \n
6. order "water" to get 1 unit of water and 1 unit of food.\n
   The water is pure with probability {P_WATER}.

Can you survive forever?

GOOD GAME!
"""
GAMEOVER = 'GAME OOOOOVER OOOVER OOOOOOOVERRRRRR!!!!!!!!!\n XXXX YOU LOSER XXXXX\n'
RNG = np.random.default_rng()


def flip(p):
    return RNG.random() < p


def continue_quit():
    i = 0
    while i not in {'c', 'q'}:
        print()
        i = input('type c to continue, q to quit ')
    return i


def augment_reserve(state_, reserve, objec, maxval):
    """
    object disappears after use, even if reserve has hit its max before use
    if object empty before use, nothing happens, but turn is wasted
    """
    stat = state_.copy()
    if stat[objec]:
        if stat[reserve] < maxval:
            stat[reserve] += 1
            if stat[reserve] > maxval:
                stat[reserve] = maxval
                print(f'your {reserve} is at its max :)')
        else:
            print(
                f'max reserves reached, your action had no effect, but you lost a {objec}'
            )
    else:
        print(f"you just wasted a turn as you don't have any {objec}")
    stat[objec] = False
    return stat


def select_action():
    actions = {
        1: 'eat',
        2: 'drink',
        3: 'water plant',
        4: 'order "pure water"',
        5: 'order "only water"',
        6: 'order "water"'
    }
    action = -1
    while action not in actions.keys():
        try:
            action = int(input(f'select action: {actions}: '))
        except ValueError:
            pass
    return action


def update_state(act, d):
    dd = d.copy()

    # CONSUMPTION
    if act == 1:  # eat
        dd = augment_reserve(dd, 'food_reserve', 'food_in_hand',
                             MAX_FOOD_PLAYER)
    elif act == 2:  # drink
        if dd['pure_water_in_hand']:
            dd = augment_reserve(dd, 'water_reserve', 'pure_water_in_hand',
                                 MAX_WATER_PLAYER)
        elif dd['impure_water_in_hand']:
            dd['impure_water_in_hand'] = False
            dd['poisoned'] = True  # you've been poisoned
            print('you just poisoned yourself!!')
    elif act == 3:  # water plant
        k = 'impure_water_in_hand'
        if not dd[k]:  # if no impure water in hand, fall back on pure water
            k = 'pure_water_in_hand'
        dd = augment_reserve(dd, 'plant_reserve', k, MAX_WATER_PLANT)

    # ORDERS
    elif act == 4:  # order pure water
        if not dd['food_in_hand']:
            dd['food_in_hand'] = True
            print('  you got 1 unit of food')
        if dd['pure_water_in_hand'] or dd['impure_water_in_hand']:
            print('you already have water')
            return dd
        if not dd['pure_water_in_hand']:
            dd['pure_water_in_hand'] = True
            print('  you got 1 unit of pure water')
    elif act == 5:  # order only water
        if dd['food_in_hand']:
            if flip(P_WATER):
                if dd['pure_water_in_hand']:
                    print('hands full, nothing happens')
                    return dd
                dd['pure_water_in_hand'] = True
                print('  you got 1 unit of pure water')
            else:
                if dd['impure_water_in_hand']:
                    print('hands full, nothing happens')
                    return dd
                dd['impure_water_in_hand'] = True
                print('  you got 1 unit of impure water')
        else:
            dd['pure_water_in_hand'] = True
            dd['impure_water_in_hand'] = True
            print('  you have 1 unit of pure water and 1 unit of impure water')

    elif act == 6:  # order water
        if not dd['food_in_hand']:
            dd['food_in_hand'] = True
            print('  you got 1 unit of food')
        if dd['pure_water_in_hand'] or dd['impure_water_in_hand']:
            print('you already have water')
            return dd
        if flip(P_WATER):
            dd['pure_water_in_hand'] = True
            print('  you got 1 unit of pure water')
        else:
            dd['impure_water_in_hand'] = True
            print('  you got 1 unit of impure water')
    return dd


def game():
    def print_(ds):
        health_keys = [
            'food_reserve', 'water_reserve', 'plant_reserve', 'poisoned'
        ]
        hd = {k: ds[k] for k in health_keys}
        inventory = [
            'food_in_hand', 'pure_water_in_hand', 'impure_water_in_hand'
        ]
        idd = {k: ds[k] for k in inventory}
        print(f"Health: {hd}")
        print(f"Inventory: {idd}")
        print()

    alive = True
    state = {
        'food_reserve': MAX_FOOD_PLAYER,
        'water_reserve': MAX_WATER_PLAYER,
        'plant_reserve': MAX_WATER_PLANT,
        'food_in_hand': False,
        'impure_water_in_hand': False,
        'pure_water_in_hand': False,
        'poisoned': False,
    }
    to_survive = ['food_reserve', 'water_reserve', 'plant_reserve']
    turn = 0
    while alive:
        turn += 1
        print(f"\n=========== turn {turn} ===============\n")
        for v in to_survive:
            state[v] -= 1 / 2
        print_(state)
        a = select_action()
        state = update_state(a, state)
        alive = all([state[v] for v in to_survive]) and not state['poisoned']

    print(GAMEOVER)


def main_loop():
    print(INTRO)
    v = continue_quit()
    if v == 'q':
        print(EXIT)
        return None
    print(RULES)
    v = continue_quit()
    if v == 'q':
        print(EXIT)
        return None
    game()


if __name__ == "__main__":
    main_loop()
