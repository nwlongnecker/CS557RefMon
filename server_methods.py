import server_side_connection
import openSSL
import fileIO
import os
import subprocess

tmp_file_dir = "files/"

def storeFile(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	filename = net.recv()
	file_contents = net.recv()

	fileIO.writeFile(tmp_file_dir + '/' + filename, file_contents)

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'execute', client_common_name, 'put', filename], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))
	fileIO.removeFile(tmp_file_dir + '/' + filename)

	print('Stored', filename, 'for', client_common_name)

def retrieveFile(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	filename = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'execute', client_common_name, 'get', filename], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	result = out.decode("utf-8")

	if(result == "Success"):
		file_contents = fileIO.readFile(tmp_file_dir + '/' + filename)
		net.send(file_contents)
	else:
		net.send(result)

	net.send(result)
	fileIO.removeFile(tmp_file_dir + '/' + filename)

	print('Retrieved', filename, 'for', client_common_name)

def deleteFile(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	filename = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'execute', client_common_name, 'del', filename], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))

	print('Deleted', filename, 'for', client_common_name)

def getFilenames(peer_name, net):
	l = os.listdir(tmp_file_dir)
	net.send(str(l))
	print(peer_name, 'requested a list of their files')

def addAuthorization(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	grantee = net.recv()
	operator = net.recv()
	filename = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'add_authorization', client_common_name, grantee, operator, filename], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))

def deleteAuthorization(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	grantee = net.recv()
	operator = net.recv()
	filename = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'delete_authorization', client_common_name, grantee, operator, filename], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))

def addGroupMember(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	grantee = net.recv()
	group = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'add_group_member', client_common_name, grantee, group], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))

def deleteGroupMember(peer_name, net):
	peer_info = net.getPeerInfo()
	client_common_name = peer_info[4][0][1]

	grantee = net.recv()
	group = net.recv()

	os.chdir('refmon')
	process = subprocess.Popen(['ocaml', 'RefMon.ml', peer_name, 'delete_group_member', client_common_name, grantee, group], stdout=subprocess.PIPE)
	out, err = process.communicate()
	os.chdir('..')

	net.send(out.decode("utf-8"))
