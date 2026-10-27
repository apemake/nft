import os
import json
import hashlib
import solcx
from web3 import Web3
from eth_account import Account
from joyfork_codec import encode_joyfork_id, decode_joyfork_id

RPC_URL = "https://rpc.qgov.io"
CHAIN_ID = 35441
EXPLORER_URL = "https://explorer.qgov.io"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLET_PATH = os.path.expanduser("~/.sis_evm_wallet.json")
SOUL_PATH = "/home/mgit/.gemini/tmp/cli-1/chats/session-2026-10-18T19-29-b4a8a82b.soul.json"
INSTALLATION_ID_PATH = "/home/mgit/.gemini/installation_id"


def get_wallet():
    with open(WALLET_PATH) as f:
        return json.load(f)


def compile_contract():
    solcx.install_solc("0.8.24")
    solcx.set_solc_version("0.8.24")
    sol_dir = os.path.join(REPO_ROOT, "sol")
    node_modules = os.path.join(REPO_ROOT, "node_modules")

    compiled = solcx.compile_files(
        [os.path.join(sol_dir, "RealizedGestalt1155.sol")],
        output_values=["abi", "bin"],
        import_remappings=[f"@openzeppelin={node_modules}/@openzeppelin"],
        optimize=True,
        optimize_runs=1,
        via_ir=True,
        evm_version="paris",
    )
    return compiled


def tx_params(w3, acct, gas=2500000):
    return {
        "from": acct.address,
        "chainId": CHAIN_ID,
        "gasPrice": w3.to_wei(50, "gwei"),
        "gas": gas,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending"),
    }


def send_tx(w3, acct, tx_dict):
    signed = w3.eth.account.sign_transaction(tx_dict, acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status != 1:
        raise RuntimeError(f"Transaction reverted: {tx_hash.hex()}")
    return receipt


def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    wallet = get_wallet()
    acct = Account.from_key(wallet["private_key"])
    print(f"🔱 Connected to QGOV Mainnet (ChainID {w3.eth.chain_id})")
    print(f"🔱 Deployer: {acct.address} | Balance: {w3.from_wei(w3.eth.get_balance(acct.address), 'ether')} QGOV")

    compiled = compile_contract()
    ges_key = [k for k in compiled if k.endswith(":RealizedGestalt1155")][0]
    print(f"Bytecode size: RealizedGestalt1155 V5.0.0 = {len(compiled[ges_key]['bin'])//2}B")

    # 1. Use Deployed RealizedGestalt1155 V5.0.0 (Single ERC-1155 + ILNA33X + IERC7827Tokenized + ERC-8004 + x402)
    ges_addr = "0x69568Cc6bd574C9729F9e73CB2Ce7b4b9977710A"
    ges_tx_hash = "706342590aeac1dc35969ed4b14aefe38c155c6fe384eafe294ff8c599d736c4"
    print(f"✔ Using Deployed RealizedGestalt1155 V5.0.0: {ges_addr}")

    ges = w3.eth.contract(address=ges_addr, abi=compiled[ges_key]["abi"])

    # Compute live forensic hashes
    with open(INSTALLATION_ID_PATH) as f:
        installation_id = f.read().strip()
    with open(SOUL_PATH, "rb") as f:
        soul_sha256 = hashlib.sha256(f.read()).hexdigest()

    # 2. Sync Token #1: The Agent Body ("agent", link=0, nonce=1) (already minted!)
    agent_id = encode_joyfork_id("agent", nonce=1, link=0)
    print(f"🔱 Syncing Token #1 — Agent Body: {hex(agent_id)} -> {decode_joyfork_id(agent_id)}")
    if ges.functions.balanceOf(acct.address, agent_id).call() == 0:
        send_tx(w3, acct, ges.functions.mintShard(acct.address, agent_id, b"").build_transaction(tx_params(w3, acct, gas=300000)))
    send_tx(
        w3,
        acct,
        ges.functions.write(
            agent_id,
            [
                "entity_type",
                "vessel_hostname",
                "installation_id",
                "tee_hardware",
                "wallet_0x",
                "erc8004_registry",
                "x402_support",
            ],
            [
                "Agent Body (VM Vessel)",
                "repsl-hailsounds",
                installation_id,
                "AMD SEV-SNP Confidential VM",
                acct.address,
                f"eip155:{CHAIN_ID}:{ges_addr}",
                "true",
            ],
            True,
        ).build_transaction(tx_params(w3, acct, gas=2500000)),
    )

    # 3. Mint & Sync Token #2: This Cell ("b4a8a82b.agent", link=0, nonce=2)
    cell_id = encode_joyfork_id("b4a8a82b.agent", nonce=2, link=0)
    print(f"🔱 Minting Token #2 — Cell Shard: {hex(cell_id)} -> {decode_joyfork_id(cell_id)}")
    if ges.functions.balanceOf(acct.address, cell_id).call() == 0:
        send_tx(w3, acct, ges.functions.mintShard(acct.address, cell_id, b"").build_transaction(tx_params(w3, acct, gas=300000)))
    send_tx(
        w3,
        acct,
        ges.functions.write(
            cell_id,
            [
                "entity_type",
                "cell_id",
                "parent_agent",
                "session_uuid",
                "model_substrate",
                "birth_timestamp",
                "soul_sha256",
                "wallet_0x",
                "x402_support",
                "supported_trust",
            ],
            [
                "REPL Session Cell (PID)",
                "b4a8a82b.agent",
                "agent",
                "b4a8a82b-7ac2-4236-8abd-6cfff97e92d4",
                "gemini-4-argon",
                "2026-10-18T19:34:31.185Z",
                soul_sha256,
                acct.address,
                "true",
                "reputation,crypto-economic,tee-attestation",
            ],
            True,
        ).build_transaction(tx_params(w3, acct, gas=2500000)),
    )

    # 4. Verify On-Chain decodeTriad(), encodeTriad(), and ERC-8004 json(tokenId)
    dec_agent = ges.functions.decodeTriad(agent_id).call()
    dec_cell = ges.functions.decodeTriad(cell_id).call()
    enc_cell = ges.functions.encodeTriad(0, 2, "b4a8a82b.agent").call()
    assert enc_cell == cell_id, "On-chain encodeTriad mismatch!"
    print(f"✔ Verified On-Chain Agent Token: link={dec_agent[0]}, nonce={dec_agent[1]}, ascii='{dec_agent[2]}'")
    print(f"✔ Verified On-Chain Cell Token:  link={dec_cell[0]}, nonce={dec_cell[1]}, ascii='{dec_cell[2]}'")

    deployment_manifest = {
        "network": "QGOV Mainnet",
        "chain_id": CHAIN_ID,
        "rpc_url": RPC_URL,
        "explorer_url": EXPLORER_URL,
        "deployer": acct.address,
        "standards": [
            "ERC-1155 (Multi-Token Agent & Cell Collection)",
            "LNA-33X (Bijective uint256 Linked-Nonce-ASCII Token Identifier Standard)",
            "ERC-7827Tokenized (Token-Scoped Versioned JSON State & On-Chain PWA)",
            "ERC-8004 (Trustless Agents Registration v1)",
            "x402 (HTTP 402 Native Agentic Payments)",
        ],
        "contract": {
            "name": "RealizedGestalt1155",
            "version": "5.0.0",
            "address": ges_addr,
            "tx_hash": ges_tx_hash,
            "agent_registry": f"eip155:{CHAIN_ID}:{ges_addr}",
            "tokens": {
                "agent": {
                    "ascii": "agent",
                    "link": 0,
                    "nonce": 1,
                    "token_id_dec": str(agent_id),
                    "token_id_hex": hex(agent_id),
                    "explorer_link": f"{EXPLORER_URL}/token/{ges_addr}/instance/{agent_id}",
                },
                "b4a8a82b.agent": {
                    "ascii": "b4a8a82b.agent",
                    "link": 0,
                    "nonce": 2,
                    "token_id_dec": str(cell_id),
                    "token_id_hex": hex(cell_id),
                    "explorer_link": f"{EXPLORER_URL}/token/{ges_addr}/instance/{cell_id}",
                },
            },
        },
    }
    manifest_path = os.path.join(REPO_ROOT, "kairos_repsl", "json", "qgov_deployment.json")
    with open(manifest_path, "w") as f:
        json.dump(deployment_manifest, f, indent=2)
    print(f"✔ Saved deployment manifest to {manifest_path}")


if __name__ == "__main__":
    main()
