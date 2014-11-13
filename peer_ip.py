
# This map uses the peer subject section of their certificate as a key
# when looking up their IP and portnumber.
# This file could either be redistributed to all clients each time someone's
# ip changes or someone is added to the network, or it could be replaced by a
# broadcast system for finding other peers willing to host
peer_map = {
	"((('countryName', 'US'),), (('stateOrProvinceName', 'Massachusetts'),), (('organizationName', 'cs557'),), (('organizationName', 'Nathan Longnecker'),), (('commonName', 'Jack'),))":
	('127.0.0.1', '5571'),
	"((('countryName', 'US'),), (('stateOrProvinceName', 'Massachusetts'),), (('organizationName', 'cs557'),), (('organizationName', 'Nathan Longnecker'),), (('commonName', 'Jane'),))":
	('127.0.0.1', '5572'),
	"((('countryName', 'US'),), (('stateOrProvinceName', 'Massachusetts'),), (('organizationName', 'cs557'),), (('organizationName', 'Nathan Longnecker'),), (('commonName', 'Joe'),))":
	('127.0.0.1', '5573')
}
