Note the Discovery Server is hardcoded to Port 4040
Should this port be in use, please kill the PID using it before compiling

Run discovery.py first with:
python3 discovery.py

Run any rooms you'd wish to create with room.py in the format of:
python3 room.py -d Basement Foyer "The entry way to an old house. Weathered, but still tidy and clean. A doorway leads away from the room downwards." Vase rug

Run player.py lastly in the format of:
python3 player.py Bob Foyer
