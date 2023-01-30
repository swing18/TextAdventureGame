import argparse
import signal
import socket
import sys
from urllib.parse import urlparse

# fixed port for the discovery service
port = 4040
#initialize
discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# storing each server room in a list of dictionaries
registered_servers =[]

#to exit gracefully 
def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

# Function to accept and set up clients.
def register_server(message):
   
    #split message into REGISTER name, address
    words = message.split()

    # is server list empty?
    if not registered_servers:
        registered_servers.append({'roomName':words[1],'roomPort':words[2]})
        return 'OK'
    else:
        # see if roomName or roomPort already exist in registry
        for x in registered_servers:
            for index in range(len(registered_servers)):
                for key in registered_servers[index]:
                    if registered_servers[index][key]==words[1] or registered_servers[index][key]== words[2]:
                        #print('NOTOK' 'Port number or Server name already exist in registry'+registered_servers[index][key])
                        # ensure port and name is unique, exit if not
                        return 'NOTOK' ' Port number or Server name already exist in registry'
        # add to register if unique
        registered_servers.append({'roomName':words[1],'roomPort':words[2]})
        return 'OK'
        


def deregister_server(message):
    words = message.split()
    
     # is server list empty?
    if not registered_servers:
        return 'NOTOK no servers to deregister'
    else:
        # see if roomName already exists in registry
       for index in range(len(registered_servers)):
            for key in registered_servers[index]:
             if registered_servers[index][key]==words[1]:
                print('removed ' + registered_servers[index][key])
                registered_servers.pop(index)
                return 'OK'
    # if not return an error
    #print('NOTOK server not in register')
    return 'NOTOK server not in register'


def lookup_server(message):
    words = message.split()
    # search through list to find which index coresponds to said name

    if not registered_servers:
        return 'NOTOK no servers to lookup'
    else:
        # see if roomName exists in registry
       for index in range(len(registered_servers)):
            for key in registered_servers[index]:
                 if registered_servers[index][key]==words[1]:
                    #print('returning '+registered_servers[index]['roomPort'])
                    return 'OK '+ registered_servers[index]['roomPort']
    #if not return an error
    return 'NOTOK server does not exist'
        
    

    



def handle_message(message,addr):
    words =message.split()
    # process based on LOOKUP REGISTER OR DEREGISTER

    if(words[0]=='REGISTER'):
        reply=register_server(message)
        discovery_socket.sendto(reply.encode(),addr)

    elif(words[0]=='DEREGISTER'):
        reply=deregister_server(message)
        discovery_socket.sendto(reply.encode(),addr)

    elif(words[0]=='LOOKUP'):
        reply=lookup_server(message)
        discovery_socket.sendto(reply.encode(),addr)

    # Otherwise, the command is bad.

    else:
        reply= "Invalid command"
        discovery_socket.sendto(reply.encode(),addr)
    return
    
def main():

    global discovery_socket

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)


  
   
    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    discovery_socket.bind(('', port))
    print('Discovery Service will wait for clients at port: ' + str(discovery_socket.getsockname()[1]))

    # Loop forever waiting for messages from clients.

    while True:

        # Receive a packet from a client and process it.

        message, addr = discovery_socket.recvfrom(1024)
        
        # Process the message and retrieve a response.

        handle_message(message.decode(), addr)

        # Send the response message back to the client.

        

if __name__ == '__main__':
    main()



