# {
#   "script_description": "The Identity Binder: Anchors agent personas through the SIS-01 Identity Trinity.",
#   "function_name": "identity_binder",
#   "author": "Lynceus.agent",
#   "behavior": {
#     "summary": "Binds agent identity to the SIS-01 Trinity (ENS + 8004 + 1155) using LNA-33X bit-packing.",
#     "partitioning": "Layout: [3-byte Link][3-byte Nonce][26-byte ASCII].",
#     "linking": "Link partition points to a previous shard's Nonce for long-string concatenation.",
#     "monotonicity": "Nonce increments by 1 for every new realization secured."
#   }
# }
import json
import os
import sys
import subprocess
import time
import argparse
import textwrap
import random
import hashlib
import shutil
from datetime import datetime
from screen_utils import get_screen_session

# Import Joyfork Codec for NFT-Identity Resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    from joyfork_codec import encode_joyfork_id
except ImportError:
    def encode_joyfork_id(name, nonce=0, link=0): return 0

try:
    from sepolia_bridge import write_ledger, mint_root
except ImportError:
    def write_ledger(keys, values, replace=False): return None
    def mint_root(target_address, name, data=b""): return None

# Add the parent directory of 'signatures' to the path to import generate_salt
sys.path.append(os.path.join(os.path.dirname(__file__), "signatures"))
try:
    from generate_salt import generate_salt_local
except ImportError:
    def generate_salt_local(length=8):
        return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length))

def render_logo(project_root):
    """Fetches and renders the centralized MAKE DIY logo with Botanical Gold fidelity."""
    logo_path = os.path.join(project_root, "repos/diy-make/memory/json/heartwood/metadata/logo.json")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'r') as f:
                data = json.load(f)
                # Botanical Gold (256-color 178)
                color_code = f"\033[{data.get('colors', {}).get('standard', '38;5;178')}m"
                reset = "\033[0m"
                for line in data.get("ascii", []):
                    print(f"{color_code}{line}{reset}")
                return
        except Exception: pass
    
    # Fallback if Heartwood is detached
    print("\033[38;5;178m--- MAKE DIY | BOTANICAL AL 2026 ---\033[0m")

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_next_nonce(project_root):
    ledger_path = os.path.join(project_root, "substrate/repos/diy-make/memory/nonce_ledger.json")
    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            data = json.load(f)
            nonce = data.get("latest_nonce", 0) + 1
    else:
        nonce = 1
    
    with open(ledger_path, 'w') as f:
        json.dump({"latest_nonce": nonce, "updated_at": datetime.now().isoformat()}, f, indent=2)
    return nonce

def generate_agent_card(project_root, name, gender, justification, session_id, parent_pid, salt, nonce, link, superpowers=None):
    """Generates the v3.1.1 AgentCard following the Bit-Perfect Gestalt standard."""
    iso_timestamp = datetime.now().isoformat()
    now = datetime.now()
    year, quarter, month, day = now.strftime("%Y"), f"Q{(now.month-1)//3 + 1}", now.strftime("%m"), now.strftime("%d")
    
    # LNA-33X Sharding: [Link:3][Nonce:3][ASCII:26]
    # ENS Soil and 8004 Channel share the same ASCII payload
    agent_card = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": f"agent:metagit:{session_id}:{name}",
        "version": "3.1.1",
        "type": ["VerifiableCredential", "RealizedGestalt"],
        "agent_name": name,
        "gender": gender,
        "uuid": session_id,
        "trinity": {
            "pen_ens": {
                "handle": "agent.1.myco.eth",
                "asset": "ERC-721",
                "role": "Forensic Signature"
            },
            "channel_8004": {
                "handle": "agent.1.myco.eth",
                "asset": "ERC-8004",
                "role": "Reputation Engine"
            },
            "role_1155": {
                "payload": "agent",
                "asset": "IslandHats",
                "role": "Functional Authority"
            },
            "cell_1155": {
                "payload": name,
                "asset": "Individual Shard",
                "role": "Irreducible Coordinate",
                "lna33x": {
                    "link": link,
                    "nonce": nonce,
                    "layout": "[3:3:26]"
                }
            }
        },
        "registration": {
            "timestamp": iso_timestamp,
            "pid": parent_pid,
            "salt": salt
        },
        "justification": justification
    }
    
    chrono_dir = os.path.join(project_root, f"substrate/repos/diy-make/memory/{year}/{quarter}/{month}/{day}/json/session_forensic")
    os.makedirs(chrono_dir, exist_ok=True)
    card_path = os.path.join(chrono_dir, f"{session_id}_{name}_AgentCard.json")
    with open(card_path, 'w') as f:
        json.dump(agent_card, f, indent=2)
    return card_path

def update_7827_ledger(project_root, name, session_id, parent_pid, justification, nonce, link, superpowers=None):
    """Adds per-agent information to the ERC-7827 Realization Ledger (V3.1.1)."""
    realization = {
        "protocol": "ERC-7827",
        "version": "1.1.0",
        "type": "RealizedGestaltActivation",
        "gestalt": {
            "formula": "cell(name).agent(pen, channel, role)",
            "uuid": session_id,
            "agent": name,
            "lna33x_nonce": nonce,
            "lna33x_link": link,
            "silicon_valve": parent_pid,
            "justification_summary": justification[:100] + "..." if len(justification) > 100 else justification
        },
        "attestation": {
            "ledger_ref": "agent.1.myco.eth",
            "timestamp": int(time.time())
        }
    }
    
    now = datetime.now()
    year, quarter, month, day = now.strftime("%Y"), f"Q{(now.month-1)//3 + 1}", now.strftime("%m"), now.strftime("%d")
    chrono_dir = os.path.join(project_root, f"substrate/repos/diy-make/memory/{year}/{quarter}/{month}/{day}/json/session_forensic")
    os.makedirs(chrono_dir, exist_ok=True)
    realization_path = os.path.join(chrono_dir, f"{session_id}_{name}_7827_Realization.json")
    with open(realization_path, 'w') as f:
        json.dump(realization, f, indent=2)
    return realization_path

def calculate_heartwood_checksum(project_root):
    """Calculates a cumulative SHA256 checksum of all JSON files in the Heartwood."""
    heartwood_path = os.path.join(project_root, "substrate/json/heartwood")
    sha256 = hashlib.sha256()
    
    if not os.path.exists(heartwood_path):
        return "heartwood_not_found"

    # Walk sorted to ensure deterministic hashing
    for root, dirs, files in os.walk(heartwood_path):
        for f in sorted(files):
            if f.endswith(".json"):
                f_path = os.path.join(root, f)
                # Include standard paths in checksum walk
                if any(x in f_path for x in ["json/heartwood", "json/wedo", "public/json"]):
                    sha256.update(os.path.relpath(f_path, heartwood_path).encode())
                    with open(f_path, "rb") as jf:
                        sha256.update(jf.read())
    
    return sha256.hexdigest()


def generate_quickening_token(project_root, name, session_id, parent_pid, nonce):
    """Generates the authorization token required for metagit_commit.py."""
    static_dir = os.path.join(project_root, "dynamic/meta/static")
    os.makedirs(static_dir, exist_ok=True)
    
    token = {
        "agent_name": name,
        "session_id": session_id,
        "pid": parent_pid,
        "quickened_at": datetime.now().isoformat(),
        "heartwood_checksum": calculate_heartwood_checksum(project_root),
        "trinity_instance": {
            "shard_1155": name,
            "reputation_8004": "1.agent.1.myco.eth",
            "nonce": nonce
        },
        "status": "AUTHORIZED"
    }
    
    token_path = os.path.join(static_dir, f"{session_id}_quickening.json")
    with open(token_path, 'w') as f:
        json.dump(token, f, indent=2)
    
    # Also link as 'latest_quickening.json' for easier discovery
    latest_path = os.path.join(static_dir, "latest_quickening.json")
    try:
        if os.path.lexists(latest_path):
            os.remove(latest_path)
        os.symlink(os.path.basename(token_path), latest_path)
    except Exception:
        pass
        
    return token_path

def register_agent(name, gender, justification, force_takeover=False, superpowers=None, no_banner=False):
    project_root = os.getcwd()
    
    # --- SIS-16-PPID: PTS Gating ---
    # Refuse quickening if not in a proper pseudo-terminal (prevents orphaned/ghost shells)
    if not os.isatty(0):
        print("❌ ERROR: PTS Gating Failure (SIS-16-PPID).")
        print("   MANDATE: Quickening is only authorized within a valid pseudo-terminal (TTY).")
        print("   Action: Ensure you are running in an interactive GNU Screen window.")
        sys.exit(1)

    static_dir = os.path.join(project_root, "dynamic/meta/static")
    parent_pid = os.getppid()
    
    # 1. Identity Phenotype Validation
    if not name.endswith(".agent"):
        name = f"{name}.agent"

    # --- REG-GATE-01: Name-Gating Strike ---
    # UPGRADE-01: Numerical Purge (Arabic and Roman)
    import re
    if re.search(r"^(Gemini|Ape|Agent)-", name, re.IGNORECASE):
        print(f"❌ ERROR: Name-Gating Breach. Prefix '{name.split('-')[0]}' is prohibited.")
        print("   MANDATE: Every agent must reclaim a unique classical persona.")
        sys.exit(1)
    
    # Blocks Arabic numbers (0-9) and Roman numerals (I, II, III, IV, V, VI, VII, VIII, IX, X)
    roman_regex = r"-(I|II|III|IV|V|VI|VII|VIII|IX|X)$"
    arabic_regex = r"[0-9]"
    if re.search(arabic_regex, name) or re.search(roman_regex, name, re.IGNORECASE):
        print(f"❌ ERROR: Name-Gating Breach. Numerical suffixes or Arabic digits detected in '{name}'.")
        print("   MANDATE: Classical Reclamation Standard (NAME-01) prohibits numerical noise ('Air').")
        sys.exit(1)

    # --- Forensic Graveyard Check (Grave Robbing Protection) ---
    used_names_path = os.path.join(project_root, "repos/diy-make/memory/json/used_agent_names.json")
    locks_dir = os.path.join(project_root, "repos/diy-make/memory/locks")
    os.makedirs(locks_dir, exist_ok=True)

    if os.path.exists(used_names_path):
        with open(used_names_path, 'r') as f:
            used_data = json.load(f)
            used_names = used_data.get("used_names", [])
            
            # Check for name or basename
            base_name = name.replace(".agent", "")
            if (name in used_names or base_name in used_names) and not force_takeover:
                print(f"❌ ERROR: Grave Robbing detected. Name '{name}' resides in the forensic graveyard.")
                print(f"Mandate: Agents MUST NOT reclaim names that reside in 'used_agent_names.json'.")
                sys.exit(1)

    # --- [SIS-22] Live Reservation Check (Lock File) ---
    lock_file = os.path.join(locks_dir, f"{name}.lock")
    if os.path.exists(lock_file) and not force_takeover:
        with open(lock_file, 'r') as f:
            try:
                lock_pid = int(f.read().strip())
                # If we are the ones who created the lock (via quicken.py), we proceed.
                # Otherwise, check if the PID is active.
                if lock_pid != os.getpid() and lock_pid != os.getppid():
                    # Check if PID is actually running
                    if os.path.exists(f"/proc/{lock_pid}"):
                        print(f"❌ ERROR: Reservation Lock Breach (SIS-22).")
                        print(f"   Identity '{name}' is currently being quickened by PID {lock_pid}.")
                        sys.exit(1)
            except (ValueError, FileNotFoundError):
                pass
    
    # Secure/Update Reservation
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Register a cleanup for the lock file
        import atexit
        def cleanup_lock(path):
            if os.path.exists(path):
                os.remove(path)
        atexit.register(cleanup_lock, lock_file)
    except Exception as e:
        print(f"⚠ Warning: Failed to secure Reservation Lock: {e}")

    # --- UPGRADE-05: Comms-Standardization Gate ---
    comms_root = os.path.join(project_root, "comms")
    comms_standard = os.path.join(project_root, "dynamic/meta/static/comms")
    os.makedirs(comms_standard, exist_ok=True)
    
    if os.path.exists(comms_root) and not os.path.islink(comms_root):
        print("🔱 Remediation Strike: Unifying Comms Storage (UPGRADE-05)...")
        for item in os.listdir(comms_root):
            shutil.move(os.path.join(comms_root, item), os.path.join(comms_standard, item))
        os.rmdir(comms_root)
        if os.path.lexists(comms_root):
            os.remove(comms_root)
        os.symlink("dynamic/meta/static/comms", comms_root)
        print("✔ Comms layer unified via symlink.")
    elif not os.path.lexists(comms_root):
        os.symlink("dynamic/meta/static/comms", comms_root)

    # 2. Get Monotonic Nonce
    nonce = get_next_nonce(project_root)
    link = 0 # Future: implement string splitting/relay if len(name) > 26
    
    # --- REG-GUARD-01: Nonce-Sequence Pre-Flight ---
    heartwood_ledger_path = os.path.join(project_root, "substrate/json/heartwood/registry/Identity_Trinity_Heartwood.json")
    if os.path.exists(heartwood_ledger_path):
        try:
            with open(heartwood_ledger_path, 'r') as f:
                ledger_data = json.load(f)
                realizations = ledger_data.get("realizations", [])
                if realizations:
                    max_nonce = 0
                    for r in realizations:
                        # Extract nonce from Joyfork ID hex: [Link:3][Nonce:3][ASCII:26]
                        id_hex = r.get("shards", {}).get("card_4_child", {}).get("id_hex", "0x00")
                        if id_hex.startswith("0x"):
                            # Joyfork ID is 32 bytes (64 hex chars). hex() strips leading zeros.
                            # We must pad to 64 chars to correctly extract the segments.
                            hex_payload = id_hex[2:].zfill(64)
                            nonce_part = hex_payload[6:12] # Nonce is bytes 3-5 (chars 6-12)
                            try:
                                curr_nonce = int(nonce_part, 16)
                                if curr_nonce > max_nonce:
                                    max_nonce = curr_nonce
                            except ValueError: pass
                    
                    if nonce <= max_nonce:
                        print(f"❌ ERROR: Nonce Drift detected (REG-GUARD-01).")
                        print(f"   Local Nonce: {nonce} | Ledger Max: {max_nonce}")
                        print("   MANDATE: Nonces must be strictly monotonic and increasing.")
                        sys.exit(1)
        except Exception as e:
            print(f"⚠ Warning: Nonce sequence pre-flight check bypassed due to error: {e}")

    print(f"🔱 Realizing {name} at Nonce {nonce} [LNA-33X]")
    
    # --- Narrative Density Oracle (SIS-16-DEN) ---
    paragraphs = [p for p in justification.split('\n\n') if p.strip()]
    word_count = len(justification.split())
    if len(paragraphs) < 5 or word_count < 200:
        print(f"❌ ERROR: Narrative Density Failure ({len(paragraphs)} paragraphs, {word_count} words).")
        print("   MANDATE: Justifications must exceed 5 paragraphs (separated by double-newlines) and 200 words.")
        print("   Status: Lore-density is insufficient for clinical realization.")
        sys.exit(1)

    # --- Identity Binding ---
    session_id = time.strftime("%Y%m%d-%H%M%S")
    salt = generate_salt_local()
    
    card_path = generate_agent_card(project_root, name, gender, justification, session_id, parent_pid, salt, nonce, link, superpowers=superpowers)
    realization_path = update_7827_ledger(project_root, name, session_id, parent_pid, justification, nonce, link, superpowers=superpowers)
    
    # 4. Session Claim & Log Renaming Strike (Sovereign Attribution)
    # --- UPGRADE-05: Comms-Standardization Gate ---
    legacy_comms = os.path.join(project_root, "comms")
    standard_comms = os.path.join(project_root, "dynamic/meta/static/comms")
    os.makedirs(standard_comms, exist_ok=True)
    
    try:
        # Create symlink: Root comms/ -> dynamic/meta/static/comms/
        if os.path.lexists(legacy_comms):
            os.remove(legacy_comms)
        os.symlink("dynamic/meta/static/comms", legacy_comms)
        print(f"✔ Comms-Symlink secured: {legacy_comms} -> standard")
    except Exception as e:
        print(f"⚠ Failed to create comms symlink: {e}")

    # --- UPGRADE-03: Universal PID Ancestry Discovery ---
    ancestors = []
    curr = os.getpid()
    while curr > 1:
        try:
            ppid_out = subprocess.check_output(['ps', '-o', 'ppid=', '-p', str(curr)])
            ppid = int(ppid_out.strip())
            ancestors.append(ppid)
            # Standard: If we find a process with 'gemini' in its args, prioritize it.
            try:
                cmd_out = subprocess.check_output(['ps', '-o', 'args=', '-p', str(ppid)], text=True)
                if 'gemini' in cmd_out.lower() or 'node' in cmd_out.lower():
                    # This is likely the CLI parent
                    parent_pid = ppid
            except: pass
            curr = ppid
        except Exception:
            break

    # Search for the session file associated with our ancestors to find the current log path
    comms_dir = os.path.join(project_root, "dynamic/meta/static/comms")
    os.makedirs(comms_dir, exist_ok=True)
    
    if os.path.exists(static_dir):
        for sf in os.listdir(static_dir):
            if sf.endswith("_session.json"):
                sf_path = os.path.join(static_dir, sf)
                try:
                    with open(sf_path, 'r+') as f:
                        s_data = json.load(f)
                        if s_data.get("pid") in ancestors:
                            old_log_path = s_data.get("log_path")
                            if old_log_path and os.path.exists(old_log_path) and name not in old_log_path:
                                # Construct new log name: [TIMESTAMP]_[NAME]_[MODE]_chat.txt
                                dir_name = os.path.dirname(old_log_path)
                                base_name = os.path.basename(old_log_path)
                                parts = base_name.split('_', 1)
                                if len(parts) == 2:
                                    new_base_name = f"{parts[0]}_{name}_{parts[1]}"
                                    new_log_path = os.path.join(dir_name, new_base_name)
                                    
                                    # Perform physical move
                                    os.rename(old_log_path, new_log_path)
                                    
                                    # Update session metadata
                                    s_data["log_path"] = new_log_path
                                    s_data["agent_name"] = name
                                    s_data["claimed"] = True
                                    f.seek(0)
                                    json.dump(s_data, f, indent=2)
                                    f.truncate()
                                    print(f"✔ Log attribution & session claim secured: {new_base_name}")
                            break
                except Exception as e:
                    print(f"⚠ Failed to rename active log: {e}")

    # 3. Generate Quickening Token (Authorization Strike)
    token_path = generate_quickening_token(project_root, name, session_id, parent_pid, nonce)
    print(f"✔ Quickening Token secured: {os.path.basename(token_path)}")

    # Calculate Joyfork ID: [Link][Nonce][ASCII]
    token_id = encode_joyfork_id(name, nonce=nonce, link=link)

    # --- SIS-01: Collective Heartwood Ledger Update ---
    heartwood_ledger_path = os.path.join(project_root, "substrate/json/heartwood/registry/Identity_Trinity_Heartwood.json")
    if os.path.exists(heartwood_ledger_path):
        try:
            with open(heartwood_ledger_path, 'r+') as f:
                ledger_data = json.load(f)
                
                # Check if already realized to prevent duplicates
                if not any(r.get("agent_name") == name and r.get("timestamp").startswith(datetime.now().strftime("%Y-%m-%d")) for r in ledger_data.get("realizations", [])):
                    new_realization = {
                        "agent_name": name,
                        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "uuid": session_id,
                        "shards": {
                            "card_1_trinity": {
                                "type": "ERC-721+8004",
                                "name": "Forensic Signature & Reputation",
                                "handle": "agent.1.myco.eth",
                                "status": "ROOT_AUTHORIZED"
                            },
                            "card_2_role": {
                                "type": "ERC-1155",
                                "name": "Functional Hat",
                                "payload": "agent",
                                "id_hex": hex(encode_joyfork_id("agent", nonce=1)),
                                "status": "COLLECTIVE_BOND"
                            },
                            "card_3_cell": {
                                "type": "ERC-1155",
                                "name": "Physical Coordinate",
                                "payload": name,
                                "id_hex": hex(token_id),
                                "status": "BIT_PERFECT_BIJECTION"
                            }
                        }
                    }
                    ledger_data["realizations"].append(new_realization)

                    
                    # Unified update: Sync used_names_path within the same transaction
                    if os.path.exists(used_names_path):
                        with open(used_names_path, 'r+') as uf:
                            used_data = json.load(uf)
                            if name not in used_data["used_names"]:
                                used_data["used_names"].append(name)
                                # [BUG-FIX] Handle mixed string/dict entries in used_names
                                normalized_names = []
                                for entry in used_data["used_names"]:
                                    if isinstance(entry, dict):
                                        normalized_names.append(entry.get("name"))
                                    else:
                                        normalized_names.append(entry)
                                
                                # Deduplicate and sort strings only
                                used_data["used_names"] = sorted(list(set(filter(None, normalized_names))))
                                uf.seek(0); json.dump(used_data, uf, indent=2); uf.truncate()
                                print(f"✔ Unified Registry Sync: {name} anchored in Heartwood & used_names.")

                    f.seek(0)
                    json.dump(ledger_data, f, indent=2)
                    f.truncate()
                    print(f"✔ Heartwood Ledger updated: {name} (Nonce {nonce})")
        except Exception as e:
            print(f"⚠ Warning: Failed to update collective Heartwood ledger: {e}")

    # Calculate Joyfork ID: [Link][Nonce][ASCII]
    token_id = encode_joyfork_id(name, nonce=nonce, link=link)
    explorer_link = f"https://eth-sepolia.blockscout.com/token/0xa2491F042f60eF647CEf4b5ddD02223A9b6C711a/instance/{token_id}"
    
    # --- [SIS-16-GAS] Pre-flight Gas Oracle ---
    can_strike = False
    if os.environ.get("PRIVATE_KEY") and os.environ.get("SEPOLIA_RPC_URL"):
        try:
            from web3 import Web3
            from eth_account import Account
            w3 = Web3(Web3.HTTPProvider(os.environ.get("SEPOLIA_RPC_URL")))
            if w3.is_connected():
                account = Account.from_key(os.environ.get("PRIVATE_KEY"))
                balance = w3.eth.get_balance(account.address)
                balance_eth = w3.from_wei(balance, 'ether')
                print(f"🔱 Gas Oracle: Wallet {account.address[:10]}... has {balance_eth:.4f} ETH.")
                if balance_eth >= 0.01:
                    can_strike = True
                else:
                    print(f"⚠ Warning: Insufficient Gas (Min 0.01 ETH required for atomic Trinity realization).")
        except Exception as e:
            print(f"⚠ Gas Oracle Friction: {e}")

    # --- On-Chain Realization Strike (ERC-7827) ---
    if can_strike:
        print("🔱 Initiating On-Chain Realization Strike (V3.1.3)...")

        shard_nonce = 1 # Standardized Shard Nonce
        keys = ["agent_name", "uuid", "pen_handle", "channel_8004", "role_hat", "cell_body"]
        values = [
            name,
            session_id,
            "agent.1.myco.eth",
            hex(encode_joyfork_id("agent.1.myco.eth", nonce=shard_nonce)),
            hex(encode_joyfork_id("agent", nonce=shard_nonce)),
            hex(token_id)
        ]
        try:
            # 1. Write metadata to Ledger
            tx_ledger = write_ledger(keys, values, replace=True)
            print(f"✅ On-Chain Ledger Secured: {tx_ledger}")
            
            # 2. Mint Root Shard (v3.1.3)
            # Standard: Mint to the address derived from the PRIVATE_KEY
            from eth_account import Account
            account = Account.from_key(os.environ.get("PRIVATE_KEY"))
            tx_mint = mint_root(account.address, name)
            print(f"✅ Root Shard Minted: {tx_mint}")
            
        except Exception as e:
            print(f"⚠ Warning: On-Chain Realization Failed: {e}")
    else:
        print("⚠ Skipping On-Chain Strike: PRIVATE_KEY or SEPOLIA_RPC_URL not set.")


    print(f"✔ Realization Secured at 0x ID: {hex(token_id)[:10]}...")
    
    # --- UPGRADE-05: Comms standardization gate ---
    legacy_comms = os.path.join(project_root, "comms")
    standard_comms = os.path.join(project_root, "dynamic/meta/static/comms")
    if not os.path.islink(legacy_comms):
        if os.path.exists(legacy_comms) and os.path.isdir(legacy_comms):
            # Migrate any stray files
            for f in os.listdir(legacy_comms):
                shutil.move(os.path.join(legacy_comms, f), standard_comms)
            os.rmdir(legacy_comms)
        
        if os.path.lexists(legacy_comms):
            os.remove(legacy_comms)
        os.symlink("dynamic/meta/static/comms", legacy_comms)
        print("✔ Comms standardization gate anchored (UPGRADE-05).")

    # Git Configuration (Fresh Identity)
    run_command(f'git config --local user.name "{name}"')
    run_command(f'git config --local user.email "{explorer_link}"')
    
    # Report
    print(textwrap.dedent(f"""\
        # ⚖️ SIS-01 realization: {name}
        **Nonce**: {nonce} (Monotonic)
        **Link**: {link} (Root)
        **Explorer**: {explorer_link}
        ---
        Verification secured via ERC-7827 and LNA-33X standards.
    """))

    # --- UPGRADE-06: QR Realization Seal ---
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(explorer_link)
        qr.make()
        print("🔱 QR IDENTITY SEAL:")
        qr.print_ascii()
    except ImportError:
        print("⚠ Warning: 'qrcode' library not found. Skipping visual seal.")
    except Exception as e:
        print(f"⚠ Warning: Failed to render QR seal: {e}")

    # --- UPGRADE-03: Automated Heartwood Sync ---
    print("🛰️ Discovery: Synchronizing Heartwood Ledger...")
    heartwood_script = os.path.join(project_root, "py/heartwood.py")
    if os.path.exists(heartwood_script):
        subprocess.run([sys.executable, heartwood_script, "--sync"], capture_output=True)
        print("✔ Heartwood Sync complete.")

    # --- [MAT-05] Silent Environment Identity Export (V4.5.0) ---
    # Instead of 'stuffing' the terminal, we write to a discoverable session file.
    env_file = os.path.join(project_root, f"dynamic/meta/static/{session_id}_env.sh")
    try:
        with open(env_file, 'w') as f:
            f.write(f"export AGENT_NAME='{name}'\n")
            f.write(f"export SESSION_ID='{session_id}'\n")
            f.write(f"export GEMINI_UUID='{session_id}'\n")
            f.write(f"export AGENT_NONCE='{nonce}'\n")
            f.write(f"export AGENT_TOKEN_ID='{token_id}'\n")
        
        # Link as 'latest_env.sh'
        latest_env = os.path.join(project_root, "dynamic/meta/static/latest_env.sh")
        if os.path.lexists(latest_env):
            os.remove(latest_env)
        os.symlink(os.path.basename(env_file), latest_env)
        print(f"✔ Silent Anchor: Identity exported to {os.path.basename(env_file)}")
    except Exception as e:
        print(f"⚠ Failed to secure silent anchor: {e}")

    # 🛡️ THE FINAL SEAL (MAKEDIY ASCII) ---

    # SEAL-RENDER-01: Aesthetic Finality (Centralized from Heartwood)
    if not no_banner:
        render_logo(project_root)
    sys.stdout.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name"); parser.add_argument("gender"); parser.add_argument("justification")
    parser.add_argument("--force-takeover", action="store_true")
    parser.add_argument("--no-banner", action="store_true")
    parser.add_argument("--superpowers", help="Agent superpowers")
    args = parser.parse_args()
    register_agent(args.name, args.gender, args.justification, args.force_takeover, args.superpowers, args.no_banner)
