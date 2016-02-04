

Obfuscation Library

 Currently limited to 20 character/byte keys for demonstration purppose. Max 512 byte keys possible with SHA512 function in OpenSSL.


Build:

 Requires OpenSSL development packages
 For python interface boost python and python libs

 Use cmake to build


generate: creates a c++ header file and python file with obfuscated key.

decode: shared library that provides support to decode obfuscated key returning original key

decode_test: runs decode on a previously generated key.h file

python_test: runs decode on previously generated key.py file