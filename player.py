import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address.

server = ('', '')

# Discovery Server address.

discovery_server = ('', '')

# User name for tagging sent messages.

name = ''

# Inventory of items.

inventory = []

# Directions that are possible.

connections = { 
    "north" : "",
    "south" : "",
    "east" : "",
    "west" : "",
    "up" : "",
    "down" : ""
    }

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='exit'
    send_timeout(message.encode(), server)
    for item in inventory:
        message = f'drop {item}'
        send_timeout(message.encode(), server)
    sys.exit(0)

# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# function for the client to senc with a timeout
def send_timeout(message, address):
    
    client_socket.sendto(message, address)


    try:
        #start timer
        client_socket.settimeout(5)

        while(True):
            response, addr = client_socket.recvfrom(1024)
            if(response):
                client_socket.settimeout(None)
               
                break

    except socket.timeout as socketerror:
        print("Timeout - error, no reply from server, goodbye!")
        sys.exit(0)
    return response, addr 
        

# Function to join a room.
def join_room():
    message = f'join {name}'
 #   client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(5)
    client_socket.sendto(message.encode(), server)
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
        print('Something bad happened')
        sys.exit()
    print(response.decode())

# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command):

    global server

    # Parse command.

    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        response, addr = send_timeout(message.encode(), server)

    # Check for particular commands of interest from the user.

    # If we exit, we have to drop everything in our inventory into the room.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            send_timeout(message.encode(), server)
        sys.exit(0)

    # If we look, we will be getting the room description to display.

    elif (command == 'look'):
        print(response.decode())

    # If we inventory, we never really reached out to the room, so we just display what we have.

    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')

    # If we take an item, we let the server know and put it in our inventory, assuming we could take it.

    elif (words[0] == 'take'):
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])

    # If we drop an item, we remove it from our inventory and give it back to the room.

    elif (words[0] == 'drop'):
        print(response.decode())
        inventory.remove(words[1])

    # If we're wanting to go in a direction, we check with the room and it will tell us if it's a valid
    # direction.  We can then join the new room as we know we've been dropped already from the other one.

    elif (words[0] in connections):
       
        reply = response.decode().split()
        if (reply[0]=='OK'):
            server_address = 'room://localhost:'+reply[1]
            server_address = urlparse(server_address)
            host = server_address.hostname
            port = server_address.port
            server = (host, port)    
            print(server)
            join_room()      
        else:
            print(*reply)

    # The player wants to say something ... print the response.

    elif (words[0] == 'say'):
        print(response.decode())
        
    # Otherwise, it's an invalid command so we report it.

    else:
        print(response.decode())

# Function to handle incoming messages from room.  Also look for disconnect messages to shutdown.

def handle_message_from_server(sock, mask):
    response, addr = client_socket.recvfrom(1024)
    words=response.decode().split(' ')
    print()
    if len(words) == 1 and words[0] == 'disconnect':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(response.decode())
        do_prompt()

# Function to handle incoming messages from user.

def handle_keyboard_input(file, mask):
    line=sys.stdin.readline()[:-1]
    process_command(line)
    do_prompt()

# Our main function.

def main():

    global name
    global client_socket
    global server

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("room", help="room the user is starting in")
    args = parser.parse_args()
    
    # hardcoded address of discovery service
    
    discovery = 'room://localhost:4040'
    discovery_address = urlparse(discovery)
    host = discovery_address.hostname
    port = discovery_address.port  
    discovery_server = (host, port)

    # find the address of the starting room from discovery.py
    lookup_message = 'LOOKUP '+ args.room
     #send the message to discovery.py
    client_socket.sendto(lookup_message.encode(),discovery_server)
    
    while(True):
            
            discovery_reply, addr = client_socket.recvfrom(1024)
            if(discovery_reply):
                
                #print("received message from discovery")
                
                break
    
    print(discovery_reply.decode())
    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.
    reply = discovery_reply.decode().split()
   
    if(reply[0]!='OK'):
        print("The room you wpuld like to join does not exist....exiting")
        sys.exit(1)
    
    server_address = 'room://localhost:'+reply[1]
    server_address = urlparse(server_address)
    host = server_address.hostname
    port = server_address.port
    server = (host, port)
   
    name = args.name

    # Send message to enter the room.

    join_room()

    # Set up our selector.

    #client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)
    
    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while(True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)    


if __name__ == '__main__':
    main()
