# mitmproxy - Resource Override

Forked from [heytric](https://github.com/heyrict/mitmproxy-resource-override), who got it from [kylepaulsen](https://github.com/kylepaulsen/mitmproxy-resource-override).
Added some minor debug output, fixed hostname in url (was IP in transparent mode). Furthermore, all files we are going to replace aren't downloaded from server anymore. (This fixes replacing bigger files, like a 400mb .exe...) Instead, we just request the Header with HTTP HEAD. Moved to RegEx instead of fixing the custom parsing stuff by [kylepaulsen](https://github.com/kylepaulsen/mitmproxy-resource-override).

# How to use
1. Install mitmproxy (see the other info section below if you have trouble)
2. Download this script.
3. Create a file called overrides.txt where you are going to run mitmproxy.
4. Put your override rules inside overrides.txt (See below for more details on this)
5. Run mitmproxy (--anticache is recommended):

<!-- Markdown is stupid - need to use a comment to turn off list formatting. -->

    $ mitmproxy -s override.py
    or
    $ mitmproxy --anticache -s override.py


# overrides.txt
This is the file where you define your url replace rules. Each rule is on its own line. The request part understands RegEx, the local side does not. I replaced the complicated star-syntax with python-build-in regex. Don't forget to escape / and .
The script will parse this file every time a request is made so you can change it without having to restart mitmproxy. Here is what one replace rule looks like:

```
http:\/\/example.com\/.*\.exe , some/evil/virus.exe
```

A rule is made up of a url, comma, and lastly a file path. See the table below for examples:

| Rule (URL , File Path)                                              | Requested URL                 | File Path That Is Used As Response |
|---------------------------------------------------------------------|-------------------------------|------------------------------------|
| http:\\/\\/example.com\\/dir\\/filename\\.exe , some/evil/virus.exe | Any .exe from example.com     | some/evil/virus.exe                |
| http:\\/\\/example.com\\/.*\\.exe , some/evil/virus.exe              | Any .exe from example.com     | some/evil/virus.exe                |
| http:\\/\\/.*\\.exe , some/evil/virus.exe                           | Any .exe from anywhere        | some/evil/virus.exe                |

# Other Info About mitmproxy

Install mitmproxy following the instructions here: https://mitmproxy.org/doc/install.html

OR TL;DR, Mac and Linux: Install pip and then run pip install mitmproxy

You might need to install some other dependencies if it fails (Read the error logs).

I needed to run:

    sudo apt-get install python-dev libxml2-dev libxslt-dev zlib1g-dev libffi-dev libssl-dev

You may want to add the Certificate Authority cert files to your computers trusted CAs. The certs are usally in ~/.mitmproxy . Google on how to do this.

# License

MIT
