# C3 Relay Rumbler

A proof-of-concept tool that attempts to retrieve the configuration from the memory dump of an [F-Secure C3](https://labs.f-secure.com/tools/c3/) Relay executable.

Currently supported channels (both negotiation and non-negotiation):
- Dropbox
- Slack
- GitHub
- GoogleDrive
- UNC
- LDAP

This tool will also parse the dump for channel URLs (e.g. `github.com`), as well as [artefacts](https://gist.github.com/ajpc500/9ae6eb427375438f906b0bf394813bc5) from C3 DLLs and shellcode.

Lastly, the parser will check for the presence of pipe strings (i.e. `\\.\pipe\`) and return these. Pipe names present could suggest the presence of peripherals (e.g. a Cobalt Strike beacon) having been deployed in the relay process.

> Tested with C3 release versions 1.2.0 and 1.3.0

## Limitations

- This only parses configs from dumps of Relay executables, i.e. not DLLs or shellcode.

- For DLLs and shellcode, only the URL parsing and DLL artefacts will be checked.

- Only returns the initially configured channel, i.e. not those added post-execution - though checks for URLs could infer additional channels.

- Some trailing characters may be present in parsed config entries, using `-v` will print the bytes being analysed for manual evaluation.

- Support for more channels to be added.

## Usage

Help menu:

```
python3 relayrumbler.py -h
usage: relayrumbler.py [-h] [-f FILE] [-v] [-l] [-c] [-b]

Read values from file

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path of memory dump
  -v, --verbose         Print raw output of config as hex
  -l, --list-channels   Show loaded channels and quit.
  -c, --no-colour       No colours in printed output.
  -b, --no-banner       Do not print banner.
```

List channels loaded into the config (`config.py`):

```
 python3 relayrumbler.py -b --list-channels

[*] Listing channels loaded in config...

[+] Dropbox
- Known Arguments:
    User Agent
    Token
    Folder
- Channel types:
    negotiation
    non-negotiation
- URLS:
    dropboxapi.com

[+] Slack
- Known Arguments:
    Token
    Channel Name
- Channel types:
    negotiation
    non-negotiation
- URLS:
    slack.com
    ...
```

Example output for LDAP relay:

```
python3 relayrumbler.py -f Relay_x64_e965_LDAP.dmp

  _____   ____     ______ _______        _______ __   __
 / ____| |___ \   |_____/ |______ |      |_____|   \_/        @ajpc500
| |        __) |  |    \_ |______ |_____ |     |    |
| |       |__ <    ______ _     _ _______ ______         _______  ______
| |____   ___) |  |_____/ |     | |  |  | |_____] |      |______ |_____/
 \_____| |____/   |    \_ |_____| |  |  | |_____] |_____ |______ |    \_

________________________________________________________________________



[*] Looking for offset for config...
[+] Found offset (matching LDAP negotiation channel): 597078

[*] Checking for peripherals via pipe strings check...
[*] No pipe strings found.

[*] Attempting to parse C3 relay config...
[+] Found 7 config entries.

---------- RELAY CONFIG -----------
 |- Channel: LDAP
 |- Type: Negotiation

 |- Negotiation Identifier: xsu1vwza
 |- Data Attribute: mSMQSignCertificates
 |- Lock Attribute: primaryInternationalISDNNumber
 |- Domain Controller: DC2.UK.MWR.COM
 |- Username: Administrator@uk.mwr.com
 |- Password: Password1!-
 |- DN: CN=Administrator,CN=users,DC=uk,DC=mwr,DC=com
-----------------------------------
```

Example output for dump of Internet Explorer process with injected Dropbox relay shellcode:

```
python3 relayrumbler.py -bf iexplore-with-relay.dmp
  
[+] Found C3 Relay Reflective DLL Artifacts.
 |- 9997304: NodeRelayDll_r64.dllStartNodeRelay
 |- 11983792: NodeRelayDll_r64.dllStartNodeRelay
 |- 13889755: NodeRelayDll_r64.dllStartNodeRelay

[+] Found Dropbox URLs.

[*] Looking for offset for config...
[!] Couldn't locate offset. Exiting...
```

Example output for dump of GoogleDrive relay with beacon deployed:
```
python3 relayrumbler.py -bf gdrive-with-beacon.dmp

[+] Found GoogleDrive URLs.

[*] Looking for offset for config...
[+] Found offset (matching GoogleDrive negotiation channel): 1557710

[*] Checking for peripherals via pipe strings check...
[+] Found pipe names:
  - \.\pipe\mypipe
  - \.\pipe\mypipe

[*] Attempting to parse C3 relay config...
[+] Found 6 config entries.

---------- RELAY CONFIG -----------
 |- Channel: GoogleDrive
 |- Type: Negotiation

 |- Negotiation Identifier: hu3wy3bk
 |- User Agent: [...]
 |- Client ID: [...].googleusercontent.com
 |- Client Secret: [...]
 |- Refresh Token: [...]
 |- Folder Name: [...]
-----------------------------------
```