import socket

BLOCK_LEN = 1024

def send(socket, message):
	# Send the length of the message.
	# Should work as long as we send messages shorter than ~10 googol chars
	length = str(len(message)).encode('utf-8')
	socket.sendall(length)
	# Send the message
	socket.sendall(message.encode('utf-8'))

def recv(socket):
	# Get the length of the message
	lengthRemaining = int(socket.recv(BLOCK_LEN).decode('utf-8'))
	# Read until we've read the whole message
	message = ''
	while lengthRemaining > 0:
		message += socket.recv(BLOCK_LEN).decode('utf-8')
		lengthRemaining -= BLOCK_LEN
	return message