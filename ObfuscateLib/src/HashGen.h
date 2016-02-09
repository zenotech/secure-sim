

#include <openssl/sha.h>

void generateObfuscator(unsigned char hash[SHA384_DIGEST_LENGTH]){

	using namespace std;

	// Generate long string
    srand(101);
    string str = to_string(rand());
    while (str.size() < SHA384_DIGEST_LENGTH){
        str.append(to_string(rand()));
    }
	
	const unsigned char *ckey = reinterpret_cast<const unsigned char*>(str.c_str());

  	SHA384(ckey, sizeof(str.size()) - 1, hash);

  }