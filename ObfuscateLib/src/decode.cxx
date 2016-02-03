
#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <typeinfo>
#include <openssl/sha.h>

#include <dlfcn.h>
#include <sys/types.h>

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

	// Generate long string
	string className = typeid(std::string).name();
	if(className.size() < SHA_DIGEST_LENGTH){
		cout << "Auto generated string < hash length" << endl;
		exit(EXIT_FAILURE);
	}

	cout << "Str: " << className << endl;

	// Hash the string to generate obfuscator
  	unsigned char hash[SHA_DIGEST_LENGTH]; // == 20

	const unsigned char *ckey = reinterpret_cast<const unsigned char*>(className.c_str());

  	SHA1(ckey, sizeof(className.size()) - 1, hash);

  	cout << "Hash: " << hash << endl;

	// Xor key to recover Key
	unsigned char originalKey[SHA_DIGEST_LENGTH]; 
	for(int i = 0; i < SHA_DIGEST_LENGTH; ++i){
		originalKey[i] = obfuscatedKey[i] ^ hash[i];
	}

	string key = reinterpret_cast<char*>(originalKey);

	return key;
}

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
