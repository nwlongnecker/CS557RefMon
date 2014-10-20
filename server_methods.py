import server_side_connection
import openSSL
import fileIO
import base64

def getPeerDir(peer_name, peer_info):
	# I wanted to hash the peer directory but had difficulty
	# with it so I just use peer name in plaintext
	encoded_peer_id = str(peer_info[4][0][1])
	peer_directory = 'CA/' + peer_name + '/' + encoded_peer_id
	fileIO.checkDir(peer_directory)
	return peer_directory

def storeFile(peer_name, net):
	peer_info = net.getPeerInfo()
	peer_directory = getPeerDir(peer_name, peer_info)

	filename = net.recv()
	file_contents = net.recv()

	fileIO.writeFile(peer_directory + '/' + filename, file_contents)

	client_common_name = peer_info[4][0][1]
	print('Stored', filename, 'for', client_common_name)

def retrieveFile(peer_name, net):
	peer_info = net.getPeerInfo()
	peer_directory = getPeerDir(peer_name, peer_info)

	filename = net.recv()
	file_contents = fileIO.readFile(peer_directory + '/' + filename)
	net.send(file_contents)

	client_common_name = peer_info[4][0][1]
	print('Retrieved', filename, 'for', client_common_name)

def deleteFile(peer_name, net):
	peer_info = net.getPeerInfo()
	peer_directory = getPeerDir(peer_name, peer_info)

	filename = net.recv()
	fileIO.removeFile(peer_directory + '/' + filename)

	client_common_name = peer_info[4][0][1]
	print('Deleted', filename, 'for', client_common_name)

