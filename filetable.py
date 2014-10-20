import ast
import fileIO
import openSSL

def getFiletable(peer_name):
	filetable_name = 'CA/' + peer_name + '/filetable.dat'
	keyfile = 'CA/' + peer_name + '/' + peer_name + '.key'
	filetable_raw = None
	if fileIO.fileExists(filetable_name):
		ciphertext = fileIO.readFile(filetable_name)
		filetable_raw = openSSL.decrypt(keyfile, ciphertext)
	if filetable_raw:
		dictionary = ast.literal_eval(filetable_raw)
	else:
		dictionary = {}
	return dictionary

def storeFiletable(peer_name, dictionary):
	filetable_name = 'CA/' + peer_name + '/filetable.dat'
	keyfile = 'CA/' + peer_name + '/' + peer_name + '.key'
	# If we don't remove the file before rewriting it we get bad decrypts
	fileIO.removeFile(filetable_name)
	ciphertext = openSSL.encrypt(keyfile, str(dictionary))
	fileIO.writeFile(filetable_name, ciphertext)

def addFile(peer_name, filename, peer_id):
	dictionary = getFiletable(peer_name)
	dictionary[filename] = peer_id
	storeFiletable(peer_name, dictionary)

def removeFile(peer_name, filename):
	dictionary = getFiletable(peer_name)
	del dictionary[filename]
	storeFiletable(peer_name, dictionary)
