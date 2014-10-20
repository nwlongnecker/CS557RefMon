# set up the CA itself

openssl genrsa -aes128 -out root-ca.key 2048
openssl req -new -x509 -days 3650 -key root-ca.key -out root-ca.crt -config openssl.cnf
openssl x509 -noout -text -in root-ca.crt
perl mk_new_ca_dir.pl DistFileSysCA
mv root-ca.crt DistFileSysCA/signing-ca-1.crt
mv root-ca.key DistFileSysCA/signing-ca-1.key
chmod -R go-rwx DistFileSysCA/

# User keys and certificates:

cd user_guttman
openssl req -newkey rsa:2048 -keyout guttman.key -config ../openssl.cnf -out guttman.req
openssl ca -config openssl.cnf -out user_guttman/guttman.crt -infiles user_guttman/guttman.req
