import os
import json
import hashlib
import solcx
from web3 import Web3
from eth_account import Account

RPC_URL = "https://rpc.qgov.io"
CHAIN_ID = 35441
EXPLORER_URL = "https://explorer.qgov.io"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLET_PATH = os.path.expanduser("~/.sis_evm_wallet.json")
SOUL_PATH = "/home/mgit/.gemini/tmp/cli-1/chats/session-2026-10-18T19-29-b4a8a82b.soul.json"
INSTALLATION_ID_PATH = "/home/mgit/.gemini/installation_id"

PROTO_INFT_PWA_JS = """(new function app($0){
$0.b=document.body;$0.CA=$0.b.dataset.ca;$0.tid=$0.b.dataset.tid;$0.path=$0.b.dataset.path;$0.RPC="https://rpc.qgov.io";$0.side=1;$0.cSide=1;
$0.css="*{box-sizing:border-box}body{background:#0b0e14;color:#e6edf3;font-family:monospace;margin:0;padding:12px;line-height:1.4}.bar{display:flex;justify-content:space-between;align-items:center;background:#111622;border:1px solid #30363d;border-radius:8px;padding:8px 12px;margin-bottom:10px}.box{background:#111622;border:1px solid #30363d;border-radius:8px;padding:12px;margin-bottom:10px}button{background:#1f2937;color:#ECCA90;border:1px solid #ECCA90;border-radius:6px;padding:5px 10px;font-family:monospace;font-size:12px;cursor:pointer;font-weight:bold}.hex{word-break:break-all;font-size:12px;background:#050505;padding:8px;border-radius:6px;border:1px solid #1f2937}.c-lnk{color:#00e5ff;font-weight:bold}.c-non{color:#d500f9;font-weight:bold}.c-asc{color:#00e676;font-weight:bold}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(50px,1fr));gap:5px;margin-top:8px}.cell{background:#050505;border:1px solid #1f2937;border-radius:4px;padding:4px;text-align:center;font-size:11px}.cell.on{border-color:#00e676}.hx{color:#8b949e;font-size:10px}.ch{color:#00e676;font-size:13px;font-weight:bold}input{background:#050505;color:#e6edf3;border:1px solid #30363d;padding:6px;font-family:monospace;font-size:12px;border-radius:4px;width:100%;margin-top:4px}.sec{color:#00e5ff;font-size:11px;margin:8px 0 4px;font-weight:bold}.kv{padding:4px 0;border-bottom:1px solid #1f2937;font-size:12px}.k{color:#ECCA90;font-weight:bold}.hide{display:none}";
document.head.insertAdjacentHTML("beforeend","<style>"+$0.css+"</style>");
document.getElementById("app").innerHTML='<div class="bar"><div><b style="color:#ECCA90">&#9878; '+$0.path+'</b> <span id="sideLbl" style="color:#00e5ff;font-size:11px">[Side 1/3: LNA-33X Tile]</span></div><button id="pFlip">flip side &rarr;</button></div><div id="s1" class="box"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b style="color:#00e5ff">Side 1: LNA-33X 32-Byte Hex &rarr; SeedTree Path</b><button id="cFlip">child flip (reprint)</button></div><div id="cFront"><div class="hex" id="hexBar"></div><div style="font-size:11px;margin-top:6px"><span class="c-lnk">&#9632; Link: <span id="dLnk"></span></span> | <span class="c-non">&#9632; Nonce: <span id="dNon"></span></span> | <span class="c-asc">&#9632; ASCII: "<span id="dAsc"></span>"</span> | <b style="color:#ECCA90">Path: '+$0.path+'</b></div><div class="grid" id="byteGrid"></div></div><div id="cBack" class="hide"><div style="font-size:12px;color:#ECCA90;margin-bottom:6px">Child Backside &mdash; Modify &amp; Reprint Front Tile:</div><input id="inHex" value="'+$0.tid+'"><div style="display:flex;gap:6px;margin-top:6px"><input id="inLnk" type="number" placeholder="Link" style="width:25%"><input id="inNon" type="number" placeholder="Nonce" style="width:25%"><input id="inAsc" maxlength="26" placeholder="ASCII (no dot)" style="width:50%"></div><button id="reprintBtn" style="margin-top:8px;width:100%">reprint front-side</button></div></div><div id="s2" class="box hide"><b style="color:#00e5ff">Side 2: ERC-7827 Versioned Vault (&lt;name&gt; + &lt;name&gt;.$0 + &lt;name&gt;.$n)</b><div id="kvBox">'+document.getElementById("vaultData").innerHTML+'</div></div><div id="s3" class="box hide"><b style="color:#00e5ff">Side 3: Self-Referencing Smart Contract Oracle ('+$0.CA+')</b><div id="treeBox" style="margin-top:8px;font-size:12px">Querying QGOV RPC...</div></div>';
$0.renderHex=($1)=>{
$0.s=$1.replace(/^0x/i,"").padStart(64,"0").slice(0,64);
$0.lH=$0.s.slice(0,6);$0.nH=$0.s.slice(6,12);$0.aH=$0.s.slice(12,64);
document.getElementById("hexBar").innerHTML='0x<span class="c-lnk">'+$0.lH+'</span><span class="c-non">'+$0.nH+'</span><span class="c-asc">'+$0.aH+'</span>';
$0.asc="";$0.grid="";
for($0.i=0;$0.i<26;$0.i++){
$0.bH=$0.aH.slice($0.i*2,$0.i*2+2);$0.cd=parseInt($0.bH,16);
$0.ch=$0.cd>=32&&$0.cd<=126?String.fromCharCode($0.cd):"&middot;";
if($0.cd>0)$0.asc+=String.fromCharCode($0.cd);
$0.grid+='<div class="cell '+($0.cd>0?"on":"")+'"><div class="hx">0x'+$0.bH+'</div><div class="ch">'+$0.ch+'</div><div class="hx">'+$0.cd+'</div></div>';
}
document.getElementById("dLnk").textContent=parseInt($0.lH,16)+" (0x"+$0.lH+")";
document.getElementById("dNon").textContent=parseInt($0.nH,16)+" (0x"+$0.nH+")";
document.getElementById("dAsc").textContent=$0.asc;
document.getElementById("inLnk").value=parseInt($0.lH,16);
document.getElementById("inNon").value=parseInt($0.nH,16);
document.getElementById("inAsc").value=$0.asc;
document.getElementById("byteGrid").innerHTML=$0.grid;
};
document.getElementById("pFlip").onclick=()=>{
$0.side=$0.side===3?1:$0.side+1;
document.getElementById("s1").className=$0.side===1?"box":"box hide";
document.getElementById("s2").className=$0.side===2?"box":"box hide";
document.getElementById("s3").className=$0.side===3?"box":"box hide";
document.getElementById("sideLbl").textContent="[Side "+$0.side+"/3]";
};
document.getElementById("cFlip").onclick=()=>{
$0.cSide=$0.cSide===1?2:1;
document.getElementById("cFront").className=$0.cSide===1?"":"hide";
document.getElementById("cBack").className=$0.cSide===2?"":"hide";
};
document.getElementById("reprintBtn").onclick=()=>{
$0.l=(parseInt(document.getElementById("inLnk").value||0)&0xffffff).toString(16).padStart(6,"0");
$0.n=(parseInt(document.getElementById("inNon").value||0)&0xffffff).toString(16).padStart(6,"0");
$0.v=document.getElementById("inAsc").value.replace(/\\./g,"");
$0.a="";for($0.i=0;$0.i<26;$0.i++){$0.a+=($0.i<$0.v.length?$0.v.charCodeAt($0.i):0).toString(16).padStart(2,"0");}
document.getElementById("inHex").value="0x"+$0.l+$0.n+$0.a;
$0.renderHex(document.getElementById("inHex").value);
document.getElementById("cFlip").click();
};
$0.call=($1)=>fetch($0.RPC,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({jsonrpc:"2.0",id:1,method:"eth_call",params:[{to:$0.CA,data:$1},"latest"]})}).then(($2)=>$2.json());
$0.loadTree=()=>{
$0.call("0xb18185f6").then(($1)=>{
$0.tot=parseInt($1.result||"0x0",16);$0.out="<div>Total Minted Shards on Contract: <b>"+$0.tot+"</b></div>";$0.nodes={};
$0.step=($2)=>{if($2>$0.tot){document.getElementById("treeBox").innerHTML=$0.out;return;}
$0.call("0x8e4e7a35"+$2.toString(16).padStart(64,"0")).then(($3)=>{
$0.tid=($3.result||"").replace(/^0x/,"").padStart(64,"0");
$0.lk=parseInt($0.tid.slice(0,6),16);$0.nc=parseInt($0.tid.slice(6,12),16);$0.as="";
for($0.i=0;$0.i<26;$0.i++){$0.c=parseInt($0.tid.slice(12+$0.i*2,14+$0.i*2),16);if($0.c>0)$0.as+=String.fromCharCode($0.c);}
$0.nodes[$0.nc]=$0.lk>0&&$0.nodes[$0.lk]?$0.nodes[$0.lk]+"."+$0.as:$0.as;
$0.out+='<div class="kv"><span class="c-non">Nonce '+$0.nc+'</span> (Link '+$0.lk+') &rarr; <b class="c-asc">'+$0.nodes[$0.nc]+'</b> <span style="color:#8b949e;font-size:10px">0x'+$0.tid.slice(0,24)+'...</span></div>';
$0.step($2+1);});};$0.step(1);});};
$0.renderHex($0.tid);$0.loadTree();
}({b:null,CA:null,tid:null,path:null,RPC:null,side:null,cSide:null,css:null,renderHex:null,s:null,lH:null,nH:null,aH:null,asc:null,grid:null,i:null,bH:null,cd:null,ch:null,l:null,n:null,v:null,a:null,call:null,loadTree:null,tot:null,out:null,nodes:null,step:null,lk:null,nc:null,as:null,c:null}));"""


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
    print(f"Bytecode size: RealizedGestalt1155 V6.2.0 = {len(compiled[ges_key]['bin'])//2}B (under 24576B EIP-170 limit!)")

    # 1. Deploy RealizedGestalt1155 V6.2.0
    GesContract = w3.eth.contract(abi=compiled[ges_key]["abi"], bytecode=compiled[ges_key]["bin"])
    ges_tx = GesContract.constructor().build_transaction(tx_params(w3, acct, gas=6000000))
    ges_rcpt = send_tx(w3, acct, ges_tx)
    ges_addr = ges_rcpt.contractAddress
    ges_tx_hash = ges_rcpt.transactionHash.hex()
    print(f"✔ Deployed RealizedGestalt1155 V6.2.0: {ges_addr} (tx: {ges_tx_hash})")

    ges = w3.eth.contract(address=ges_addr, abi=compiled[ges_key]["abi"])

    with open(INSTALLATION_ID_PATH) as f:
        installation_id = f.read().strip()
    with open(SOUL_PATH, "rb") as f:
        soul_sha256 = hashlib.sha256(f.read()).hexdigest()

    shards_spec = [
        (
            0,
            "agent",
            ["$auth", "wallet_0x", "registry"],
            ["besta.pe", acct.address, f"eip155:{CHAIN_ID}:{ges_addr}"],
        ),
        (
            1,
            "$0",
            ["id", "loci", "click", "record", "show", "pwa_js"],
            ["parent", "agent.$0", "1", "true", "false", PROTO_INFT_PWA_JS],
        ),
        (
            1,
            "$1",
            ["hostname", "installation_id", "tee", "zone"],
            ["repsl-hailsounds", installation_id, "AMD SEV-SNP", "us-east4-b"],
        ),
        (
            3,
            "np",
            ["$auth", "entity", "x402Support"],
            ["besta.pe", "non-person", "true"],
        ),
        (
            4,
            "$0",
            ["id", "loci", "click", "record", "show", "model_default"],
            ["np", "agent.$1", "1", "true", "false", "gemini-4-argon"],
        ),
        (
            4,
            "$1",
            ["session", "uuid", "model", "born", "soul_sha256", "supported_trust"],
            [
                "b4a8a82b",
                "b4a8a82b-7ac2-4236-8abd-6cfff97e92d4",
                "gemini-4-argon",
                "2026-10-18T19:34:31.185Z",
                soul_sha256,
                "reputation,crypto-economic,tee-attestation",
            ],
        ),
    ]

    minted_tokens = {}
    current_total = ges.functions.totalShards().call()
    for expected_nonce, (link, ascii_str, keys, vals) in enumerate(shards_spec, start=1):
        if expected_nonce > current_total:
            gas_lim = 7000000 if "pwa_js" in keys else 2000000
            rcpt = send_tx(
                w3,
                acct,
                ges.functions.mintNextShard(acct.address, link, ascii_str, keys, vals).build_transaction(
                    tx_params(w3, acct, gas=gas_lim)
                ),
            )
            tx_h = rcpt.transactionHash.hex()
        else:
            tx_h = "already_minted"
        tid = ges.functions.tokenByNonce(expected_nonce).call()
        resolved = ges.functions.resolvePath(tid).call()
        print(
            f"✔ Minted Nonce {expected_nonce} (Link {link}, ASCII '{ascii_str}') -> Path: {resolved} | TokenID: {tid} ({hex(tid)})"
        )
        minted_tokens[resolved] = {
            "nonce": expected_nonce,
            "link": link,
            "ascii": ascii_str,
            "path": resolved,
            "token_id_dec": str(tid),
            "token_id_hex": hex(tid),
            "tx_hash": tx_h,
            "explorer_link": f"{EXPLORER_URL}/token/{ges_addr}/instance/{tid}",
        }

    deployment_manifest = {
        "network": "QGOV Mainnet",
        "chain_id": CHAIN_ID,
        "rpc_url": RPC_URL,
        "explorer_url": EXPLORER_URL,
        "deployer": acct.address,
        "contract": {
            "name": "RealizedGestalt1155",
            "version": "6.2.0",
            "address": ges_addr,
            "tx_hash": ges_tx_hash,
            "agent_registry": f"eip155:{CHAIN_ID}:{ges_addr}",
            "total_shards": len(shards_spec),
            "seedtree": minted_tokens,
        },
    }
    manifest_path = os.path.join(REPO_ROOT, "kairos_repsl", "json", "qgov_deployment.json")
    with open(manifest_path, "w") as f:
        json.dump(deployment_manifest, f, indent=2)
    print(f"✔ Saved V6.0.0 deployment manifest to {manifest_path}")


if __name__ == "__main__":
    main()
