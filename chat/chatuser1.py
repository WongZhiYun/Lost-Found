import socket  #Import the socket library for network programming

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket (IPv4, TCP)

server.bind(("127.0.0.1", 9999))  # Must bind before listen

server.listen(1) # Start listening for incoming connections 
# 1 = maximum number of queued connections

client, addr = server.accept()# Accept a connection from a client


done = False   #Flag to control when the chat should stop
 
while not done:
    # Receive message from client (up to 1024 bytes)
    msg = client.recv(1024).decode('utf-8')
    if msg == 'quit':      # If the message is "quit", end the chat
        done = True
    else:
        print(msg)         # Otherwise, print the client's message
    client.send(input("Message: ").encode('utf-8'))      # Ask server user to type a reply and send it back to the client


client.close()
server.close()
