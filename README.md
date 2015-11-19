# secure-sim
Utilities and libs for securing simulation data on 3rd Party HPC sites

## Solution 1
Solution 1 is a demo of using Asymetric keys to generate a shared secret and using that to encrpt data files to be sent to the HPC site.
### Getting started
To setup and configure the client from the source do the following:
```
virtualenv ./venv
. ./venv/bin/activate
pip install -f ./requirements.txt
python poc.commands.py generate_key
python poc.commands.py configure
```
Note: by default the tool will store the config file in your user profile, you can override this by setting the POC_CONFIG environment variable to another location.
