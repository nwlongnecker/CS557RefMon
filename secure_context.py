import ssl
import socket


# Create a secure context for all socket communication
def createSecureContext(peer_name) :
	# Only allow TLS 1.2 (Most secure, requires OpenSSL 1.0.1)
	secure_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
	# Use this peer's certificate and key for authentication
	secure_context.load_cert_chain(
		'CA/' + peer_name + '/' + peer_name + '.crt',
		'CA/' + peer_name + '/' + peer_name + '.key')
	# Only recognize peers signed by the CA
	secure_context.load_verify_locations(
		'CA/DistFileSysCA/signing-ca-1.crt')
	# Require all connections to present a certificate
	secure_context.verify_mode = ssl.CERT_REQUIRED
	# Use ciphers that are at least 128 bit
	secure_context.set_ciphers('HIGH')
	return secure_context

# Create a connection for a client. Ready to send when it returns
def createConnectedClientSocket(peer_name, hostip, portno):
	# Create a secure context for this connection
	secure_context = createSecureContext(peer_name)
	# Create a socket in the secure context
	secure_socket = secure_context.wrap_socket(socket.socket(), server_side = False)

	# Allow reuse of the port
	secure_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Connect to the specified IP
	secure_socket.connect((hostip, portno))
	return secure_socket

# Create a listening socket for the server. Ready to accept when it returns
def createListeningServerSocket(peer_name, ip, portno):
	# Create a secure context for this connection
	secure_context = createSecureContext(peer_name)
	# Load Diffie Helman key generation parameters
	# so the server can use Diffie Helman key exchange
	# file generated using:
	# openssl dhparam -outform PEM -out dh.rand -check -2
	secure_context.load_dh_params('CA/DistFileSysCA/dh.rand')
	# Do not reuse the same DH key during this SSL session
	ssl.OP_SINGLE_DH_USE = True

	# Create a socket in the secure context
	secure_socket = secure_context.wrap_socket(socket.socket(), server_side = True)

	# Allow reuse of the port
	secure_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Bind to the specified ip
	secure_socket.bind((ip, portno))
	# Listen for connections
	secure_socket.listen(5)
	return secure_socket