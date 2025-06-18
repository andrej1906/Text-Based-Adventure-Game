"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from dataclasses import dataclass


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id_num: Integer id of this event's location
        - brief_description: One sentence describing location
        - long_description: Small paragraph of 5 sentences describing the location
        - available_commands: List of available commands in this location
        - possible_commands: List of possible commands in this location
        - items: List of items at this location
        - enemies: List of enemies at this location
        - visited: Variable that keeps count of how many times you have visited this location


    Representation Invariants:
        - self.id_num>0
        - len(self.long_description)>len(self.brief_description)
        - len(self.available_commands)>0
        - len(self.visited)>=0
    """
    id_num: int
    brief_description: str
    long_description: str
    available_commands: dict[str, int]
    items: list[str]
    enemies: list[str]
    visited: bool
    possible_commands: dict[str, int]

    # This is just a suggested starter class for Location.
    # You may change/add parameters and the data available for each Location object as you see fit.
    #
    # The only thing you must NOT change is the name of this class: Location.
    # All locations in your game MUST be represented as an instance of this class.

    def __init__(self, location_id, brief_description, long_description, available_commands, items, enemies,
                 possible_commands, visited=False) -> None:
        """Initialize a new location."""
        self.id_num = location_id
        self.brief_description = brief_description
        self.long_description = long_description
        self.available_commands = available_commands
        self.items = items
        self.enemies = enemies
        self.visited = visited
        self.possible_commands = possible_commands


@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - name: The name of the item
        - description: A brief description of the item
        - target_position: The position or location where the item is intended to be used
        - target_points: The number of points the item affects
        - use_effect: A list of effects the item has when used

    Representation Invariants:
        - len(self.name) > 0
        - len(self.description) > 0
        - self.target_points >= 0
    """

    # NOTES:
    # This is just a suggested starter class for Item.
    # You may change these parameters and the data available for each Item object as you see fit.
    # (The current parameters correspond to the example in the handout).
    #
    # The only thing you must NOT change is the name of this class: Item.
    # All item objects in your game MUST be represented as an instance of this class.

    name: str
    description: str
    target_position: int
    target_points: int
    use_effect: list[any]


@dataclass
class Entity:
    """An entity in our text adventure game world.

    Instance Attributes:
       - inventory: A list containing all the items the entity is carrying
        - health: The current health of the entity
        - levels: The level or experience ranking of the entity
        - attack_damage: The amount of damage the entity deals in combat

    Representation Invariants:
        - isinstance(self.inventory, list)
        - self.health >= 0
        - self.levels >= 0
        - self.attack_damage >= 0
    """
    inventory: list[str]
    health: int
    levels: int
    attack_damage: int


@dataclass
class Player(Entity):
    """The player in our text adventure game world.

    Instance Attributes:
        - base_health: The starting health of the player
        - health_additions: Additional health gained from levels or items

    Representation Invariants:
        - self.base_health > 0
        - self.health_additions >= 0
    """
    base_health: int
    health_additons: int


@dataclass
class Enemy(Entity):
    """The enemies in our text adventure game world.

    Instance Attributes:
        - name: The name of the enemy
        - description: A brief description of the enemy
        - lines: A list of phrases or dialogue lines the enemy might say

    Representation Invariants:
        - len(self.name) > 0
        - len(self.description) > 0
        - isinstance(self.lines, list)
        - all(isinstance(line, str) for line in self.lines)
        - len(self.lines) > 0
    """
    name: str
    description: str
    lines: list[str]


# Note: Other entities you may want to add, depending on your game plan:
# - Puzzle class to represent special locations (could inherit from Location class if it seems suitable)
# - Player class
# etc.

if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
