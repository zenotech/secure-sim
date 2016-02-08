

#include <openssl/sha.h>

void generateObfuscator(unsigned char hash[SHA384_DIGEST_LENGTH]){

	using namespace std;

	// Generate long string
	string className = typeid(std::string).name();
	
    if(className.size() < SHA384_DIGEST_LENGTH){
		cout << "Auto generated string < hash length" << endl;
		exit(EXIT_FAILURE);
	}

	const unsigned char *ckey = reinterpret_cast<const unsigned char*>(className.c_str());

  	SHA384(ckey, sizeof(className.size()) - 1, hash);

  }