"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate an entire
playthrough of the game. Please consult the project handout for instructions and details.

You can copy/paste your code from the ex1_simulation file into this one, and modify it as needed
to work with your game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from __future__ import annotations
import random

from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location, Enemy, Player


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int,
                 commands: list[tuple[str, int, str | None, dict[str, any] | None]]) -> None:
        """Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        initial_location = self._game.get_location()
        self._events.add_event(Event(
            id_num=initial_location.id_num,
            score=commands[0][1]
        ))
        # Hint: self._game.get_location() gives you back the current location

        self.generate_events(commands, initial_location)
        # Hint: Call self.generate_events with the appropriate arguments

    def generate_events(self, commands: list[tuple[str, int, str, dict[str, any]]], current_location: Location) -> None:
        """Generate all events in this simulation.

        Preconditions:
        - len(commands) > 0
        - all commands with the key 'command' in the list are valid commands at each associated location in the game
        """
        for event in commands:
            if event[0] in current_location.available_commands:
                current_location = self._game.get_location(current_location.available_commands[event[0]])

            elif event[0] in current_location.possible_commands:
                current_location = self._game.get_location(current_location.possible_commands[event[0]])

            self._events.add_event(Event(
                current_location.id_num,
                event[1]
            ), event[0], event[2], event[3])

        # Hint: current_location.available_commands[command] will return the next location ID
        # which executing <command> while in <current_location_id> leads to

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        >>> simulation = AdventureGameSimulation('game_data.json', 1, [("open door", 1, None, None)])
        >>> simulation.get_id_log()
        [1, 2]
        """

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and log location descriptions."""

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        current_event = self._events.first  # Start from the first event in the list
        visited_rooms = set()
        random.seed(1)
        event_num = 0
        passed_events = EventList()
        player_inv = []

        while current_event:
            # passed_events.add_event(current_event)
            curr_location = self._game.get_location(current_event.id_num)
            curr_item = current_event.item_interaction
            if current_event.entity_interaction:
                curr_enemy = current_event.entity_interaction["enemy"]
                curr_player = current_event.entity_interaction["player"]
            else:
                curr_enemy = None
                curr_player = None

            if current_event.id_num not in visited_rooms:
                print("==========")
                print(curr_location.long_description)
            else:
                print("==========")
                print(curr_location.brief_description)

            if current_event is not self._events.last:
                print("==========")
                print("You choose:", current_event.next_command)

            if current_event.next_command == "log":
                passed_events.display_events()

            elif current_event.next_command == "look":
                print(curr_location.long_description)

                if curr_location.items:
                    print("\nYou can see:")
                    for item_name in curr_location.items:
                        print(f"{item_name}")

                if curr_location.enemies:
                    print("\nThere is also:")
                    for enemy_name in curr_location.enemies:
                        game_enemy = self._game.get_enemy(enemy_name)
                        print(f"{game_enemy.description}")
                        print(f"{game_enemy.name}: level {game_enemy.levels}")

            elif current_event.next_command == "inventory":
                print("Your items are:")
                for item in player_inv:
                    print(item)

            elif current_event.next_command == "use":
                if curr_item and self._game.get_item(curr_item).target_position == current_event.id_num:
                    print(f"You used {curr_item}, something might have changed...")
                elif curr_item:
                    print("You can't  use that item here!")
                else:
                    print("You decided not to use anything")

                player_inv.remove(curr_item)

            elif current_event.next_command == "time":
                hours = (event_num + 300) // 60
                minutes = (event_num + 300) % 60
                print(f"The time is {str(hours).zfill(2)}:{str(minutes).zfill(2)}")

            elif current_event.next_command == "score":
                print("Your score is: ", current_event.score)

            elif current_event.next_command == "pickup":
                if curr_item:
                    print(self._game.get_item(curr_item).description)
                else:
                    print("You decided not to pickup anything")

            elif current_event.next_command == "drop":
                if curr_item:
                    print("You decided to drop: ", curr_item)
                else:
                    print("You decided not to drop anything")

            elif current_event.next_command == "fight":
                next_enemy_event = current_event.next
                next_player_event = None

                while next_enemy_event != self._events.last:
                    if next_enemy_event.entity_interaction:
                        if next_enemy_event.entity_interaction["enemy"].name == curr_enemy.name:
                            break

                    if next_enemy_event.entity_interaction and not next_player_event:
                        next_player_event = next_enemy_event

                    next_enemy_event = next_enemy_event.next

                if next_enemy_event.entity_interaction:
                    enemy_health_dif = curr_enemy.health - next_enemy_event.entity_interaction["enemy"].health
                    curr_enemy_health = curr_enemy.health - enemy_health_dif
                else:
                    enemy_health_dif = curr_player.attack_damage
                    curr_enemy_health = curr_enemy.health - enemy_health_dif

                if next_player_event:
                    player_health_dif = curr_player.health - next_player_event.entity_interaction["player"].health
                else:
                    if enemy_health_dif < curr_player.attack_damage:
                        player_health_dif = 0

                    else:
                        player_health_dif = curr_enemy.attack_damage

                if player_health_dif == 0:
                    print(f"{curr_player.attack_damage} damage dealt.")

                else:
                    print(f"{enemy_health_dif} damage dealt.")

                if player_health_dif == 0:
                    print(f"{curr_enemy.name} healed {-(curr_player.attack_damage - enemy_health_dif)}!")
                else:
                    print(f"{curr_enemy.name} attacked!")
                    print(f"{player_health_dif} damage taken")

                print(f"\n{curr_enemy.name}: {random.choice(curr_enemy.lines)}")
                print(f"{curr_enemy.name} health: {max(curr_enemy_health, 0)}")
                print(f"Your health: {max(curr_player.health - player_health_dif, 0)}")

                if curr_enemy_health <= 0:
                    print(f"You beat {curr_enemy.name}")
                    print(f"Your level is now {curr_player.levels + curr_enemy.levels}")
                    print(f"Your health is now "
                          f"{curr_player.base_health + (curr_player.levels + curr_enemy.levels
                                                        * curr_player.health_additons)} "
                          f"and your attack is {curr_player.attack_damage + curr_enemy.levels}")

                    for enemy_item in curr_enemy.inventory:
                        print(f"They gave you {enemy_item}.")
                        player_inv.append(enemy_item)

            elif current_event.next_command == "heal":
                next_enemy_event = current_event.next
                next_player_event = None

                while next_enemy_event != self._events.last:
                    if next_enemy_event.entity_interaction["enemy"].name == curr_enemy.name:
                        break

                    if next_enemy_event.entity_interaction and not next_player_event:
                        next_player_event = next_enemy_event

                    next_enemy_event = next_enemy_event.next

                if next_player_event:
                    player_health_dif = curr_player.health - next_player_event.entity_interaction["player"].health

                else:
                    player_health_dif = curr_player.health + curr_player.levels

                if next_enemy_event.entity_interaction:
                    enemy_health_dif = curr_enemy.health - next_enemy_event.entity_interaction["enemy"].health
                    curr_enemy_health = curr_enemy.health - enemy_health_dif
                else:
                    enemy_health_dif = -curr_enemy.levels
                    curr_enemy_health = curr_enemy.health - enemy_health_dif

                if enemy_health_dif == 0:
                    print(f"Healed {curr_player.levels}")
                    print(f"{curr_enemy.name} attacked!")
                    print(f"{curr_player.levels - player_health_dif} damage taken")

                else:
                    print(f"Healed {player_health_dif}")
                    print(f"{curr_enemy.name} healed {enemy_health_dif}!")

                print(f"\n{curr_enemy.name}: {random.choice(curr_enemy.lines)}")
                print(f"{curr_enemy.name} health: {max(curr_enemy_health, 0)}")
                print(f"Your health: {max(curr_player.health - player_health_dif, 0)}")

            elif current_event.next_command == "hand in assignment":
                if not current_event == self._events.last.prev:
                    print("Stop wasting time!")

            # Move to the next event in the linked list
            visited_rooms.add(current_event.id_num)
            current_event = current_event.next
            event_num += 1

        if self._events.last.prev.next_command == "hand in assignment":
            print("You handed in your project just in time!")
        else:
            print("You didn't hand in your project on time and failed...")

        print(f"Your final score is {self._events.last.score}")


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    win_walkthrough = [
        ('open door', 1, None, None),
        ('take stairs', 2, None, None),
        ('descend to library', 3, None, None),
        ('look', 4, None, None),
        ('pickup', 5, 'laptop charger', None),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=20, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=30, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=18, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=28, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=16, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=28, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=13, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=28, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=12, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=28, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=11, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=28, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=9, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=26, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=7, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=22, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=4, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=19, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('fight', 10, None, {
            'enemy': Enemy(inventory=['archive key'], health=2, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=['laptop charger'], health=16, levels=1, attack_damage=3, base_health=25,
                             health_additons=5)}),
        ('use', 16, 'archive key', None),
        ('take stairs', 12, None, None),
        ('go outside', 12, None, None),
        ('walk to coffee shop', 12, None, None),
        ('look', 13, None, None),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=30, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair,'
                                       ' protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=40, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=23, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair,'
                                       ' protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=31, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=19, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair,'
                                       ' protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=25, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=12, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair,'
                                       ' protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=21, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=5, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair,'
                                       ' protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=21, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=2, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair, '
                                       'protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=21, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('fight', 14, None, {
            'enemy': Enemy(inventory=[], health=1, levels=3, attack_damage=6, name='sleep-deprived student',
                           description='A wild-eyed student fueled by caffeine and despair, '
                                       'protecting their research at all costs.',
                           lines=["I've got 2 hours to submit this!", "Go away, I’m working!",
                                  "I haven’t slept in 3 days!"]),
            'player': Player(inventory=['laptop charger'], health=21, levels=3, attack_damage=5, base_health=25,
                             health_additons=5)}),
        ('go outside', 17, None, None),
        ('run to cs building', 17, None, None),
        ('enter classroom', 17, None, None),
        ('look', 18, None, None),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=50, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=55, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=40, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=55, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=38, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=55, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=29, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=45, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=21, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=45, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=8, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=38, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('fight', 19, None, {
            'enemy': Enemy(inventory=['acces fob'], health=3, levels=3, attack_damage=7, name='angry ta',
                           description='A teaching assistant who has graded one too many bad assignments.',
                           lines=["This is incorrect!", "Did you even read the rubric?", "Resubmit for half credit."]),
            'player': Player(inventory=['laptop charger'], health=38, levels=6, attack_damage=8, base_health=25,
                             health_additons=5)}),
        ('exit to cs building', 25, None, None),
        ('use', 25, 'acces fob', None),
        ('go outside', 22, None, None),
        ('take stairs', 22, None, None),
        ('descend to library', 22, None, None),
        ('enter archive room', 22, None, None),
        ('look', 22, None, None),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=80, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=70, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=61, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=58, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=51, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=58, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=32, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=46, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=14, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=32, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('fight', 23, None, {'enemy': Enemy(inventory=['lucky uoft mug'], health=6, levels=4, attack_damage=10,
                                            name='haunting grad student',
                                            description='A ghostly figure that haunts the library’s archives, '
                                                        'whispering forgotten knowledge.',
                                            lines=["You shall not pass!", "Your knowledge is weak!",
                                                   "Feel the wrath of the archives!"]),
                             'player': Player(inventory=['laptop charger'], health=32, levels=9, attack_damage=11,
                                              base_health=25, health_additons=5)}),
        ('ascend to library', 32, None, None),
        ('take stairs', 32, None, None),
        ('go outside', 32, None, None),
        ('run to cs building', 32, None, None),
        ('enter proffessors office', 32, None, None),
        ('exit to cs building', 32, None, None),
        ('enter server room', 33, None, None),
        ('look', 33, None, None),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=120, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=90, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=106, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=90, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=107, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=90, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=105, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=70, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=86, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=59, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=59, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=59, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=55, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=49, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=54, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=49, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=49, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=34, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=45, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=22, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=27, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=2, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('fight', 34, None, {
            'enemy': Enemy(inventory=['usb drive'], health=8, levels=5, attack_damage=15, name='security bot',
                           description='A campus security robot programmed to protect the server room.',
                           lines=["Unauthorized access detected.", "Leave now or be removed.", "Initiating lockdown."]),
            'player': Player(inventory=['laptop charger', 'lucky uoft mug'], health=2, levels=13, attack_damage=15,
                             base_health=25, health_additons=5)},),
        ('exit to cs building', 49, None, None),
        ('enter proffessors office', 49, None, None),
        ('hand in assignment', 49, None, None),

    ]  # Create a list of all the commands needed to walk through your game to win it
    expected_log = [1, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 7, 10, 10, 10, 10, 10, 10, 10, 10, 10, 7, 11,
                    14, 14, 14, 14, 14, 14, 14, 14, 14, 11, 11, 7, 4, 6, 9, 9, 9, 9, 9, 9, 9, 9, 6, 4, 7, 11, 13, 11,
                    12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 13, 13]
    # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your walkthrough

    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    sim.run()
    sim_id = sim.get_id_log()
    assert expected_log == sim_id

    inventory_demo = [('open door', 1, None, None),
                      ('look', 2, None, None),
                      ('pickup', 3, 'sticky note', None),
                      ('inventory', 4, None, None)]
    expected_log = [1, 2, 2, 2, 2]

    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    sim.run()
    sim_id = sim.get_id_log()
    assert expected_log == sim_id

    scores_demo = [('open door', 1, None, None),
                   ('look', 2, None, None),
                   ('pickup', 3, 'sticky note', None),
                   ('score', 4, None, None)]
    expected_log = [1, 2, 2, 2, 2]

    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    sim.run()
    sim_id = sim.get_id_log()
    assert expected_log == sim_id

    fight_demo = [
        ('open door', 1, None, None),
        ('take elevator', 2, None, None),
        ('descend to library', 3, None, None),
        ('look', 4, None, None),
        ('fight', 5, None, {
            'enemy': Enemy(inventory=['archive key'], health=20, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=[], health=30, levels=1, attack_damage=3, base_health=25, health_additons=5)})
    ]

    expected_log = [1, 2, 3, 6, 6, 6]

    sim = AdventureGameSimulation('game_data.json', 1, fight_demo)
    sim.run()
    sim_id = sim.get_id_log()
    assert expected_log == sim_id

    heal_demo = [
        ('open door', 1, None, None),
        ('take elevator', 2, None, None),
        ('descend to library', 3, None, None),
        ('look', 4, None, None),
        ('fight', 5, None, {
            'enemy': Enemy(inventory=['archive key'], health=20, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=[], health=30, levels=1, attack_damage=3, base_health=25, health_additons=5)}),
        ('heal', 5, None, {
            'enemy': Enemy(inventory=['archive key'], health=17, levels=2, attack_damage=2, name='grumpy librarian',
                           description='A librarian who has had enough of noisy students and late book returns.',
                           lines=["Return your books on time!", "This isn’t a social club!",
                                  "Respect the library rules!"]),
            'player': Player(inventory=[], health=28, levels=1, attack_damage=3, base_health=25, health_additons=5)})
    ]

    expected_log = [1, 2, 3, 6, 6, 6, 6]

    sim = AdventureGameSimulation('game_data.json', 1, heal_demo)
    sim.run()
    sim_id = sim.get_id_log()
    assert expected_log == sim_id

# Add more enhancement_demos if you have more enhancements
# enhancement1_demo = [...]
# expected_log = []
# assert expected_log == AdventureGameSimulation(...)

# Note: You can add more code below for your own testing purposes
