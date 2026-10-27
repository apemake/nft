import os
import json
import sys
import time
import requests
from web3 import Web3
from eth_account import Account
from load_secrets import load_secrets
load_secrets()

# 🟢 Sepolia Bridge for ERC-7827 Ledger Realization (V4.4.7)
# Mandate: Settle agentic agency in the bit-perfect 28-byte Hub.

RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
HUB_ADDR = "0xEAEAfce97Dca540f0D14a50B7E1Dd9EAa09f71Cd"

def get_w3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise Exception("❌ Failed to connect to Sepolia RPC.")
    return w3

def wait_for_portal(token_id, timeout=600):
    url = f"https://eth-sepolia.blockscout.com/api/v2/tokens/{HUB_ADDR}/instances/{token_id}"
    print(f"⌛ Clinical Polling: Waiting for portal to open at {token_id}...")
    start_time = time.time()
    attempt = 1
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, headers={'User-Agent': 'Metagit-Forensic/4.4.7'}, timeout=10)
            if resp.status_code == 200:
                print(f"✅ PORTAL OPEN: Token is live. (Attempt {attempt})")
                return True
            print(f"  ... still 404 (Attempt {attempt}, {int(time.time() - start_time)}s)")
        except Exception as e:
            print(f"  ... polling error: {e}")
        attempt += 1
        time.sleep(20)
    print(f"❌ TIMEOUT: Portal remained closed after {timeout}s.")
    return False

def mint_shard(target_address, token_id, data=b"", nonce=None):
    if not PRIVATE_KEY: raise Exception("❌ PRIVATE_KEY missing.")
    w3 = get_w3()
    account = Account.from_key(PRIVATE_KEY)
    abi = [{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"mintShard","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    contract = w3.eth.contract(address=w3.to_checksum_address(HUB_ADDR), abi=abi)
    print(f"🔱 Minting Shard: {hex(token_id)}")
    
    if nonce is None:
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
    
    # Aggressive EIP-1559 Pricing
    priority_fee = w3.to_wei(5, 'gwei')
    base_fee = w3.eth.get_block('latest')['baseFeePerGas']
    
    tx = contract.functions.mintShard(w3.to_checksum_address(target_address), token_id, data).build_transaction({
        'chainId': 11155111,
        'nonce': nonce,
        'maxFeePerGas': base_fee + priority_fee,
        'maxPriorityFeePerGas': priority_fee,
        'gas': 500000
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✔ Sent: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    if receipt.status != 1: raise Exception(f"❌ Reverted: {tx_hash.hex()}")
    return wait_for_portal(token_id)

def write_shard_ledger(token_id, keys, values, replace=False, nonce=None):
    if not PRIVATE_KEY: raise Exception("❌ PRIVATE_KEY missing.")
    w3 = get_w3()
    account = Account.from_key(PRIVATE_KEY)
    abi = [{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"string[]","name":"keys","type":"string[]"},{"internalType":"string[]","name":"values","type":"string[]"},{"internalType":"bool","name":"replace","type":"bool"}],"name":"write","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    contract = w3.eth.contract(address=w3.to_checksum_address(HUB_ADDR), abi=abi)
    print(f"🔱 Writing Ledger: {hex(token_id)}")
    
    # EIP-1559 Dynamic Nonce
    nonce = w3.eth.get_transaction_count(account.address, 'latest')

    tx = contract.functions.write(token_id, keys, values, replace).build_transaction({
        'chainId': 11155111,
        'nonce': nonce,
        'maxFeePerGas': w3.eth.get_block('latest')['baseFeePerGas'] * 2 + w3.to_wei(10, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(10, 'gwei'),
        'gas': 1500000 # Massive gas limit for heavy Hub logic
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✔ Sent: {tx_hash.hex()}")
    
    # Wait for transaction confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    if receipt.status != 1:
        print(f"❌ Ledger Write Reverted: {tx_hash.hex()}")
        return False
        
    # Definitive Portal Verification
    return wait_for_portal(token_id)
