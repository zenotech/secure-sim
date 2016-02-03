#include <dlfcn.h>
#include <sys/types.h>
#include <string>
#include <sstream>
#include <iomanip>
#include <openssl/sha.h>
#include <typeinfo>

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



unsigned char obfuscatedSecretKey[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF };

string ToHex(const string& s, bool upper_case /* = true */)
{
    ostringstream ret;

    for (string::size_type i = 0; i < s.length(); ++i)
        ret << std::hex << std::setfill('0') << std::setw(2) << (upper_case ? std::uppercase : std::nouppercase) << (int)s[i];

    return ret.str();
}



int main(int argc, char *argv[]) {
    #if !(DEBUG) // Don't interfere with Xcode debugging sessions.
        disable_gdb();
    #endif

    unsigned char obfuscator[SHA_DIGEST_LENGTH];

    std::string typestr = typeid(std::string).name();



      const unsigned char str[] = "Original String";
  unsigned char hash[SHA_DIGEST_LENGTH]; // == 20

  SHA1(str, sizeof(str) - 1, hash);

    // XOR the class name against the obfuscated key, to form the real key.
unsigned char actualSecretKey[sizeof(obfuscatedSecretKey)];
for (int i=0; i<sizeof(obfuscatedSecretKey); i++) {
    actualSecretKey[i] = obfuscatedSecretKey[i] ^ obfuscator[i];
}

}
