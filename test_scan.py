import scapy.all as scapy

def scan(ip):
    # 1. Create the ARP Request (The "Shout")
    # asking: "Who has this IP address?"
    arp_request = scapy.ARP(pdst=ip)
    
    # 2. Create the Broadcast Frame (The "Megaphone")
    # dst="ff:ff..." means send to EVERYONE on the network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # 3. Stack them together (Put the letter in the envelope)
    packet = broadcast/arp_request
    
    # 4. Send and wait for answer
    # srp = Send and Receive Packets
    answered_list = scapy.srp(packet, timeout=1, verbose=False)[0]
    
    # 5. Print results
    print("--- DEVICES FOUND ---")
    for element in answered_list:
        print(f"IP: {element[1].psrc}  |  MAC: {element[1].hwsrc}")

# Run the function
# IMPORTANT: This targets your Pi's network range
scan("10.0.0.0/24")