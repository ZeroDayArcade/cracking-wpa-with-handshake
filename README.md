# Cracking WPA/WPA2 WiFi Passwords from a Captured Handshake
A python script for cracking WPA/WPA2 PSK passwords with a captured handshake.  

For capturing a handshake, see the other repo: <a href="https://github.com/ZeroDayArcade/capture-handshake-wpa-wifi-hacking">Capturing a 4-Way Handshake from WPA/WPA2 WiFi Networks with a Python Script</a>.

This script can crack WiFi passwords for WPA and WPA2 networks when supplied with information contained within captured packets from a 4-way handshake. In other words when supplied with: 
1. MIC
2. SSID
3. MAC address of the Access Point (AP)
4. MAC address of the Client
5. Nonce for the AP
6. EAPoL of Client (which includes Nonce for Client)

along with a passwords list.

A sample list of the top 100 passwords is included for testing. In a real world scenario, you'd typically use a much larger list. This script is for demonstration purposes and built for comprehension over speed. It is meant to help those looking to build their own cracking tools get started with a bare-bones example.

***Only ever hack a network you own and have legal permission to hack. This is for educational purposes only and to help you advance your penetration testing skills and knowledge.*** 

## Background Information

When a client machine connects to an access point (AP) such as a wireless router, a 4-way handshake takes place. Packets from this exchange can be captured by a third party listening for packets with a wireless adapter set to monitor or promiscuous mode. Contained within these packets is the information above, which ultimately contains the password to the WiFi network if the network is secured with a PSK. The reason this is not normally an issue is because the password is scrambled through several layers of encryption making the information seemingly useless.

However, the hashing functions that mask the true password can be used in conjunction with a list of common passwords in order to potentially crack the password and gain unauthorized access to the network. A hacker can take a list of potential passwords and run each one through the same hashing functions the access point uses to see if any produce the same MIC value that was captured in the 4-way handshake. If any of them do, then the hacker knows that they have the correct password. 

Note that this is much different than attempting to login to the network by typing in different passwords and seeing if any of them work. This process happens offline. Once the MIC and other information is obtained from the handshake, the hacker can make as many attempts as they want to find the password without having to interact with the Access Point again until they're ready to connect with the cracked password.


## How the script works

You can use our <a href="https://github.com/ZeroDayArcade/capture-handshake-wpa-wifi-hacking">WPA/WPA2 Handshake Capture script</a> to obtain a MIC (+Nonces and EAPoL frames) from an AP with a ~$10 WiFi adapter. This will also produce a `WPA*02` hashcat hc22000 format hash line that you can run directly with this script (see below). Alternatively you can obtain this information with <a href="https://github.com/ZerBea/hcxdumptool">hcxdumptool</a> or the <a href="https://github.com/risinek/esp32-wifi-penetration-tool">ESP32 Wi-Fi Penetration Tool</a>.

This script (`crack_handshake.py`) does the password cracking that comes after the MIC / Nonces/ EAPoL frames have been obtained from the Access Point.

To generate a potential matching MIC with a test password from the passwords list, the following steps are taken:
1. A PMK (Pairwise Master Key) is computed using a cryptographic function called PBKDF2 with the test password and SSID as inputs
2. A PTK is then calculated from the PMK, the MAC addresses from the AP and Client, and Nonces from the AP and Client as inputs.
3. A MIC is then computed from the first 16 bytes of the PTK (the KCK), and data from an EAPoL frame.

In order to crack a password, `crack_handshake.py` simply loops through a list of likely passwords and does the above 3 steps with each test password until a matching MIC is found. It is essentially a less sophisticated, CPU-based way of doing something similar to what hashcat does with a dictionary attack in hash mode 22000 with known MIC + Nonces + EAPoL frames.

Personally, I like to have short and simple code examples to build off of, or to port to other languages. All of the code uses only standard python libraries. There's only about ~70 total lines of python, and without print statements and spaces it's closer to ~40 lines total.

## Running the script

This script is built to work with hashcat hash lines (hc22000 format) out of the box. For those unfamiliar, these hash lines contain all of the information described above when they start with `WPA*02`. To attempt a crack with one of these hash lines simply run:
```
python3 crack_handshake.py """<WPA02_HASHCAT_HC22000_FORMAT_HASHLINE>""" <PASSWORD_LIST_SRC>
```
**IMPORTANT:** When running the script in this manor make sure to use triple quotes around the hash line. Otherwise characters like `*` in the hash line can cause the script to run incorrectly and can cause weird problems in your Terminal. 

Note that `<PASSWORD_LIST_SRC>` can be ommited to simply use the sample `passlist.txt` file that comes with this repo.

The script can also be imported by other python scripts and the `crack_handshake()` function can be supplied with parameters like so: 
```
crack_handshake(mic, mac_ap, mac_cl, essid, nonce_ap, nonce_cl, eapol_client)
```
The function expects each parameter to be a valid byte string.

## Getting and Testing the Script:
Clone the project:
```
git clone https://github.com/ZeroDayArcade/cracking-wpa-with-handshake.git
```
cd into project directory:
```
cd cracking-wpa-with-handshake
```
Test the script with a hashcat example:
```
python3 crack_handshake.py """WPA*02*024022795224bffca545276c3762686f*6466b38ec3fc*225edc49b7aa*54502d4c494e4b5f484153484341545f54455354*10e3be3b005a629e89de088d6a2fdc489db83ad4764f2d186b9cde15446e972e*0103007502010a0000000000000000000148ce2ccba9c1fda130ff2fbbfb4fd3b063d1a93920b0f7df54a5cbf787b16171000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac040100000fac040100000fac028000*a2""" passlist.txt
```

Another hashcat example from the hashcat forums (<a href="https://hashcat.net/forum/thread-10253-page-2.html">Source</a>):

```
python3 crack_handshake.py """WPA*02*1709ba709b92c3eb7b662036b02e843c*6c5940096fb6*64cc2edaeb52*6c686c64*ca37bb6be93179b0ce86e0f4e393d742fca6854ace6791f29a7d0c0ec1534086*0103007502010a00000000000000000001f09960e32863aa57ba250769b6e12d959a5a1f1cc8939d6bed4401a16092fa72000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac040100000fac040100000fac020000*00"""
```

Our sample password list is enough to successfully crack both of these examples. And of course you can always supply your own passwords list, or add your own passwords to passlist.txt. 

This script was tested on several versions of Linux including Kali Linux running on a x86-64 Intel machine and Raspian (on a Raspberry Pi 4/ARM processor) as well as on macOS and Windows. It was tested with hashcat examples from the hashcat forums and with real captured frames from a simple penetration test with a weak password. It should work on pretty much everything running Python 3, and was tested with Python 3.7 through 3.11.


## Acknowledgements
`passlist.txt` is a sample list taken from the top 100 most common passwords put together by Daniel Miessler. I've added "hashcat!" to the list for the example hash. See the original list here:
https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt

<br/>  

# More Zero Day Arcade Resources:
**Learn Reverse Engineering, Assembly, Code Injection and More:**  
🎓  <a href="https://zerodayarcade.com/tutorials">zerodayarcade.com/tutorials</a> 

**More WiFi Hacking with Simple Python Scripts:**  
<a href="https://github.com/ZeroDayArcade/capture-pmkid-wpa-wifi-hacking">Capturing PMKID from WiFi Networks</a>  
<a href="https://github.com/ZeroDayArcade/wpa-password-cracking-with-pmkid/">Cracking WiFi Passwords with PMKID</a>  
<a href="https://github.com/ZeroDayArcade/capture-handshake-wpa-wifi-hacking">Capturing 4-Way Handshake from WPA/WPA2 Networks</a>  

# Find Hacking Bounties in Gaming:
🎮  <a href="https://zerodayarcade.com/bounties">zerodayarcade.com/bounties</a>

