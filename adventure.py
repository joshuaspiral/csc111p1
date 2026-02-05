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

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from game_entities import Location, Item
from event_logger import Event, EventList

# Game Constants
MAX_MOVES = 50
FIND_POINT_VALUE = 5
REQUIRED_ITEMS = ["usb drive", "laptop charger", "lucky mug"]
TARGET_LOCATION = 4

# ANSI Color Codes
"""ANSI escape codes for terminal colors."""
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# Backgrounds
BG_BLUE = "\033[44m"
BG_GREEN = "\033[42m"
BG_RED = "\033[41m"


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The ID of the player's current location.
        - ongoing: Whether the game is still in progress.
        - inventory: List of Item objects the player is carrying.
        - score: The player's current score.
        - moves: Number of moves the player has made.
        - max_moves: Maximum moves allowed before losing.
        - found_items: Set of item names that have been picked up (for scoring).
        - deposited_items: Set of item names deposited at target (for scoring).

    Representation Invariants:
        - self.current_location_id in self._locations
        - self.moves >= 0
        - self.score >= 0
    """

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int
    ongoing: bool
    inventory: list[Item]
    score: int
    moves: int
    max_moves: int
    found_items: set[str]
    deposited_items: set[str]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """
        self._locations, self._items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True
        self.inventory = []
        self.score = 0
        self.moves = 0
        self.max_moves = MAX_MOVES
        self.found_items = set()
        self.deposited_items = set()

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        # TODO: Add Item objects to the items list; your code should be structured similarly to the loop above
        for item_data in data['items']:
            item_obj = Item(item_data['name'], item_data['description'], item_data['start_position'],
                            item_data['target_position'], item_data['target_points'])
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        # TODO: Complete this method as specified
        if loc_id is None:
            return self._locations[self.current_location_id]
        return self._locations[loc_id]

    def find_item_by_name(self, name: str) -> Optional[Item]:
        """Return the Item object with the given name, or None if not found."""
        for item in self._items:
            if item.name.lower() == name.lower():
                return item
        return None

    def check_win_condition(self) -> bool:
        """Check if the player has won by depositing all required items at the target location."""
        target_loc = self.get_location(TARGET_LOCATION)
        return all(item_name in target_loc.items for item_name in REQUIRED_ITEMS)

    def check_lose_condition(self) -> bool:
        """Check if the player has lost by exceeding maximum moves."""
        return self.moves >= self.max_moves

    def process_command(self, command: str, log: EventList) -> str:
        """Process a command, updating game state and log, and returning a result message."""
        loc = self.get_location()
        parts = command.lower().strip().split(" ", 1)
        verb = parts[0]
        noun = parts[1] if len(parts) > 1 else ""

        if verb == "quit":
            self.ongoing = False
            return ""
        elif verb == "look":
            return loc.long_description
        elif verb == "inventory":
            lines = ["Inventory:"]
            if not self.inventory:
                lines.append("  (empty)")
            else:
                for item in self.inventory:
                    lines.append(f"  - {item.name}")
            return "\n".join(lines)
        elif verb == "score":
            return f"Current Score: {self.score}\nMoves: {self.moves}/{self.max_moves}"
        elif verb == "log":
            log.display_events()
            return ""
        elif command in loc.available_commands:
            next_id = loc.available_commands[command]
            # SImple Puzzle: Entering Robarts (ID 3) requires 'tcard'
            if next_id == 3 and not any(i.name == 'tcard' for i in self.inventory):
                return "You try to enter Robarts Library, but the turnstile gate is locked.\nYou need your T-Card to tap in."

            self.current_location_id = next_id
            self.moves += 1
            new_loc = self.get_location()
            log.add_event(Event(new_loc.id_num, new_loc.long_description), command)
            return ""
        elif verb == "take" or (verb == "pick" and noun.startswith("up ")):
            if verb == "pick":
                noun = noun[3:]
            if noun in loc.items:
                loc.items.remove(noun)
                item_obj = self.find_item_by_name(noun)
                if item_obj:
                    self.inventory.append(item_obj)
                    msg = f"You picked up the {noun}."
                    if noun not in self.found_items:
                        self.score += FIND_POINT_VALUE
                        self.found_items.add(noun)
                    return msg
                return "Error: Item data not found."
            return "You don't see that here."
        elif verb == "drop":
            item = None
            for it in self.inventory:
                if it.name.lower() == noun.lower():
                    item = it
                    break

            if item:
                self.inventory.remove(item)
                loc.items.append(item.name)
                msg = f"You dropped the {noun}."
                if loc.id_num == item.target_position and item.name not in self.deposited_items:
                    msg += f"\nYou deposited the {item.name} in the correct place! (+{item.target_points} points)"
                    self.score += item.target_points
                    self.deposited_items.add(item.name)
                return msg
            return "You aren't carrying that."
        elif verb == "examine":
            target = None
            for it in self.inventory:
                if it.name.lower() == noun.lower():
                    target = it
                    break
            if not target and noun in loc.items:
                target = self.find_item_by_name(noun)
            if target:
                return target.description
            return "You don't see that here."

        return "I don't understand that command."


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    game_log = EventList()
    game = AdventureGame('game_data.json', 1)
    menu = ["look", "inventory", "score", "log", "quit"]

    # Welcome banner
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{YELLOW}  CSC111 TEXT ADVENTURE: The Missing Project Files {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{DIM}Find your USB drive, laptop charger, and lucky mug!{RESET}")
    print(f"{DIM}Return them to your dorm before the 1pm deadline.{RESET}\n")

    # Log starting location
    start_loc = game.get_location()
    game_log.add_event(Event(start_loc.id_num, start_loc.long_description), None)

    while game.ongoing:
        location = game.get_location()

        # Check win condition
        if game.check_win_condition():
            print(f"\n{BOLD}{BG_GREEN}{WHITE} 🎉 CONGRATULATIONS! 🎉 {RESET}")
            print(f"{GREEN}You have returned all the missing items to your dorm room!{RESET}")
            print(f"{BOLD}Final Score: {YELLOW}{game.score}{RESET}")
            game.ongoing = False
            break

        # Check lose condition
        if game.check_lose_condition():
            print(f"\n{BOLD}{BG_RED}{WHITE} ⏰ TIME'S UP! ⏰ {RESET}")
            print(f"{RED}It's 1:00pm! The deadline has passed.{RESET}")
            print(f"{DIM}You ran out of time. GAME OVER.{RESET}")
            game.ongoing = False
            break

        # Location header
        print(f"\n{BOLD}{BG_BLUE}{WHITE} LOCATION {location.id_num} {RESET}")
        if not location.visited:
            print(f"{CYAN}{location.long_description}{RESET}")
            location.visited = True
        else:
            print(f"{DIM}{location.brief_description}{RESET}")

        # Show items at location
        if location.items:
            print(f"\n{YELLOW}✨ You see: {BOLD}{', '.join(location.items)}{RESET}")

        # Display possible actions
        print(f"\n{MAGENTA}{'─'*40}{RESET}")
        print(f"{BOLD}Commands:{RESET} {DIM}look, inventory, score, log, quit{RESET}")
        print(f"{BOLD}Movement:{RESET}", end=" ")
        actions = list(location.available_commands.keys())
        print(f"{GREEN}{', '.join(actions)}{RESET}" if actions else f"{DIM}(none){RESET}")

        # Get input
        choice = input(f"\n{BOLD}{WHITE}> {RESET}").lower().strip()

        print(f"{DIM}{'─'*40}{RESET}")

        # Process command
        result_msg = game.process_command(choice, game_log)
        if result_msg:
            # Color the result based on content
            if "picked up" in result_msg or "deposited" in result_msg:
                print(f"{GREEN}{result_msg}{RESET}")
            elif "don't" in result_msg or "aren't" in result_msg or "locked" in result_msg:
                print(f"{RED}{result_msg}{RESET}")
            elif "Inventory" in result_msg or "Score" in result_msg:
                print(f"{CYAN}{result_msg}{RESET}")
            else:
                print(result_msg)
