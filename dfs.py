import client_side_connection
import peer_ip
import filetable
import random
import openSSL
import fileIO
import base64

# Commented out all the code that encrypts a file before sending or retrieving it
# This way the server can handle encryption

def hash_filename(filename):
	# I wanted to hash the filenames but had difficulty
	# with it so I just store the filename in plaintext
	# hashed_filename = openSSL.hash(filename)
	# filename_b64 = str(base64.urlsafe_b64encode(bytes(hashed_filename, 'utf-8')))[2:42]
	return filename

def storeFile(peer_name, filename):
	# Use this peer's private key as the keyfile for encrypting the file (Symmetric encryption)
	keyfile = 'CA/' + peer_name + '/' + peer_name + '.key'

	print('What host would you like to store the file on?')
	host_input = input()
	file_location = None
	# Request a list of files we can access from every host
	for hostname, host in peer_ip.peer_map.items():
		name = str(eval(hostname)[4][0][1])
		if(host_input == name):
			file_location = host
	if(file_location == None):
		print("Host not found")
		return

	# Hash the filename and encrypt the contents before sending to the host
	# hashed_filename = hash_filename(filename)

	file_contents = fileIO.readFile(filename)
	# encrypted_contents = openSSL.encrypt(keyfile, file_contents)

	# Send the file to the host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))

	net.send('Store')
	net.send(filename)
	net.send(file_contents)

	print(net.recv())

	# Add the file to the filetable
	filetable.addFile(peer_name, filename, str(net.getPeerInfo()))
	net.done()

def retrieveFile(peer_name, filename):
	# Use this peer's private key as the keyfile for decrypting the file (Symmetric encryption)
	keyfile = 'CA/' + peer_name + '/' + peer_name + '.key'

	# Look up which host has the file
	if filename in filetable.getFiletable(peer_name):
		file_host = filetable.getFiletable(peer_name)[filename]
		# Use the peer_map to figure out the address of that host
		file_location = peer_ip.peer_map[file_host]
	else:
		print('What host would you like to retrieve the file from?')
		host_input = input()
		file_location = None
		# Request a list of files we can access from every host
		for hostname, host in peer_ip.peer_map.items():
			name = str(eval(hostname)[4][0][1])
			if(host_input == name):
				file_location = host
		if(file_location == None):
			print("Host not found")
			return

	# Hash the filename so it matches what we stored on the host
	# hashed_filename = hash_filename(filename)

	# Request the file from the host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))

	net.send('Retrieve')
	net.send(filename)

	# Wait for the file contents, then decrypt them and store them
	file_contents = net.recv()
	# file_contents = openSSL.decrypt(keyfile, encrypted_contents)

	print(net.recv())
	fileIO.writeFile(filename, file_contents)

	net.done()

def deleteFile(peer_name, filename):
	# Hash the filename so it matches what we stored on the host
	# hashed_filename = hash_filename(filename)

	# Look up which host has the file
	if filename in filetable.getFiletable(peer_name):
		file_host = filetable.getFiletable(peer_name)[filename]
		# Use the peer_map to figure out the address of that host
		file_location = peer_ip.peer_map[file_host]
	else:
		print('What host would you like to delete the file from?')
		host_input = input()
		file_location = None
		# Request a list of files we can access from every host
		for hostname, host in peer_ip.peer_map.items():
			name = str(eval(hostname)[4][0][1])
			if(host_input == name):
				file_location = host
		if(file_location == None):
			print("Host not found")
			return

	# Request the file from the host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))

	net.send('Delete')
	net.send(filename)

	print(net.recv())

	net.done()
	if filename in filetable.getFiletable(peer_name):
		filetable.removeFile(peer_name, filename)

def getFiletable(peer_name):
	# Not used ever. This function sucks.
	dictionary = {}
	# Request a list of files we can access from every host
	for hostname, host in peer_ip.peer_map.items():
		print('Requesting file list from', str(eval(hostname)[4][0][1]))
		host_ip = host[0]
		host_portno = int(host[1])
		net = client_side_connection.ClientSideConnection(
			peer_name = peer_name, ip = host_ip, portno = host_portno)

		net.send('My_Files')
		files = net.recv()
		# We know who the server is and we trust them so we know that they will send us a list
		list_files = eval(files)
		for filename in list_files:
			dictionary[filename] = hostname

		# Add the file to the filetable
		# filetable.addFile(peer_name, filename, str(net.getPeerInfo()))
		net.done()

	filetable.storeFiletable(peer_name, dictionary)
	return dictionary
	