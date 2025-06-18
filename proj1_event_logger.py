"""CSC111 Project 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of this event's location
    - description: Long description of this event's location
    - next_command: String command which leads this event to the next event, None if this is the last game event
    - next: Event object representing the next event in the game, or None if this is the last game event
    - prev: Event object representing the previous event in the game, None if this is the first game event

    Representation Invariants:
    - self.id_num > 0
    - isinstance(self.description, str) and len(self.description) > 0
    - self.next_command is None or isinstance(self.next_command, str)
    - self.next is None or isinstance(self.next, Event)
    - self.prev is None or isinstance(self.prev, Event)
    - self.item_interaction is None or isinstance(self.item_interaction, str)
    - self.entity_interaction is None or isinstance(self.entity_interaction, dict)
    """

    id_num: int
    score: int
    item_interaction: Optional[str] = None
    entity_interaction: Optional[dict[str, any]] = None
    next_command: Optional[str] = None
    next: Optional[Event] = None
    prev: Optional[Event] = None


class EventList:
    """
    A linked list of game events.

    Instance Attributes:
        - first: The first event in the list, or None if the list is empty.
        - last: The last event in the list, or None if the list is empty.

    Representation Invariants:
        - (self.first is not None and self.last.next is None) or (self.first is None and self.last is None)
    """
    first: Optional[Event]
    last: Optional[Event]

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def display_events(self) -> None:
        """Display all events in chronological order."""
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}, Score: {curr.score}, "
                  f"Item: {curr.item_interaction}, Enemy: {curr.entity_interaction}")
            curr = curr.next

    def is_empty(self) -> bool:
        """Return whether this event list is empty."""
        curr = self.first

        return curr is None

    def add_event(self, event: Event, command: Optional[str] = None, item_interaction: Optional[str] = None,
                  entity_interaction: Optional[dict[str, any]] = None) -> None:
        """Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.
        """
        if self.is_empty():
            self.first = event
            self.last = event

        else:
            self.last.next = event
            self.last.next.prev = self.last
            self.last.next_command = command
            self.last = event
            self.last.next = None
            if item_interaction is not None:
                self.last.prev.item_interaction = item_interaction
            if entity_interaction is not None:
                self.last.prev.entity_interaction = entity_interaction

    def remove_last_event(self) -> None:
        """Remove the last event from this event list.
        If the list is empty, do nothing."""

        if self.is_empty():
            return

        elif self.first == self.last:
            self.first = None
            self.last = None

        else:
            self.last = self.last.prev
            self.last.next = None
            self.last.next_command = None
            self.last.item_interaction = None

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence."""
        curr = self.first
        location_ids = []
        while curr is not None:
            location_ids.append(curr.id_num)
            curr = curr.next
        return location_ids

    def get_command_log(self) -> list[tuple[str | None, int]]:
        """ Rerturns a list of all commands used for each event in this list along with the given location ID"""
        curr = self.first
        commands = []
        while curr is not None:
            commands.append((curr.next_command, curr.id_num))
            curr = curr.next
        return commands

    # Note: You may add other methods to this class as needed but DO NOT CHANGE THE SPECIFICATION OF ANY OF THE ABOVE


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
