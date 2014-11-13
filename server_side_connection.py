import secure_context
import network_protocol
import socket

class ServerSideConnection(object):

	def __init__(self, peer_name):
		# Just running locally, so the IP is always this
		ip = '127.0.0.1'
		# Set the portno based on the peer we're using
		if(peer_name == 'Jack'):
			portno = 5571
		elif(peer_name == 'Jane'):
			portno = 5572
		elif(peer_name == 'Joe'):
			portno = 5573
		else:
			print("Valid users are: Jack, Jane, or Joe")
		self.secure_socket = secure_context.createListeningServerSocket(
		 		peer_name, ip, portno)

	# Accepts the next connection. Must be called before send or recv
	def nextConnection(self):
		(client_connection, address) = self.secure_socket.accept()
		self.client_connection = client_connection

	# Sends data to the current connection
	def send(self, message):
		network_protocol.send(self.client_connection, message)

	# Receives data from the current connection
	def recv(self):
		return network_protocol.recv(self.client_connection)

	def getPeerInfo(self):
		return self.client_connection.getpeercert()['subject']

	# Closes the current connection
	# Should be called before calling nextConnection again
	def done(self):
		self.client_connection.shutdown(socket.SHUT_RDWR)

