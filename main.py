import os
import json
import random

with open('gods.json', 'r') as gods_file:
    gods = json.load(gods_file)

    gods_seq = list(gods.items())
    god_count = len(gods)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def filter_shards(pair):
    key, value = pair

    return 'shard' not in key.lower()


def filter_core_relics(pair):
    key, value = pair
    names = ('beads', 'aegis', 'blink')

    return any(name in key.lower() for name in names)


def relics_menu():
    menu_options = [
        'practice with all relics',
        'practice with all relics minus shards',
        'practice with only beads, aegis and blink',
        'exit'
    ]

    menu_length = len(menu_options)

    with open('relics.json', 'r') as relics_file:
        relics = json.load(relics_file)

    for option_index, option_desc in enumerate(menu_options, 1):
        option_desc = option_desc.capitalize()
        print(f'{option_index}. {option_desc}.')

    selected_option_index = input(f'\nPlease enter your preferred option [1-{menu_length}]: ')
    selected_option_index = int(selected_option_index) - 1
    selected_option_desc = menu_options[selected_option_index]

    clear()

    # Exit
    if selected_option_index == 3:
        print('Goodbye.')
        exit()

    print(f'You have chosen to {selected_option_desc}.')

    if selected_option_index == 1:
        # Filter so that there aren't any shards.
        relics = dict(filter(filter_shards, relics.items()))

    if selected_option_index == 2:
        # Filter so that there's only beads, aegis and blink.
        relics = dict(filter(filter_core_relics, relics.items()))

    return relics


def question_loop(relics):
    interrupted = False

    while not interrupted:
        god = random.choice(gods_seq)
        relic = random.choice(relics)

        god_name, god_role = god
        relic_name, (relic_cooldown_minutes, relic_cooldown_seconds) = relic

        game_minutes, game_seconds = random.randint(3, 40), random.randint(1, 59)

        game_time_in_seconds = game_minutes * 60 + game_seconds
        relic_time_in_seconds = relic_cooldown_minutes * 60 + relic_cooldown_seconds

        relic_next_availability = game_time_in_seconds + relic_time_in_seconds
        relic_next_availability_minutes, relic_next_availability_seconds = divmod(relic_next_availability, 60)

        print(f'\n{god_name} used {relic_name} at {game_minutes}:{game_seconds:02d}.')
        print(f'The relic has a cooldown of {relic_time_in_seconds} seconds.')

        response = input(f'When is the next time they will be available? ')
        minutes, seconds = response.split(':')
        minutes, seconds = int(minutes), int(seconds)

        if relic_next_availability_minutes == minutes and relic_next_availability_seconds == seconds:
            print(f"That is correct! {god_name}'s {relic_name} will be available at {minutes}:{seconds:02d}.")
        else:
            print(
                f'Sorry! The correct answer is {relic_next_availability_minutes}:{relic_next_availability_seconds:02d}.'
            )

        continuation = input('\nWould you like to continue? y/N ')

        if continuation.lower() == 'n':
            interrupted = True
            clear()


def main():
    print("Welcome to Pawrsley's relic timer practice.\n")

    try:
        while True:
            relics = relics_menu()
            relics_seq = list(relics.items())
            relic_count = len(relics)

            print(f'The program has successfully registered {god_count} gods and {relic_count} relics.\n')

            question_loop(relics_seq)

    except KeyboardInterrupt:
        print('Goodbye.')
        exit()


# TODO: Proper error handling for user input.
if __name__ == "__main__":
    main()
