

#include <openssl/sha.h>

void generateObfuscator(unsigned char hash[SHA_DIGEST_LENGTH]){

	using namespace std;

	// Generate long string
	string className = typeid(std::string).name();
	if(className.size() < SHA_DIGEST_LENGTH){
		cout << "Auto generated string < hash length" << endl;
		exit(EXIT_FAILURE);
	}

	//cout << "Str: " << className << endl;

	const unsigned char *ckey = reinterpret_cast<const unsigned char*>(className.c_str());

  	SHA1(ckey, sizeof(className.size()) - 1, hash);

  	//cout << "Hash: " << hash << endl;
  }