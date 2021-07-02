class configs():
    CHANNEL_DETAILS = {
        "Dropbox" : { 
            "urls": ["dropboxapi.com"],
            "offsets":{
                "negotiation": b"\x2a\xe5\x05\x3a\x08\x00\x00\x00",
                "non-negotiation": b"\x2a\xe5\x05\x3a\x04\x00\x00\x00"
            },
            "args": [ "User Agent", "Token", "Folder" ]
        },
        "Slack" : {
            "urls": ["slack.com"],
            "offsets": {
                "negotiation": b"\xe5\x2b\x1b\x08\x00\x00\x00",
                "non-negotiation": b"\xe5\x2b\x1b\x04\x00\x00\x00"
            },
            "args": [ "Token", "Channel Name" ]
        },
        "GitHub" : {
            "urls": ["github.com"],
            "offsets": {
                "negotiation": b"\x4f\x73\x08\x00\x00\x00",
                "non-negotiation": b"\x4f\x73\x04\x00\x00\x00"
            },
            "args": [ "Token", "Repository Name", "User Agent" ]
        },
        "GoogleDrive" : {
            "urls": ["googleapis.com", "googleusercontent.com"],
            "offsets": {
                "negotiation": b"\x49\xfe\x08\x00\x00\x00",
                "non-negotiation": b"\x49\xfe\x04\x00\x00\x00"
            },
            "args": [ "User Agent", "Client ID", "Client Secret", "Refresh Token", "Folder Name" ]
        },
        "UNC" : {
            "offsets": {
                "negotiation": b"\x2b\x31\x08\x00\x00\x00",
                "non-negotiation": b"\x2b\x31\x04\x00\x00\x00"
            },
            "args": [ "Filesystem Path" ]
        },
        "LDAP" : {
            "offsets": {
                "negotiation": b"\x43\xdf\x08\x00\x00\x00",
                "non-negotiation": b"\x43\xdf\x04\x00\x00\x00"
            },
            "args": [ "Data Attribute", "Lock Attribute", "Domain Controller", "Username", "Password", "DN" ]
        }
    }