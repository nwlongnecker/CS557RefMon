import parse_params
import server_side_connection
import server_methods

peer_name = parse_params.getUsername(server_side = True)

net = server_side_connection.ServerSideConnection(
	peer_name = peer_name)

print('Server Started, Waiting for connections...')

while True:
	net.nextConnection()

	command = net.recv()

	if(command == 'Store'):
		server_methods.storeFile(peer_name, net)

	elif(command == 'Retrieve'):
		server_methods.retrieveFile(peer_name, net)

	elif(command == 'Delete'):
		server_methods.deleteFile(peer_name, net)

	net.done()
