import client_side_connection
import peer_ip
import filetable
	
def add_authorization(peer_name):
	print('Who would you like to give authorization to?')
	grantee = input()
	print('What file would you like to give them access to?')
	filename = input()
	print('What operation would you like to allow them to do (get, put, or del)?')
	operation = input()

	# Look up which host has the file
	file_host = filetable.getFiletable(peer_name)[filename]
	# Use the peer_map to figure out the address of that host
	file_location = peer_ip.peer_map[file_host]

	# Connect to the appropriate host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))

	net.send('Add_Authorization')
	net.send(grantee)
	net.send(operation)
	net.send(filename)
	# print the response
	print(net.recv())

def delete_authorization(peer_name):
	print('Who would you like to remove authorization from?')
	grantee = input()
	print('What file would you like to remove access to?')
	filename = input()
	print('What operation would you like to restrict them from (get, put, or del)?')
	operation = input()

	# Look up which host has the file
	file_host = filetable.getFiletable(peer_name)[filename]
	# Use the peer_map to figure out the address of that host
	file_location = peer_ip.peer_map[file_host]

	# Connect to the appropriate host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))

	net.send('Delete_Authorization')
	net.send(grantee)
	net.send(operation)
	net.send(filename)
	# print the response
	print(net.recv())

def add_group_member(peer_name):
	print('What host would you like to modify groups for?')
	host = input()

	
	print('Who would you like to add to a group?')
	grantee = input()
	print('What group would you like to add them to?')
	group = input()

	# Look up which host has the file
	file_host = filetable.getFiletable(peer_name)[filename]
	# Use the peer_map to figure out the address of that host
	file_location = peer_ip.peer_map[file_host]

	# Connect to the appropriate host
	net = client_side_connection.ClientSideConnection(
		peer_name = peer_name, ip = file_location[0], portno = int(file_location[1]))
	
	net.send('Add_Group_Member')
	net.send(grantee)
	net.send(group)

def delete_group_member(peer_name):
	net.send('Delete_Group_Member')
	print("delete_group_member")