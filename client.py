import parse_params
import client_side_connection
import sys
import fileIO
import re
import dfs
import filetable
import refmon_client

peer_name = parse_params.getUsername(server_side = False)

print('Hello ', peer_name)

while True:
	print()
	print('What would you like to do?')
	print('1. View files')
	print('2. Store files')
	print('3. Retrieve files')
	print('4. Delete files')
	print('5. Add Authorization')
	print('6. Delete Authorization')
	print('7. Add Group Member')
	print('8. Delete Group Member')
	print('9. Exit')

	accepted = False
	while not accepted:
		# Running this on python3; input does not evaluate data
		value = input('1-9: ')
		if re.match('\A[1-9]\Z', value):
			accepted = True

	if(value == '1'):
		dictionary = filetable.getFiletable(peer_name)
		print()
		print('Here are all of your files:')
		if dictionary:
			for k, v in dictionary.items():
				print(k)
		else:
			print('You do not have any files stored')
	elif(value == '2'):
		print('What file would you like to store?')
		filename = input()
		if not fileIO.fileExists(filename):
			print('Sorry,', filename, 'is not a valid file')
			continue
		# Store the file on a random peer and add it to the filetable
		dfs.storeFile(peer_name, filename)
		# print(filename, 'stored')
	elif(value == '3'):
		print('Which file would you like to retrieve?')
		filename = input()
		# if filename not in filetable.getFiletable(peer_name):
		# 	print('Could not find', filename, 'in your file system')
		# 	continue
		if fileIO.fileExists(filename):
			print(filename, 'already exists on this machine!')
			print('Please move the file to avoid overwrites')
			continue
		# Retrieve and restore the file
		dfs.retrieveFile(peer_name, filename)
		# print(filename, 'restored')
	elif(value == '4'):
		print('Which file would you like to delete?')
		filename = input()
		# if filename not in filetable.getFiletable(peer_name):
		# 	print('Could not find', filename, 'in your file system')
		# 	continue
		# Delete the file
		dfs.deleteFile(peer_name, filename)
		# print(filename, 'deleted')
	elif(value == '5'):
		refmon_client.add_authorization(peer_name)
	elif(value == '6'):
		refmon_client.delete_authorization(peer_name)
	elif(value == '7'):
		refmon_client.add_group_member(peer_name)
	elif(value == '8'):
		refmon_client.delete_group_member(peer_name)
	elif(value == '9'):
		print('Goodbye', peer_name)
		sys.exit()
