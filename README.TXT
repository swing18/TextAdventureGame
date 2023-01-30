How to play the game: 

Setup:

Run discovery.py first with:
python3 discovery.py

Next, create any rooms you'd wish to create with room.py in the format of:
python3 room.py -(direction of an adjacent room, ie: -u, -d etc.) (adjacent room name) (room name) "(room description)" (list of items in the room)
Example:
python3 room.py -d Basement Foyer "The entry way to an old house. Weathered, but still tidy and clean. A doorway leads away from the room downwards." Vase rug

Enter a player into the game by running player.py in the format of:
python3 player.py (Player Name) (Room name) 
Example:
python3 player.py Bob Foyer


Commands:
look:  Display the name, description, and contents of the room including other players.
take:  Take an item from the room and add it to the player's inventory.  The item must exist in the room to be taken.
drop:  Take an item from the player's inventory and add it to the room.  The item must exist in the player's inventory to be dropped.
inventory:  List the player's inventory.
exit:  The player leaves the game, dropping any items in their inventory into the room before leaving.  The game client then terminates.
north south east west up down: Move a player to a room in that direction if one exists.
say: send a message that other players in the room can see. (Ex: say Hello bob!)

Notes:
A room must be created for a player to join it.
Possible room directions are u,d,n,s,e,w.

The Discovery Server is hardcoded to Port 4040.
Should this port be in use, please kill the PID using it before compiling

This project was created in Western University's CS3357A course as a multipart assignment. The code in this repository was from the end of semester cumalitive submission. Note on potential code similairty. Professor Mike Katchabaw told all students to use his solutions to the previous assigment to complete the upcoming assignment. 
Assignment Grade: 100%
Due Date: December 8th 2022
Final Submission Course Weight: 25%
