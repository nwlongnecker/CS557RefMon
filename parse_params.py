import getopt
import sys
import os.path

def getUsername(server_side):
	if server_side:
		mode = 'server'
	else:
		mode = 'client'
	peer_name = None
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'u:', ['username='])
	except getopt.GetoptError:
		usage(mode)
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage(mode)
			sys.exit()
		elif opt in ('-u', '--username'):
			peer_name = arg

	if not peer_name:
		print('Please provide a username')
		usage(mode)
		sys.exit()
	elif not peerNameValid(peer_name):
		print('Could not find key and certificate for that user')
		print('Files expected:')
		print('CA/' + peer_name + '/' + peer_name + '.crt')
		print('CA/' + peer_name + '/' + peer_name + '.key')
		sys.exit()
	return peer_name

def usage(mode):
	print(mode + '.py -u <username>')

def peerNameValid(peer_name):
	return os.path.isfile('CA/' + peer_name + '/' + peer_name + '.crt') and os.path.isfile('CA/' + peer_name + '/' + peer_name + '.key')
