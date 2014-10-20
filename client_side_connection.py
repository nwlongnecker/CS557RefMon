import secure_context
import network_protocol
import socket

class ClientSideConnection(object):

	def __init__(self, peer_name, ip, portno):
		self.secure_socket = secure_context.createConnectedClientSocket(
	 		peer_name, ip, portno)

	def send(self, message):
		network_protocol.send(self.secure_socket, message)

	def recv(self):
		return network_protocol.recv(self.secure_socket)

	def done(self):
		self.secure_socket.shutdown(socket.SHUT_RDWR)

	def getPeerInfo(self):
		return self.secure_socket.getpeercert()['subject']