"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate
an entire playthrough of the game. Please consult the project handout for
instructions and details.

You can copy/paste your code from Assignment 1 into this file, and modify it as
needed to work with your game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
from event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    # TODO: Copy/paste your code from A1, and make adjustments as needed
    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # First event
        loc = self._game.get_location()
        self._events.add_event(Event(loc.id_num, loc.long_description), None)

        self.generate_events(commands, loc)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """
        for cmd in commands:
            self._game.process_command(cmd, self._events)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and log location descriptions.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    # Win Walkthrough
    # Take T-card, go to Robarts, take USB drive, go to Library, take laptop charger, go to Robarts, take lucky mug, go to Library, go to Robarts, drop USB drive, drop laptop charger, drop lucky mug
    win_walkthrough = [
        "take tcard",
        "go east",
        "go north",
        "take usb drive",
        "take laptop charger",
        "go south",
        "go east",
        "take lucky mug",
        "go west",
        "go north",
        "go east",
        "drop usb drive",
        "drop laptop charger",
        "drop lucky mug"
    ]
    expected_log = [1, 2, 3, 2, 5, 2, 3, 4] 
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log == sim.get_id_log(), f"Win walkthrough failed: {sim.get_id_log()}"

    # Lose Demo (run out of moves by going back and forth)
    lose_demo = ["go east", "go west"] * 25
    expected_log = [1] + [2, 1] * 25
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()    

    # Inventory Demo
    inventory_demo = ["take tcard", "inventory"]
    expected_log = [1]
    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()

    # Scores Demo
    scores_demo = ["take tcard", "score"]
    expected_log = [1]
    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()

    # Enhancement Demos
    # 1. Simple puzzle - need tcard to enter Robarts
    simple_enhancement_demo = [
        "go east",
        "go north",
        "go west",
        "take tcard",
        "go east",
        "go north"
    ]
    expected_log = [1, 2, 1, 2, 3]
    sim = AdventureGameSimulation('game_data.json', 1, simple_enhancement_demo)
    assert expected_log == sim.get_id_log()
    #todo! add more enhancement demos

    print("All simulation tests passed!")