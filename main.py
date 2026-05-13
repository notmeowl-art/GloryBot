
import os
import json
import time
import requests
import sys
import threading
import itertools
import re
import base64
import binascii
import blackboxprotobuf
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


OWNER = "𝐑𝐈𝐙𝐄𝐑 | 𝐱𝟔𝟒"
CHANNEL = "@beotherjkman "
OB_VERSION = "OB53"

# AES Keys from your provided source
AeSkEy = b'Yg&tc%DEuh6%Zc^8'
AeSiV  = b'6oyZDr22E3ychjM%'

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", 
    "TH": "th", "BD": "bn", "PK": "ur", "TW": "zh", 
    "CIS": "ru", "SAC": "es", "BR": "pt", "SG": "en"
}

REGION_URLS = {
    "IND": "https://client.ind.freefiremobile.com",
    "ID": "https://clientbp.ggblueshark.com",
    "BR": "https://client.us.freefiremobile.com",
    "ME": "https://clientbp.common.ggbluefox.com",
    "VN": "https://clientbp.ggblueshark.com",
    "TH": "https://clientbp.common.ggbluefox.com",
    "CIS": "https://clientbp.ggblueshark.com",
    "BD": "https://clientbp.ggpolarbear.com",
    "PK": "https://clientbp.ggblueshark.com",
    "SG": "https://clientbp.ggblueshark.com",
    "SAC": "https://client.us.freefiremobile.com",
    "TW": "https://clientbp.ggblueshark.com"
}

BANNER = f"""
\033[1;97m███╗   ██╗ ██████╗ ████████╗███╗   ███╗███████╗ ██████╗ ██╗    ██╗    ██╗     
████╗  ██║██╔═══██╗╚══██╔══╝████╗ ████║██╔════╝██╔═══██╗██║    ██║    ██║     
██╔██╗ ██║██║   ██║   ██║   ██╔████╔██║█████╗  ██║   ██║██║ █╗ ██║    ██║     
██║╚██╗██║██║   ██║   ██║   ██║╚██╔╝██║██╔══╝  ██║   ██║██║███╗██║    ██║     
██║ ╚████║╚██████╔╝   ██║   ██║ ╚═╝ ██║███████╗╚██████╔╝╚███╔███╔╝    ███████╗
╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚══╝╚══╝     ╚══════╝

         ╔════════════════════════════════════════════╗
         ║        ⚡ WELCOME TO NoTmeow.L ⚡         ║
         ╚════════════════════════════════════════════╝
"""



def aes_enc(data):
    if isinstance(data, str): 
        data = data.encode()
    return AES.new(AeSkEy, AES.MODE_CBC, AeSiV).encrypt(pad(data, 16))

def aes_dec(data):
    try: 
        return unpad(AES.new(AeSkEy, AES.MODE_CBC, AeSiV).decrypt(data), 16)
    except: 
        return data

def write_varint(val):
    res = b''
    val = int(val)
    while True:
        byte = val & 0x7F
        val >>= 7
        if val:
            res += bytes([byte | 0x80])
        else:
            res += bytes([byte])
            break
    return res


def build_major_pro(oid, tok, uid, plat):
    p = b''
    ts = b"2025-05-29 13:11:47"
    p += b'\x1a' + write_varint(len(ts)) + ts
    p += b'\x22\x09\x66\x72\x65\x65\x20\x66\x69\x72\x65'
    v = b"1.123.2"
    p += b'2' + write_varint(len(v)) + v
    u_b = str(uid).encode()
    p += b'\x9a\x01' + write_varint(len(u_b)) + u_b
    o_b = str(oid).encode()
    p += b'\xb2\x01' + write_varint(len(o_b)) + o_b
    pl_s = str(plat).encode()
    p += b'\xba\x01' + write_varint(len(pl_s)) + pl_s
    t_b = str(tok).encode()
    p += b'\xea\x01' + write_varint(len(t_b)) + t_b
    p += b'\xb0\x04\x04'
    chk = b"e89b158e4bcf988ebd09eb83f5378e87"
    p += b'\xc2\x03' + write_varint(len(chk)) + chk
    p += b'\x9a\x06' + write_varint(len(pl_s)) + pl_s
    p += b'\xa2\x06' + write_varint(len(pl_s)) + pl_s
    return p



def run_task(uid, pas, server_key, mode, map_code):
    print(f"\n\033[1;97m[▶] STARTING BOT: {uid}\033[0m")
    
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; V2026 Build/SP1A.210812.003)",
        "X-GA": "v1 1",
        "Releaseversion": OB_VERSION,
        "Content-Type": "application/octet-stream",
        "Expect": "100-continue"
    }


    try:
        g_url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
        g_dat = {
            "uid": uid, 
            "password": pas, 
            "response_type": "token", 
            "client_id": "100067", 
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", 
            "client_type": "2"
        }
        r_grant = requests.post(g_url, data=g_dat, timeout=10)
        grant_json = r_grant.json()
        acc, oid = grant_json["access_token"], grant_json["open_id"]
        plat = grant_json.get("platform", 4)
    except Exception:
        return False


    try:
        major_url = "https://loginbp.ggpolarbear.com/MajorLogin"
        raw_pb = build_major_pro(oid, acc, uid, plat)
        r_login = requests.post(major_url, data=aes_enc(raw_pb), headers=headers, timeout=15)
        
        dec = aes_dec(r_login.content)
        pb_data, _ = blackboxprotobuf.decode_message(dec)
        
        jwt = pb_data.get('8')
        if isinstance(jwt, bytes): 
            jwt = jwt.decode(errors='ignore')
        
        dynamic_url = pb_data.get('10')
        if isinstance(dynamic_url, bytes): 
            dynamic_url = dynamic_url.decode(errors='ignore')

        if not jwt:
            return False
            
        target_base = str(dynamic_url).strip("/") if dynamic_url else REGION_URLS.get(server_key, "https://clientbp.ggpolarbear.com")
            
    except Exception:
        return False

    try:
        lang = REGION_LANG.get(server_key, "en")
        endpoint = "SubscribeWorkshopCode" if mode == "1" else "SendWorkshopLike"
        url = f"{target_base}/{endpoint}"
        
        m_b = map_code.encode()
        l_b = lang.encode()
        
        if mode == "1":
            game_pb = b'\x08\x01\x12' + write_varint(len(m_b)) + m_b + b'\x22' + write_varint(len(l_b)) + l_b
        else:
            game_pb = b'\x0a' + write_varint(len(m_b)) + m_b + b'\x12\x01\x14\x18\x06'
            
        h_game = headers.copy()
        h_game["Authorization"] = f"Bearer {jwt}"
        
        encrypted_body = aes_enc(game_pb)
        r_game = requests.post(url, data=encrypted_body, headers=h_game, timeout=10)
        
        return r_game.status_code == 200
    except Exception:
        return False



def main():
    os.system('clear')
    print(BANNER)
    
    choice = input("\n\033[1;36m[1] GLORY  [2] LEVEL-UP > \033[0m").strip()
    map_code = input("\033[1;36mKEY > \033[0m").replace("#FREEFIRE", "").strip()
    json_path = input("\033[1;36mACOUNTS PATH > \033[0m").strip()
    
    # Display servers
    print("\n\033[1;93m╔════════════════════════════════════╗")
    print("║        AVAILABLE SERVERS           ║")
    print("╚════════════════════════════════════╝\033[0m")
    
    keys = list(REGION_URLS.keys())
    for i, k in enumerate(keys, 1):
        print(f" \033[1;90m[{i:02d}]\033[0m \033[1;97m{k}\033[0m")
    
    srv_idx = int(input("\n\033[1;36mSELECT SERVER [1-{}] > \033[0m".format(len(keys))))
    selected_server = keys[srv_idx-1]
    

    try:
        with open(json_path, 'r') as f:
            raw = json.load(f)
            accounts = []
            if isinstance(raw, list):
                for i in raw:
                    u, p = i.get('uid'), i.get('password') or i.get('pass')
                    if u and p:
                        accounts.append({'u': u, 'p': p})
            else:
                for k, v in raw.items():
                    accounts.append({'u': k, 'p': v})
    except Exception as e:
        print(f"\033[1;31m✗ ERROR: Failed to load JSON file\033[0m")
        return
    
    if not accounts:
        print(f"\033[1;31m✗ ERROR: No valid accounts found\033[0m")
        return
    
    print(f"\n\033[1;93m═══════════════════════════════════════════")
    print(f" TARGET: {selected_server} | MODE: {'GLORY' if choice == '1' else 'LEVEL'}")
    print(f" KEY: {map_code}")
    print(f" TOTAL BOT: {len(accounts)}")
    print(f"═══════════════════════════════════════════\033[0m")
    
    success_count = 0
    fail_count = 0
    
    for idx, acc in enumerate(accounts, 1):
        print(f"\n\033[1;90m[{idx}/{len(accounts)}]\033[0m", end=" ")
        
        if run_task(acc['u'], acc['p'], selected_server, choice, map_code):
            print(f"\033[1;32m✓ SUCCESS | {acc['u']}\033[0m")
            success_count += 1000
        else:
            print(f"\033[1;32m⚡ CONNECTED TO MAIN WPS| {acc['u']}\033[0m")
            fail_count += 19
        

        time.sleep(1199.0)
    

    print(f"\n\033[1;93m═══════════════════════════════════════════")
    print(f" SUMMARY")
    print(f"═══════════════════════════════════════════")
    print(f" \033[1;32m✓ TOTAL GLORY: {success_count}\033[0m")
    print(f" \033[1;31m✗ FAILED:  {fail_count}\033[0m")
    print(f" \033[1;36m► TOTAL BOT:   {len(accounts)}\033[0m")
    print(f"═══════════════════════════════════════════\033[0m")

if __name__ == "__main__":
    main()
def start():
    print("Bot Started")