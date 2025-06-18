"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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

import copy
import json
import random
from typing import Optional

from game_entities import Location, Item, Enemy, Player
from proj1_event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The ID of the player's current location.
        - ongoing: A boolean indicating whether the game is still ongoing.
        - time: The current time (in minutes) past 12am.

    Representation Invariants:
        - self.current_location_id in self._locations
        - isinstance(self.ongoing, bool)
        - self.time >= 0
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object. This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.
    #   - _player: the Player object that is used for the game
    #   - _enemies: a list of Enemy objects, representing all enemies in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    _player: Player
    _enemies: list[Enemy]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed
    time: int

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items, self._enemies, self._player = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing
        self.time = 300

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item], list[Enemy], Player]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of
        (1) a dictionary of locations mapping each game location's ID to a Location object,
        (2) a list of all Item objects
        (3) a list of all Enemy objects
        (4) the Player object"""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        # Loads the locations
        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'], loc_data['enemies'],
                                    loc_data['possible_commands'])
            locations[loc_data['id']] = location_obj

        # Loads the items
        game_items = []
        for game_item in data['items']:
            item_obj = Item(game_item['name'], game_item['description'], game_item['target_position'],
                            game_item['target_points'], game_item['use_effect'])
            game_items.append(item_obj)

        # Loads the enemies
        enemies = []
        for game_enemy in data['enemies']:
            enemy_obj = Enemy(game_enemy['items'], game_enemy['health'], game_enemy['levels'], game_enemy['attack'],
                              game_enemy['name'], game_enemy['description'], game_enemy['lines'])
            enemies.append(enemy_obj)

        # Loads the player
        player_data = data['player']
        game_player = Player(player_data['items'], player_data['health'], player_data['levels'], player_data['attack'],
                             player_data['base_health'], player_data['health_additions'])

        return locations, game_items, enemies, game_player

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        if not loc_id:
            loc_id = self.current_location_id
        return self._locations[loc_id]

    def get_item(self, item_name: str) -> Item | None:
        """Return Item object associated with the given item name

        Preconditions:
            - item_name is the valid name of an item in self._items
        """
        for game_item in self._items:
            if game_item.name == item_name:
                return game_item
        return None

    def get_enemy(self, enemy_name: str) -> Enemy | None:
        """Return Enemy object associated with the given enemy name

        Preconditions:
            - enemy_name is the valid name of an item in self._enemies
        """
        for game_enemy in self._enemies:
            if game_enemy.name == enemy_name:
                return game_enemy
        return None

    def get_player(self) -> Player:
        """Return the player object."""
        return self._player

    def look(self) -> None:
        """Prints the long description of the current location and the names
        of any enemies or items present at the current location.
        """
        game_location = self.get_location()
        print(game_location.long_description)

        if game_location.items:
            print("\nYou can see:")
            for item_name in game_location.items:
                print(f"{item_name}")

        if game_location.enemies:
            print("\nThere is also:")
            for enemy_name in game_location.enemies:
                game_enemy = self.get_enemy(enemy_name)
                print(f"{game_enemy.description}")
                print(f"{game_enemy.name}: level {game_enemy.levels}")

        if game_location.items:
            game_location.available_commands["pickup"] = self.current_location_id

        if game_location.enemies:
            game_location.available_commands["fight"] = self.current_location_id
            game_location.available_commands["heal"] = self.current_location_id

    def inventory(self) -> list[str]:
        """Return the inventory of the player."""
        return self._player.inventory

    def select_item(self, game_items: list[str]) -> Optional[str]:
        """Returns the selected item from the inventory."""
        print("The available items are:")
        for game_item in game_items:
            print("- ", game_item)

        selected_game_item = input("\nPlease select an item or 'cancel': ").strip().lower()
        while selected_game_item not in game_items and selected_game_item != 'cancel':
            print("That was an invalid option; try again.")
            selected_game_item = input("\nPlease select an item or 'cancel': ").strip().lower()

        if selected_game_item == 'cancel':
            return None

        return selected_game_item

    def select_enemy(self) -> Optional[str]:
        """Returns the selected enemy from the current location."""
        print("The enemies that are present: ")
        for game_enemy in location.enemies:
            print("- ", game_enemy)

        selected_enemy = input("\nPlease select an enemy or 'cancel': ").strip().lower()
        while selected_enemy not in location.enemies and selected_enemy != 'cancel':
            print("That was an invalid option; try again.")
            selected_enemy = input("\nPlease select an enemy or 'cancel': ").strip().lower()

        if selected_enemy == 'cancel':
            return None

        return selected_enemy

    def check_can_drop(self) -> None:
        """Adds drop to the available commands if you have items to drop."""
        location.available_commands.pop("drop", None)

        if self.inventory():
            location.available_commands["drop"] = self.current_location_id

    def drop(self, item_name: str) -> None:
        """Determines and drops the given item in the current location.

        Preconditions:
        - item_name is the name of an item in the players inventory
        """
        location.items.append(item_name)
        self._player.inventory.remove(item_name)

        if "pickup" not in location.available_commands:
            location.available_commands["pickup"] = self.current_location_id

    def add_item(self, item_name: str) -> None:
        """Add an item to the player's inventory."""
        self._player.inventory.append(item_name)

    def pickup(self, item_name: str) -> None:
        """Determines and picks up the given item from the current location.

        Preconditions:
        - item_name is the name of an item in the current location
        """
        self.add_item(item_name)
        location.items.remove(item_name)

        if not location.items:
            location.available_commands.pop("pickup")

    def score(self) -> int:
        """Return the player score (level)."""
        score_acumulator = 0
        for game_item in self._player.inventory:
            score_acumulator += self.get_item(game_item).target_points

        for room in self._locations:
            if self.get_location(room).visited:
                score_acumulator += 1

        return self._player.levels + score_acumulator

    def fight(self, game_enemy: Enemy) -> None:
        """Engage in a fight between the player and an enemy.

    This function simulates a turn-based battle where:
    1. The player attacks first, dealing a randomized amount of damage based on their attack power and level.
    2. The enemy then takes a turn, choosing to either attack or heal.
    3. If the enemy attacks, the player takes randomized damage.
    4. If the enemy heals, their health increases by a random amount based on their level.
    5. The battle continues until either the player's or the enemy's health reaches 0.

    If the player loses (health drops to 0 or below):
        - The game ends, which means `self.ongoing = False`

    If the player wins (enemy health drops to 0 or below):
        1. The player gains experience levels, increasing their attack power and max health.
        2. The player's inventory is updated with items dropped by the enemy.
        3. The enemy is removed from the location.
        4. If no enemies remain at the location, combat-related commands are removed.

    Preconditions:
        - isinstance(game_enemy, Enemy)
        - game_enemy.health > 0
        - self._player.health > 0

        """
        random_attack_addition = random.randint(-self._player.levels, self._player.levels)
        game_enemy.health -= self._player.attack_damage + random_attack_addition
        print(f"{self._player.attack_damage + random_attack_addition} damage dealt.")

        enemy_move = random.choice(["attack", "heal"])

        if enemy_move == "attack":
            print(f"{game_enemy.name} attacked!")
            random_attack_addition = random.randint(-game_enemy.levels, game_enemy.levels)
            print(f"{game_enemy.attack_damage + random_attack_addition} damage taken")
            self._player.health -= (game_enemy.attack_damage + random_attack_addition)

        elif enemy_move == "heal":
            random_heal = random.randint(0, game_enemy.levels)
            print(f"{game_enemy.name} healed {random_heal}!")
            game_enemy.health += random_heal

        print(f"\n{game_enemy.name}: {random.choice(game_enemy.lines)}")
        print(f"{game_enemy.name} health: {game_enemy.health}")
        print(f"Your health: {self._player.health}")

        if self._player.health <= 0:
            self.ongoing = False

        elif game_enemy.health <= 0:
            print(f"You beat {game_enemy.name}")

            self._player.levels += game_enemy.levels
            self._player.attack_damage += game_enemy.levels
            self._player.health = self._player.base_health + self._player.levels * self._player.health_additons
            print(f"Your level is now {self._player.levels}")
            print(f"Your health is now {self._player.health} and your attack is {self._player.attack_damage}")

            for enemy_item in game_enemy.inventory:
                print(f"They gave you {enemy_item}.")
                self._player.inventory.append(enemy_item)

            location.enemies.remove(game_enemy.name)
            if not location.enemies:
                location.available_commands.pop("fight")
                location.available_commands.pop("heal")

    def heal(self, game_enemy: Enemy) -> None:
        """Heal the player and process the enemy's turn.

    This function allows the player to heal for a randomized amount based on their base health,
    health additions, and current level. After the player heals, the enemy takes a turn,
    choosing to either attack or heal.

    Preconditions:
        - isinstance(game_enemy, Enemy)
        - self._player.health > 0
        """
        random_heal = min(self._player.base_health + self._player.health_additons * self._player.levels,
                          random.randint(0, self._player.levels))
        print(f"Healed {random_heal}")
        self._player.health += random_heal

        enemy_move = random.choice(["attack", "heal"])

        if enemy_move == "attack":
            print(f"{game_enemy.name} attacked!")
            random_attack_addition = random.randint(-game_enemy.levels, game_enemy.levels)
            print(f"{game_enemy.attack_damage + random_attack_addition} damage taken")
            self._player.health -= (game_enemy.attack_damage + random_attack_addition)

        elif enemy_move == "heal":
            random_heal = random.randint(0, game_enemy.levels)
            print(f"{game_enemy.name} healed {random_heal}!")
            game_enemy.health += random_heal

        print(f"\n{game_enemy.name}: {random.choice(game_enemy.lines)}")
        print(f"{game_enemy.name} health: {game_enemy.health}")
        print(f"Your health: {self._player.health}")

        if self._player.health <= 0:
            self.ongoing = False

    def use_item(self, item_name: str) -> None:
        """Uses the item that was given in the item name."""
        item_effects = self.get_item(item_name).use_effect
        if item_effects[1] != -1:
            print(f"You used {item_name}, something might have changed...")
            location.available_commands[item_effects[0]] = item_effects[1]
            self._player.inventory.remove(item_name)

        else:
            print("You can't  use that item here!")

    def check_time_over(self) -> bool:
        """Returns True if the self.time is greater than 8am (480)"""
        if self.time > 480:
            return True
        return False

    def print_results(self) -> None:
        """Prints the final results of the game."""
        if self._player.health > 0 and not self.check_time_over():
            print("You handed in your project just in time!")

        elif self._player.health <= 0:
            print("You died and didn't get to hand in your project on time...")

        elif self.check_time_over():
            print("You didn't hand in your project on time and failed...")

        print(f"Your final score is {self.score()}")

    def show_time(self) -> None:
        """Prints the time in hh:mm format."""
        hours = self.time // 60
        minutes = self.time % 60
        print(f"The time is {str(hours).zfill(2)}:{str(minutes).zfill(2)}")

    def fight_undo(self, game_enemy: Enemy, game_player: Player) -> None:
        """Undoes the fight's results."""
        self._player = game_player
        location.available_commands.pop("fight")
        location.available_commands["fight"] = self.current_location_id
        for index in range(len(self._enemies)):
            if game_enemy.name == self._enemies[index].name:
                self._enemies[index] = game_enemy

        if game_enemy.name not in location.enemies:
            location.enemies.append(game_enemy.name)


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "use", "time", "score", "undo", "log", "quit"]
    choice = None
    random.seed(1)
    final_items = ["usb drive", "laptop charger", "lucky uoft mug"]
    print("You just woke up in your dorm room and its 5am! You have to hand in your assigment today! \
    \nFind all the nessecary items and bring them to the proffesors office before 8am, otherwise... YOU FAIL!")

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your marks will be based on how well-organized your code is.

        location = game.get_location()
        game.check_can_drop()
        game.time += 1
        if game.check_time_over():
            game.ongoing = False

        # Add new Event to game log
        if choice != "undo":
            game_log.add_event(Event(
                id_num=location.id_num,
                score=game.score()
            ),
                choice
            )

        elif game_log.is_empty():
            game_log.add_event(Event(
                id_num=location.id_num,
                score=game.score()
            ),
            )

        # Print the location either brief or long depending on wether it was visited
        if location.visited:
            print("==========")
            print(location.brief_description)
        else:
            print("==========")
            print(location.long_description)

        location.visited = True

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, use, time, score, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("==========")
        print("You decided to: ", choice)

        if choice in menu:
            if choice == "log":
                game_log.last.next_command = choice
                game_log.display_events()

            elif choice == "look":
                game.look()

            elif choice == "inventory":
                items = game.inventory()
                print("Your items are:")
                for item in items:
                    print(item)

            elif choice == "use":
                used_item = game.select_item(game.inventory())
                if used_item:
                    game.use_item(used_item)
                else:
                    print("You decided not to use anything")

                game_log.last.item_interaction = used_item

            elif choice == "time":
                game.show_time()

            elif choice == "undo" and not game_log.is_empty():
                latest_command = game_log.last.prev
                if game.time > 300:
                    game.time -= 2

                if latest_command:
                    game.current_location_id = latest_command.id_num

                    if latest_command.next_command == "drop" and latest_command.item_interaction:
                        game.pickup(latest_command.item_interaction)

                    elif latest_command.next_command == "pickup" and latest_command.item_interaction:
                        game.drop(latest_command.item_interaction)

                    elif latest_command.next_command == "use" and latest_command.item_interaction:
                        game.add_item(latest_command.item_interaction)
                        latest_item_obj = game.get_item(latest_command.item_interaction)
                        location.available_commands.pop(latest_item_obj.use_effect[0])

                    elif latest_command.next_command in ["fight", "heal"] and latest_command.entity_interaction:
                        game.fight_undo(latest_command.entity_interaction["enemy"],
                                        latest_command.entity_interaction["player"])

                    elif latest_command.next_command == "look" and \
                            ("look", latest_command.id_num) not in game_log.get_command_log()[:-2]:
                        curr_location = game.get_location(latest_command.id_num)
                        curr_location.available_commands.pop("pickup", None)
                        curr_location.available_commands.pop("fight", None)
                        curr_location.available_commands.pop("heal", None)

                game_log.remove_last_event()

            elif choice == "score":
                player_score = game.score()
                print("Your score is: ", player_score)

            elif choice == "quit":
                game.ongoing = False

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result

            if choice == "pickup":
                picked_item = game.select_item(location.items)
                if not picked_item:
                    print("You decided not to pickup anything")

                else:
                    print(game.get_item(picked_item).description)
                    game.pickup(picked_item)
                    game_log.last.item_interaction = picked_item

            elif choice == "drop":
                selected_item = game.select_item(game.inventory())
                if not selected_item:
                    print("You decided not to drop anything")

                else:
                    print("You decided to drop: ", selected_item)
                    game.drop(selected_item)
                    game_log.last.item_interaction = selected_item

            elif choice == "fight":
                enemy = game.get_enemy(game.select_enemy())
                player = game.get_player()
                game_log.last.entity_interaction = {"enemy": (copy.deepcopy(enemy)), "player": copy.deepcopy(player)}
                game.fight(enemy)

            elif choice == "heal":
                enemy = game.get_enemy(random.choice(location.enemies))
                player = game.get_player()
                game_log.last.entity_interaction = {"enemy": (copy.deepcopy(enemy)), "player": copy.deepcopy(player)}
                game.heal(enemy)

            elif choice == "hand in assignment":
                player_inv = game.inventory()

                if all([final_item in player_inv for final_item in final_items]):
                    game.ongoing = False

                else:
                    print("Stop wasting time! You still need to get:")
                    for item in final_items:
                        if item not in player_inv:
                            print(item)

    game.print_results()
