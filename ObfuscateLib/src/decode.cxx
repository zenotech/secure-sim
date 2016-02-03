
#ifdef HAVE_BOOST
#include <Python.h>
#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/list.hpp>
#endif

#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <typeinfo>
#include <openssl/sha.h>

#include <dlfcn.h>
#include <sys/types.h>



#include "HashGen.h"

using namespace std;

typedef int (*ptrace_ptr_t)(int _request, pid_t _pid, caddr_t _addr, int _data);
#if !defined(PT_DENY_ATTACH)
#define PT_DENY_ATTACH 31
#endif  // !defined(PT_DENY_ATTACH)

void disable_gdb() {
    void* handle = dlopen(0, RTLD_GLOBAL | RTLD_NOW);
    ptrace_ptr_t ptrace_ptr = (ptrace_ptr_t)dlsym(handle, "ptrace");
    ptrace_ptr(PT_DENY_ATTACH, 0, 0, 0);
    dlclose(handle);
}

string decode(unsigned char obfuscatedKey[SHA_DIGEST_LENGTH]){

    #if !(DEBUG) // Don't interfere with Xcode debugging sessions.
        disable_gdb();
    #endif

	// Hash the string to generate obfuscator
  	unsigned char hash[SHA_DIGEST_LENGTH]; // == 20
  	generateObfuscator(hash);

	// Xor key to recover Key
	unsigned char originalKey[SHA_DIGEST_LENGTH]; 
	for(int i = 0; i < SHA_DIGEST_LENGTH; ++i){
		originalKey[i] = obfuscatedKey[i] ^ hash[i];
	}

	string key = reinterpret_cast<char*>(originalKey);

	return key;
}

#ifdef HAVE_BOOST
string decodePython(boost::python::object py_key){
	using namespace boost::python;
    
    //std::string object_classname = boost::python::extract<std::string>(py_key.attr("__class__").attr("__name__"));
	//cout << object_classname << endl;

	extract<boost::python::tuple> t(py_key);

	t.check();

	boost::python::tuple tup = t(); 
	assert(len(tup) == SHA_DIGEST_LENGTH);

	unsigned char obfuscatedKey[SHA_DIGEST_LENGTH];

	for(int i = 0; i < SHA_DIGEST_LENGTH; ++i){
		obfuscatedKey[i] = extract<unsigned int>(tup[i]);
	}

	return decode(obfuscatedKey);
}

BOOST_PYTHON_MODULE(libdecode) {
  using namespace boost::python;

  def("decode", decodePython);
}
#endif

int main(int argc, char *argv[]){

	if(argc != 1){
		cout << "Usage: decode"  << endl;
		exit(EXIT_FAILURE);
	}

	// Read key
	ifstream in("key.h");
	string line;
	getline(in,line);
	getline(in,line);
	getline(in,line);

	unsigned char obfuscatedKey[SHA_DIGEST_LENGTH];
	for(int i = 0; i < SHA_DIGEST_LENGTH; ++i){
		getline(in,line);
		line = line.substr(0,line.find(','));
		
		// Convert string to hex
		unsigned char c = std::stoi(line, 0, 16);

		obfuscatedKey[i] = c;
	}

	string key = decode(obfuscatedKey);

	cout << "Key: " << key << endl;

}
