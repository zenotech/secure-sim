import libdecode

import key

my_key = key.key

print my_key

secret_key = libdecode.decode(my_key)

print 'Key: ' + secret_key