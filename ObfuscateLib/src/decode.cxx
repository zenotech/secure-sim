
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
#include <vector>

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

string decode(vector<unsigned char> obfuscatedKey){

    #if !(DEBUG) // Don't interfere with Xcode debugging sessions.
        disable_gdb();
    #endif

	// Hash the string to generate obfuscator
  	unsigned char hash[SHA384_DIGEST_LENGTH]; // == 48
  	generateObfuscator(hash);

	// Xor key to recover Key
    string originalKey;
	for(int i = 0; i < obfuscatedKey.size(); ++i){
        if (i > SHA384_DIGEST_LENGTH) {
            originalKey.push_back(obfuscatedKey[i] ^ hash[i - SHA384_DIGEST_LENGTH]);
        }
        else { 
            originalKey.push_back(obfuscatedKey[i] ^ hash[i]);
        }	
	}

	return originalKey;
}

#ifdef HAVE_BOOST
string decodePython(boost::python::object py_key){
	using namespace boost::python;
    
    //std::string object_classname = boost::python::extract<std::string>(py_key.attr("__class__").attr("__name__"));
	//cout << object_classname << endl;

	extract<boost::python::tuple> t(py_key);

	t.check();

	boost::python::tuple tup = t(); 

    vector<unsigned char> key_vector;

	for(int i = 0; i < len(tup); ++i){
        key_vector.push_back(extract<unsigned int>(tup[i]));
	}
 
	return decode(key_vector);
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

    vector<unsigned char> key_vector;

    while(getline(in, line).good()) {
        if (line == "};") {
            break;
        }
        line = line.substr(0,line.find(','));
        
        // Convert string to hex
        unsigned char c = std::stoi(line, 0, 16);
        key_vector.push_back(c);
    }

	string key = decode(key_vector);

	cout << "Key: " << key << endl;

}
