import scapy.all as scapy
import sqlite3
import requests
import random
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# --- CONFIGURATION ---
NETWORK_RANGE = "10.0.0.0/24" 
DB_NAME = "network_data.db"

# We generate a random number so your channel is unique to you
# You can change this string to anything you want (e.g. "my_secure_network_01")
unique_id = random.randint(1000, 9999)
NTFY_URL = f"https://ntfy.sh/net_sentry_admin_{unique_id}"

def send_alert(mac, ip):
    """
    Sends a push notification to your phone via ntfy.sh
    """
    print(f"📨 Sending Alert for {ip}...")
    try:
        # Professional Message Format
        message = f"🚨 SECURITY ALERT 🚨\nUnauthorized Device Detected.\nIP: {ip}\nMAC: {mac}"
        requests.post(NTFY_URL, data=message)
    except Exception as e:
        print(f"Failed to send alert: {e}")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            ip TEXT,
            first_seen TEXT,
            last_seen TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def scan_network():
    print(f"--- 📡 Scanning {NETWORK_RANGE} ---")
    
    # 1. SCAN
    arp_request = scapy.ARP(pdst=NETWORK_RANGE)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast/arp_request
    answered_list = scapy.srp(packet, timeout=2, verbose=False)[0]
    
    # 2. DB UPDATE
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    found_macs = []
    
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        found_macs.append(mac)
        
        cursor.execute("SELECT * FROM devices WHERE mac=?", (mac,))
        data = cursor.fetchone()
        
        if data is None:
            # --- ROGUE DEVICE LOGIC ---
            print(f"🚨 NEW DEVICE: {ip} ({mac})")
            
            # TRIGGER THE VOICE (NTFY)
            send_alert(mac, ip)
            
            cursor.execute("INSERT INTO devices VALUES (?, ?, ?, ?, ?)", 
                           (mac, ip, current_time, current_time, "Online"))
        else:
            print(f"✅ Update: {ip} is online.")
            cursor.execute("UPDATE devices SET last_seen=?, status=?, ip=? WHERE mac=?", 
                           (current_time, "Online", ip, mac))
    
    # 3. CLEANUP (OFFLINE LOGIC)
    if found_macs:
        placeholders = ', '.join('?' for _ in found_macs)
        query = f"UPDATE devices SET status='Offline' WHERE mac NOT IN ({placeholders})"
        cursor.execute(query, found_macs)
    else:
        cursor.execute("UPDATE devices SET status='Offline'")
        
    conn.commit()
    conn.close()
    print("--- Scan Complete. Waiting 60s... ---")

if __name__ == "__main__":
    init_db()
    scheduler = BlockingScheduler()
    scheduler.add_job(scan_network, 'interval', seconds=60)
    
    print("--- 🛡️ NET-SENTRY ENTERPRISE STARTED 🛡️ ---")
    print(f"🔔 NOTIFICATIONS ACTIVE: {NTFY_URL}")
    print("   (Click that link on your phone to subscribe)")
    
    # Run once immediately
    scan_network()
    
    # Start loop
    scheduler.start()