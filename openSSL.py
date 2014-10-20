# Helper module for interfacing with OpenSSL

import fileIO
import subprocess
import uuid

# Hashes the input to a key
# @param String plaintext The string to hash
# @return Returns the hashed key
def hash(plaintext, outputType = '-hex'):
	hashKey = None
	retval = 0
	try:
		# name the temporary files randomly
		# since the client and server are in the same dir, sometimes
		# when both tried to use openSSL simultaneously there were collisions
		temp_name = str(uuid.uuid1())
		plaintext_file = 'p' + temp_name
		key_file = 'k' + temp_name
		# write out input / create output files
		fileIO.writeFile(plaintext_file, plaintext)
		fileIO.writeFile(key_file, '')
		# run openssl hash command
		retval = subprocess.call(['openssl', 'dgst', '-sha256', outputType, '-out', key_file, plaintext_file])
		# read in the output
		hashKey = fileIO.readFile(key_file)
	finally:
		# delete temp files
		fileIO.removeFile(plaintext_file)
		fileIO.removeFile(key_file)
		# return the output
		if hashKey is None or retval != 0:
			raise Exception('Hash failed')
		else:
			return hashKey.replace('SHA256(plain.tmp)= ', '', 1)

# Decrypts the cipher with the given key
# @param String keyfile The keyfile to use when decrypting the cipher
# @param String cipher The encrypted text
# @return Returns the cipher in plaintext
def decrypt(keyfile, ciphertext):
	plaintext = None
	retval = 0
	try:
		# name the temporary files randomly
		# since the client and server are in the same dir, sometimes
		# when both tried to use openSSL simultaneously there were collisions
		temp_name = str(uuid.uuid1())
		plaintext_file = 'p' + temp_name
		cipher_file = 'c' + temp_name
		# write out input / create output files
		fileIO.writeFile(plaintext_file, '')
		fileIO.writeFile(cipher_file, ciphertext)
		# run openssl dec command
		with open(keyfile) as f:
			retval = subprocess.call(['openssl', 'enc', '-d', '-aes-256-cbc', '-a', '-pass', 'stdin', '-out', plaintext_file, '-in', cipher_file], stdin=f)
		# read in the output
		plaintext = fileIO.readFile(plaintext_file)
	finally:
		# delete temp files
		fileIO.removeFile(plaintext_file)
		fileIO.removeFile(cipher_file)
		# return the output
		if plaintext is None or retval != 0:
			raise Exception('Decrypt failed')
		else:
			return plaintext

# Encrypts the plaintext with the given key
# @param String keyfile The keyfile to use when encrypting the plaintext
# @param String plaintext The text to encrypt
# @return Returns the encrypted plaintext
def encrypt(keyfile, plaintext):
	ciphertext = None
	retval = 0
	try:
		# name the temporary files randomly
		# since the client and server are in the same dir, sometimes
		# when both tried to use openSSL simultaneously there were collisions
		temp_name = str(uuid.uuid1())
		plaintext_file = 'p' + temp_name
		cipher_file = 'c' + temp_name
		# write out input / create output files
		fileIO.writeFile(plaintext_file, plaintext)
		fileIO.writeFile(cipher_file, '')
		# run openssl enc command
		with open(keyfile) as f:
			retval = subprocess.call(['openssl', 'enc', '-aes-256-cbc', '-a', '-pass', 'stdin', '-out', cipher_file, '-in', plaintext_file], stdin=f)
		# read in the output
		ciphertext = fileIO.readFile(cipher_file)
	finally:
		# delete temp files
		fileIO.removeFile(plaintext_file)
		fileIO.removeFile(cipher_file)
		# return the output
		if ciphertext is None or retval != 0:
			raise Exception('Encrypt failed')
		else:
			return ciphertext
