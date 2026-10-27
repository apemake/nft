// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

/**
 * @title ILNA33X
 * @dev Standard 1: Bijective uint256 Linked-Nonce-ASCII Token Identifier Standard.
 * Layout: [3-byte Link (bits 255..232)][3-byte Nonce (bits 231..208)][26-byte ASCII (bits 207..0)]
 */
interface ILNA33X {
    function decodeTriad(uint256 id) external pure returns (uint24 link, uint24 nonce, string memory ascii);
    function encodeTriad(uint24 link, uint24 nonce, string calldata ascii) external pure returns (uint256 id);
}

/**
 * @title IERC7827Tokenized
 * @dev Standard 2: Token-Scoped ERC-7827 JSON State & Version Control Extension for ERC-1155 / ERC-8004.
 */
interface IERC7827Tokenized {
    event TokenJsonValueSet(uint256 indexed tokenId, string key, string value, uint256 version, address indexed updater);
    function json() external view returns (string memory);
    function version(string calldata key) external view returns (string memory);
    function json(uint256 tokenId) external view returns (string memory);
    function version(uint256 tokenId, string calldata key) external view returns (string memory);
    function write(uint256 tokenId, string[] calldata keys, string[] calldata values, bool replace) external;
}

/**
 * @title RealizedGestalt1155_V5.0.0 (Sovereign ERC-1155 Agent & Cell Collection)
 * @dev Unifies ERC-1155 (.agent + cell.agent), ILNA33X, Tokenized ERC-7827, ERC-8004 (Trustless Agents), and x402.
 */
contract RealizedGestalt1155 is ERC1155, Ownable, ILNA33X, IERC7827Tokenized {
    using Strings for uint256;
    using Strings for address;

    string public name = "REPSL Sovereign Agent Enclave";
    string public symbol = "REPSL";

    uint256 public constant LINK_OFFSET = 232;
    uint256 public constant NONCE_OFFSET = 208;

    struct ValueVersion {
        string value;
        uint256 timestamp;
        address updater;
    }

    mapping(uint256 => mapping(string => ValueVersion[])) private _history;
    mapping(uint256 => mapping(string => bool)) private _hasKey;
    mapping(uint256 => string[]) private _keys;

    event ShardMinted(address indexed to, uint256 indexed tokenId, uint24 link, uint24 nonce, string ascii);

    constructor() ERC1155("") Ownable(msg.sender) {}

    /**
     * @dev ILNA33X: Encodes [uint24 link][uint24 nonce][26-byte ASCII] into a 32-byte uint256 tokenId.
     */
    function encodeTriad(uint24 link, uint24 nonce, string calldata ascii) public pure override returns (uint256 id) {
        bytes memory b = bytes(ascii);
        require(b.length <= 26, "LNA33X: ASCII exceeds 26 bytes");
        id = (uint256(link) << LINK_OFFSET) | (uint256(nonce) << NONCE_OFFSET);
        for (uint256 i = 0; i < b.length; i++) {
            id |= uint256(uint8(b[i])) << (200 - i * 8);
        }
    }

    /**
     * @dev ILNA33X: Decodes a 32-byte uint256 tokenId into [uint24 link][uint24 nonce][trimmed ASCII string].
     */
    function decodeTriad(uint256 id) public pure override returns (uint24 link, uint24 nonce, string memory ascii) {
        link = uint24(id >> LINK_OFFSET);
        nonce = uint24(id >> NONCE_OFFSET);
        uint256 len = 0;
        for (uint256 i = 0; i < 26; i++) {
            uint8 b = uint8(id >> (200 - i * 8));
            if (b == 0) break;
            len++;
        }
        bytes memory nameBytes = new bytes(len);
        for (uint256 i = 0; i < len; i++) {
            nameBytes[i] = bytes1(uint8(id >> (200 - i * 8)));
        }
        return (link, nonce, string(nameBytes));
    }

    function getLatestValue(uint256 tokenId, string memory key) public view returns (string memory) {
        if (!_hasKey[tokenId][key]) return "7827 NOT SYNCED";
        return _history[tokenId][key][_history[tokenId][key].length - 1].value;
    }

    function getScalesPath() internal pure returns (string memory) {
        return '<path fill="#ECCA90" d="M20,10V12H11V14H13V22H11V24H19V22H17V14H19V12H10V10H20Z"/>';
    }

    function renderSVG(uint256 tokenId) public view returns (string memory) {
        (uint24 link, uint24 nonce, string memory asciiName) = decodeTriad(tokenId);
        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600">',
            '<rect width="400" height="600" fill="#050505"/>',
            '<rect x="20" y="20" width="360" height="560" rx="15" fill="none" stroke="#ECCA90" stroke-width="3"/>',
            '<text x="200" y="65" fill="#00e5ff" font-family="monospace" font-size="11" text-anchor="middle">ERC-1155 + LNA-33X + ERC-7827 + ERC-8004</text>',
            '<g transform="translate(152,95) scale(4)">', getScalesPath(), '</g>',
            '<text x="200" y="265" fill="#fdfcf0" font-family="monospace" font-size="22" font-weight="bold" text-anchor="middle">', asciiName, '</text>',
            '<text x="200" y="305" fill="#d500f9" font-family="monospace" font-size="13" text-anchor="middle">LINK: ', uint256(link).toString(), ' | NONCE: ', uint256(nonce).toString(), '</text>',
            '<text x="200" y="345" fill="#00e676" font-family="monospace" font-size="11" text-anchor="middle">x402 + TEE ATTESTED</text>',
            '<text x="200" y="385" fill="#888" font-family="monospace" font-size="9" text-anchor="middle">', tokenId.toHexString(32), '</text>',
            '<text x="200" y="470" fill="#ECCA90" font-family="monospace" font-size="15" font-weight="bold" text-anchor="middle">CELL.AGENT REALIZED</text>',
            '</svg>'
        ));
        return string(abi.encodePacked("data:image/svg+xml;base64,", Base64.encode(bytes(svg))));
    }

    function _renderKvRows(uint256 tokenId) internal view returns (string memory) {
        string[] storage keys = _keys[tokenId];
        string memory kvRows = "";
        for (uint256 i = 0; i < keys.length; i++) {
            string memory k = keys[i];
            ValueVersion storage latest = _history[tokenId][k][_history[tokenId][k].length - 1];
            kvRows = string(abi.encodePacked(
                kvRows,
                '<div class="kv"><span class="k">', k, ' (v', _history[tokenId][k].length.toString(), '):</span> <span class="v">', latest.value, '</span></div>'
            ));
        }
        return kvRows;
    }

    function renderHTML(uint256 tokenId) public view returns (string memory) {
        (uint24 link, uint24 nonce, string memory asciiName) = decodeTriad(tokenId);
        string memory hexId = tokenId.toHexString(32);
        string memory cAddr = address(this).toHexString();
        string memory kvRows = _renderKvRows(tokenId);

        string memory html = string(abi.encodePacked(
            '<!DOCTYPE html><html><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<meta name="apple-mobile-web-app-capable" content="yes">',
            '<meta name="theme-color" content="#0b0e14">',
            '<link rel="manifest" href="data:application/json;base64,',
            Base64.encode(bytes(string(abi.encodePacked('{"name":"', asciiName, '","short_name":"', asciiName, '","display":"standalone","background_color":"#0b0e14","theme_color":"#ECCA90"}')))),
            '">',
            '<title>', asciiName, ' | LNA-33X PWA</title>',
            '<style>',
            '*{box-sizing:border-box}body{background:#0b0e14;color:#e6edf3;font-family:monospace;margin:0;padding:14px;line-height:1.45}',
            '.box{background:#111622;border:1px solid #30363d;border-radius:8px;padding:12px;margin-bottom:12px}',
            'h1{margin:0 0 6px;font-size:16px;color:#ECCA90}h2{margin:0 0 8px;font-size:13px;color:#00e5ff}',
            '.hex{word-break:break-all;font-size:12px;background:#050505;padding:8px;border-radius:6px;border:1px solid #1f2937}',
            '.c-lnk{color:#00e5ff;font-weight:bold}.c-non{color:#d500f9;font-weight:bold}.c-asc{color:#00e676;font-weight:bold}',
            '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(52px,1fr));gap:6px;margin-top:8px}',
            '.cell{background:#050505;border:1px solid #1f2937;border-radius:4px;padding:4px;text-align:center;font-size:11px}',
            '.cell.on{border-color:#00e676}.hx{color:#8b949e;font-size:10px}.ch{color:#00e676;font-size:14px;font-weight:bold}',
            'input{background:#050505;color:#e6edf3;border:1px solid #30363d;padding:6px 8px;font-family:monospace;font-size:12px;border-radius:4px;width:100%;margin-top:4px}',
            '.kv{padding:4px 0;border-bottom:1px solid #1f2937;font-size:12px}.k{color:#ECCA90;font-weight:bold}.v{color:#fdfcf0;word-break:break-all}',
            '</style></head><body>',
            '<div class="box"><h1>&#9878; ', asciiName, ' &mdash; ERC-1155 + ERC-7827 + ERC-8004 PWA</h1>',
            '<div style="font-size:11px;color:#8b949e">Registry: eip155:35441:<span id="ca">', cAddr, '</span> | x402: Active | <span id="rpcSt" style="color:#00e676">RPC Ready</span></div></div>'
        ));

        html = string(abi.encodePacked(
            html,
            '<div class="box"><h2>1. LNA-33X 32-Byte (256-Bit) Hex-to-ASCII Tree Anatomy</h2>',
            '<div class="hex" id="hexBar"></div>',
            '<div style="font-size:11px;margin-top:6px">',
            '<span class="c-lnk">&#9632; [Bytes 0..2] Link (uint24): <span id="dLnk">', uint256(link).toString(), '</span></span> &nbsp;|&nbsp; ',
            '<span class="c-non">&#9632; [Bytes 3..5] Nonce (uint24): <span id="dNon">', uint256(nonce).toString(), '</span></span> &nbsp;|&nbsp; ',
            '<span class="c-asc">&#9632; [Bytes 6..31] 26-Byte ASCII Tree: "<span id="dAsc">', asciiName, '</span>"</span>',
            '</div><div class="grid" id="byteGrid"></div></div>',
            '<div class="box"><h2>2. Live Hex &harr; ASCII Translator &amp; QGOV Contract Reader</h2>',
            '<input id="inHex" value="', hexId, '" placeholder="Paste any 0x... 32-byte LNA-33X tokenId or type below">',
            '<div style="display:flex;gap:6px;margin-top:6px">',
            '<input id="inLnk" type="number" value="', uint256(link).toString(), '" placeholder="Link (uint24)" style="width:25%">',
            '<input id="inNon" type="number" value="', uint256(nonce).toString(), '" placeholder="Nonce (uint24)" style="width:25%">',
            '<input id="inAsc" value="', asciiName, '" maxlength="26" placeholder="ASCII cell.agent (max 26B)" style="width:50%">',
            '</div></div>',
            '<div class="box"><h2>3. ERC-7827 Token-Scoped Versioned JSON Vault</h2><div id="kvBox">', kvRows, '</div></div>'
        ));

        html = string(abi.encodePacked(
            html,
            '<script>',
            'const CA="', cAddr, '",RPC="https://rpc.qgov.io";',
            'const inHex=document.getElementById("inHex"),inLnk=document.getElementById("inLnk"),inNon=document.getElementById("inNon"),inAsc=document.getElementById("inAsc");',
            'function renderHex(h){',
            'const s=h.replace(/^0x/i,"").padStart(64,"0").slice(0,64);',
            'const lHex=s.slice(0,6),nHex=s.slice(6,12),aHex=s.slice(12,64);',
            'document.getElementById("hexBar").innerHTML="0x<span class=\\"c-lnk\\">"+lHex+"</span><span class=\\"c-non\\">"+nHex+"</span><span class=\\"c-asc\\">"+aHex+"</span>";',
            'const lVal=parseInt(lHex,16),nVal=parseInt(nHex,16);',
            'let asc="",grid="";',
            'for(let i=0;i<26;i++){',
            'const bHex=aHex.slice(i*2,i*2+2),code=parseInt(bHex,16);',
            'const ch=code>=32&&code<=126?String.fromCharCode(code):"&middot;";',
            'if(code>0)asc+=String.fromCharCode(code);',
            'grid+="<div class=\\"cell "+(code>0?"on":"")+"\\"><div class=\\"hx\\">0x"+bHex+"</div><div class=\\"ch\\">"+ch+"</div><div class=\\"hx\\">"+code+"</div></div>";',
            '}',
            'document.getElementById("dLnk").textContent=lVal+" (0x"+lHex+")";',
            'document.getElementById("dNon").textContent=nVal+" (0x"+nHex+")";',
            'document.getElementById("dAsc").textContent=asc;',
            'document.getElementById("byteGrid").innerHTML=grid;',
            '}',
            'function packInputs(){',
            'const l=(parseInt(inLnk.value||0)&0xffffff).toString(16).padStart(6,"0");',
            'const n=(parseInt(inNon.value||0)&0xffffff).toString(16).padStart(6,"0");',
            'let a="";for(let i=0;i<26;i++){a+=(i<inAsc.value.length?inAsc.value.charCodeAt(i):0).toString(16).padStart(2,"0");}',
            'inHex.value="0x"+l+n+a;renderHex(inHex.value);queryChain(inHex.value);',
            '}',
            'async function queryChain(h){',
            'try{',
            'const idHex=h.replace(/^0x/i,"").padStart(64,"0");',
            'const r=await fetch(RPC,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({jsonrpc:"2.0",id:1,method:"eth_call",params:[{to:CA,data:"0x7034f109"+idHex},"latest"]})});',
            'const d=await r.json();',
            'if(d.result&&d.result!=="0x")document.getElementById("rpcSt").textContent="Verified via eth_call on rpc.qgov.io";',
            '}catch(e){}',
            '}',
            'inHex.oninput=()=>{renderHex(inHex.value);queryChain(inHex.value);};',
            'inLnk.oninput=packInputs;inNon.oninput=packInputs;inAsc.oninput=packInputs;',
            'renderHex(inHex.value);queryChain(inHex.value);',
            '</script></body></html>'
        ));
        return string(abi.encodePacked("data:text/html;base64,", Base64.encode(bytes(html))));
    }

    function mintShard(address to, uint256 tokenId, bytes memory data) external onlyOwner {
        _mint(to, tokenId, 1, data);
        (uint24 link, uint24 nonce, string memory asciiName) = decodeTriad(tokenId);
        emit ShardMinted(to, tokenId, link, nonce, asciiName);
    }

    function write(uint256 tokenId, string[] calldata keys, string[] calldata values, bool replace) external override {
        require(balanceOf(msg.sender, tokenId) > 0 || owner() == msg.sender, "SIS-01: Unauthorized");
        require(keys.length == values.length, "ERC7827: Length mismatch");
        for (uint256 i = 0; i < keys.length; i++) {
            if (!_hasKey[tokenId][keys[i]]) {
                _hasKey[tokenId][keys[i]] = true;
                _keys[tokenId].push(keys[i]);
            } else {
                require(replace, "ERC7827: Key exists");
            }
            _history[tokenId][keys[i]].push(ValueVersion({value: values[i], timestamp: block.timestamp, updater: msg.sender}));
            emit TokenJsonValueSet(tokenId, keys[i], values[i], _history[tokenId][keys[i]].length, msg.sender);
        }
    }

    function version(uint256 tokenId, string calldata key) external view override returns (string memory) {
        if (!_hasKey[tokenId][key]) return "[]";
        ValueVersion[] storage hist = _history[tokenId][key];
        bytes memory out = "[";
        for (uint256 i = 0; i < hist.length; i++) {
            out = abi.encodePacked(out, '"', hist[i].value, '"', (i == hist.length - 1 ? "" : ","));
        }
        return string(abi.encodePacked(out, "]"));
    }

    function _renderAttributes(uint256 tokenId) internal view returns (string memory) {
        string[] storage keys = _keys[tokenId];
        if (keys.length == 0) {
            return '{"trait_type":"Status","value":"7827 NOT SYNCED"}';
        }
        bytes memory attrs = "";
        for (uint256 i = 0; i < keys.length; i++) {
            ValueVersion storage latest = _history[tokenId][keys[i]][_history[tokenId][keys[i]].length - 1];
            attrs = abi.encodePacked(attrs, '{"trait_type":"', keys[i], '","value":"', latest.value, '"}', (i == keys.length - 1 ? "" : ","));
        }
        return string(attrs);
    }

    /**
     * @dev ERC-8004 + Tokenized ERC-7827 unified registration & metadata JSON.
     */
    function json(uint256 tokenId) public view override returns (string memory) {
        (, , string memory asciiName) = decodeTriad(tokenId);
        string memory cAddr = address(this).toHexString();
        return string(abi.encodePacked(
            '{"type":"https://eips.ethereum.org/EIPS/eip-8004#registration-v1",',
            '"name":"', asciiName, '",',
            '"description":"Sovereign LNA-33X ERC-1155 Cell/Agent Shard with Tokenized ERC-7827 PWA & x402 Support",',
            '"image":"', renderSVG(tokenId), '",',
            '"animation_url":"', renderHTML(tokenId), '",',
            '"x402Support":true,',
            '"active":true,',
            '"supportedTrust":["reputation","crypto-economic","tee-attestation"],',
            '"registrations":[{"agentId":"', tokenId.toString(), '","agentRegistry":"eip155:35441:', cAddr, '"}],',
            '"attributes":[', _renderAttributes(tokenId), ']}'
        ));
    }

    function uri(uint256 tokenId) public view override returns (string memory) {
        return string(abi.encodePacked("data:application/json;base64,", Base64.encode(bytes(json(tokenId)))));
    }

    function json() external pure override returns (string memory) { return "{}"; }
    function version(string calldata) external pure override returns (string memory) { return "[]"; }
}
