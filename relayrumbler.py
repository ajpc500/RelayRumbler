import sys, os, argparse, re, string
from configs import *

class relayRumbler:


    def printBanner(self):
        print(r"""     
  _____   ____     ______ _______        _______ __   __                
 / ____| |___ \   |_____/ |______ |      |_____|   \_/        @ajpc500          
| |        __) |  |    \_ |______ |_____ |     |    |         
| |       |__ <    ______ _     _ _______ ______         _______  ______
| |____   ___) |  |_____/ |     | |  |  | |_____] |      |______ |_____/
 \_____| |____/   |    \_ |_____| |  |  | |_____] |_____ |______ |    \_

________________________________________________________________________
        """)

    
  
    def print_error(self, message):
        print(f"{self.ERROR}{message}{self.ENDC}")

    def print_success(self, message):
        print(f"{self.SUCCESS}{message}{self.ENDC}")
    
    def readFile(self, file):
        with open(file, 'rb') as f:
            self.data = f.read()

    def printConfigEntry(self, arg_name, entry):
        print(" |- {}: {}".format(arg_name, entry)) 

    def parseConfig(self):
        offset = self.config_offset
        byte_separator = b"\x00\x00\x00"
        pattern = re.compile(b"(?s).*?"+byte_separator)

        print("[*] Attempting to parse C3 relay config...")

        count = 0
        found_args = []
        for m in re.finditer(pattern, self.data[offset:]):
            if count == (len(configs.CHANNEL_DETAILS[self.channel]["args"])+(1 if self.is_negotiation_channel else 2)):
                break #count is greater than known args plus one or two for (non)negotiation channel
            value_entry = self.data[offset+m.start():offset+m.end()-len(byte_separator)]

            try:
                found_args.append(b''.join(re.findall(b"[ -~]", re.sub(b"\x00\x00.*$", b"", value_entry))).decode())
            except:
                found_args.append("(raw){}".format(value_entry))
            count+=1
        
        self.print_success("[+] Found {} config entries.".format(count))

        arg_map_index = 0
        
        print("\r\n---------- RELAY CONFIG -----------")
        self.printConfigEntry("Channel", self.channel)
        self.printConfigEntry("Type", "Negotiation\n" if self.is_negotiation_channel else "Non-negotiation\n")
        
        for arg in found_args:
            if arg_map_index == 0:
                if self.is_negotiation_channel:
                    self.printConfigEntry("Negotiation Identifier", arg)
                else:
                    self.printConfigEntry("Input ID", arg)
            elif arg_map_index ==1 and not self.is_negotiation_channel:
                self.printConfigEntry("Output ID", arg)
            else:
                index = arg_map_index-1 if self.is_negotiation_channel else arg_map_index-2
                value_name = configs.CHANNEL_DETAILS[self.channel]["args"][index]
                self.printConfigEntry(value_name, arg)
            arg_map_index+=1
        print("-----------------------------------")

    def stringTriage(self):
        # https://gist.github.com/ajpc500/9ae6eb427375438f906b0bf394813bc5
        rdll_strings = [ 
            b"NodeRelayDll_r64.dll.StartNodeRelay", 
            b"NodeRelayDll_r86.dll.StartNodeRelay"
        ]
        for relay_dll in rdll_strings:
            if len(re.findall(relay_dll, self.data)) > 0:
                self.print_success("\n[+] Found C3 Relay Reflective DLL Artifacts.")      
                for m in re.finditer(relay_dll, self.data):
                    self.print_success(" |- {}: {}".format(m.start(), self.data[m.start():m.end()].decode()))
        print()

    def parseChannel(self):
        for channel in configs.CHANNEL_DETAILS:               
            if "urls" in configs.CHANNEL_DETAILS[channel].keys():
                for url in configs.CHANNEL_DETAILS[channel]["urls"]:
                    if len(re.findall(url.encode(), self.data)) > 0:
                        self.print_success("[+] Found {} URLs.".format(channel))      
                        break

    def findConfigOffset(self):
        print("\n[*] Looking for offset for config...")

        found_offset = False
        for channel in configs.CHANNEL_DETAILS:
            if found_offset:
                break

            for offset in configs.CHANNEL_DETAILS[channel]["offsets"]:
                self.config_offset = self.data.find(configs.CHANNEL_DETAILS[channel]["offsets"][offset])+len(configs.CHANNEL_DETAILS[channel]["offsets"][offset])

                if(self.config_offset > len(configs.CHANNEL_DETAILS[channel]["offsets"][offset])):
                    self.print_success("[+] Found offset (matching {} {} channel): {}\n".format(channel, offset, str(self.config_offset)))
                    found_offset = True
                    self.channel = channel
                    self.is_negotiation_channel = True if offset == "negotiation" else False
                    break
            
        if not found_offset:
            self.print_error("[!] Couldn't locate offset. Exiting...")
            exit()

    def printConfigBlock(self):
        print("----------- RAW OUTPUT ------------")
        print(self.data[self.config_offset:self.config_offset+234])
        print("-----------------------------------\n")

    def listChannels(self):
        print("\n[*] Listing channels loaded in config...\n")
        for channel in configs.CHANNEL_DETAILS:
            channel_types = configs.CHANNEL_DETAILS[channel]["offsets"].keys() 
            
            self.print_success("[+] {}".format(channel))
            print("- Known Arguments: \n    {}".format('\n    '.join(configs.CHANNEL_DETAILS[channel]["args"])))
            print("- Channel types: \n    {}".format('\n    '.join(configs.CHANNEL_DETAILS[channel]["offsets"].keys())))
            
            if "urls" in configs.CHANNEL_DETAILS[channel].keys():
                print("- URLS:\n    {}".format('\n    '.join(configs.CHANNEL_DETAILS[channel]["urls"])))
            print()

    def pipeCheck(self):
        print("[*] Checking for peripherals via pipe strings check...")
        
        byte_separator = b"\x00\x00\x00"
        pipe_prefix = b"\\\\\\.\\\pipe\\\\"
        pattern = re.compile(pipe_prefix + b".*?" + byte_separator)

        found_args = []
        for m in re.finditer(pattern, self.data):
            value_entry = self.data[m.start():m.end()-len(byte_separator)]

            try:
                found_args.append(b''.join(re.findall(b"[ -~]", re.sub(b"\x00\x00.*$", b"", value_entry))).decode())
            except:
                found_args.append("(raw){}".format(value_entry))
        if found_args:
            self.print_success("[+] Found pipe names:")
            print('  - {}'.format('\n  - '.join(found_args)))
        else:
            print("[*] No pipe strings found.")
        print()

    def __init__(self, no_colour):
        self.data = {}
        self.config_offset = 0
        self.channel = ''
        self.is_negotiation_channel = False
        
        #logging
        self.SUCCESS = '' if no_colour else '\033[92m'
        self.ERROR = '' if no_colour else '\033[91m'
        self.ENDC = '' if no_colour else '\033[0m'
            

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Read values from file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', action='store', dest='file', required=False, help='Path of memory dump')
    group.add_argument('-l', '--list-channels', action='store_true', dest='list_channels', required=False, help='Show loaded channels and quit.')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', required=False, help='Print raw output of config as hex')
    parser.add_argument('-c', '--no-colour', action='store_true', dest='no_colours', required=False, help='No colours in printed output.')
    parser.add_argument('-b', '--no-banner', action='store_true', dest='no_banner', required=False, help='Do not print banner.')

    args = parser.parse_args()

    rr = relayRumbler(args.no_colours)

    if not args.no_banner:
        rr.printBanner()

    if args.list_channels:
        rr.listChannels()
    elif args.file:
        rr.readFile(args.file)
        rr.stringTriage()
        rr.parseChannel()
        rr.findConfigOffset()

        if args.verbose:
            rr.printConfigBlock()

        rr.pipeCheck()        
        rr.parseConfig()