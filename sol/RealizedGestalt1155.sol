// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

interface ILNA33X {
    function decodeTriad(uint256 id) external pure returns (uint24 link, uint24 nonce, string memory ascii);
    function encodeTriad(uint24 link, uint24 nonce, string calldata ascii) external pure returns (uint256 id);
    function resolvePath(uint256 id) external view returns (string memory path);
}

interface IERC7827Tokenized {
    event TokenJsonValueSet(uint256 indexed tokenId, string key, string value, uint256 version, address indexed updater);
    function json() external view returns (string memory);
    function version(string calldata key) external view returns (string memory);
    function json(uint256 tokenId) external view returns (string memory);
    function version(uint256 tokenId, string calldata key) external view returns (string memory);
    function write(uint256 tokenId, string[] calldata keys, string[] calldata values, bool replace) external;
}

/**
 * @title RealizedGestalt1155_V6.2.0 (100% On-Chain 3-Sided SMIL SVG + On-Chain HTML Base64 proto-iNFT PWA)
 * @dev Enforces monotonic Nonce (+1), pre-existing Link (< Nonce), no '.' in ASCII, and Link-as-'.' SeedTree resolution.
 *      Zero off-chain HTML: both the 3-sided SMIL-animated SVG (`renderSVG`) and the 3-sided HTML PWA (`renderHTML`)
 *      are 100% on-chain!
 */
contract RealizedGestalt1155 is ERC1155, Ownable, ILNA33X, IERC7827Tokenized {
    using Strings for uint256;
    using Strings for address;

    string public name = "REPSL Forensic SeedTree Enclave";
    string public symbol = "SEED";

    uint256 public constant LINK_OFFSET = 232;
    uint256 public constant NONCE_OFFSET = 208;

    uint24 public totalShards;
    mapping(uint24 => uint256) public tokenByNonce;

    struct ValueVersion {
        string value;
        uint256 timestamp;
        address updater;
    }

    mapping(uint256 => mapping(string => ValueVersion[])) private _history;
    mapping(uint256 => mapping(string => bool)) private _hasKey;
    mapping(uint256 => string[]) private _keys;

    event ShardMinted(address indexed to, uint256 indexed tokenId, uint24 link, uint24 nonce, string ascii, string path);

    constructor() ERC1155("") Ownable(msg.sender) {}

    function encodeTriad(uint24 link, uint24 nonce, string calldata ascii) public pure override returns (uint256 id) {
        bytes memory b = bytes(ascii);
        require(b.length > 0 && b.length <= 26, "LNA33X: 1..26B");
        id = (uint256(link) << LINK_OFFSET) | (uint256(nonce) << NONCE_OFFSET);
        for (uint256 i = 0; i < b.length; i++) {
            require(b[i] != 0x2e, "LNA33X: no dot");
            id |= uint256(uint8(b[i])) << (200 - i * 8);
        }
    }

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

    function resolvePath(uint256 id) public view override returns (string memory path) {
        (uint24 link, , string memory seg) = decodeTriad(id);
        path = seg;
        uint256 depth = 0;
        while (link > 0 && depth < 16) {
            uint256 parentId = tokenByNonce[link];
            if (parentId == 0) break;
            (uint24 pLink, , string memory pSeg) = decodeTriad(parentId);
            path = string(abi.encodePacked(pSeg, ".", path));
            link = pLink;
            depth++;
        }
    }

    function getLatestValue(uint256 tokenId, string memory key) public view returns (string memory) {
        if (!_hasKey[tokenId][key]) return "";
        return _history[tokenId][key][_history[tokenId][key].length - 1].value;
    }

    function getKeys(uint256 tokenId) external view returns (string[] memory) {
        return _keys[tokenId];
    }

    function getScalesPath() internal pure returns (string memory) {
        return '<path fill="#ECCA90" d="M20,10V12H11V14H13V22H11V24H19V22H17V14H19V12H10V10H20Z"/>';
    }

    function _svgKvLines(uint256 tokenId, uint256 startY) internal view returns (string memory) {
        if (tokenId == 0) return "";
        string[] storage keys = _keys[tokenId];
        string memory out = "";
        uint256 y = startY;
        for (uint256 i = 0; i < keys.length && y < 490; i++) {
            string memory k = keys[i];
            if (keccak256(bytes(k)) == keccak256(bytes("pwa_js"))) continue;
            string memory val = _history[tokenId][k][_history[tokenId][k].length - 1].value;
            if (bytes(val).length > 26) {
                bytes memory vb = bytes(val);
                bytes memory shortB = new bytes(24);
                for (uint256 j = 0; j < 24; j++) shortB[j] = vb[j];
                val = string(abi.encodePacked(string(shortB), ".."));
            }
            out = string(abi.encodePacked(
                out,
                '<text x="38" y="', y.toString(), '" fill="#ECCA90" font-family="monospace" font-size="11">', k, ' (v', _history[tokenId][k].length.toString(), '): <tspan fill="#fdfcf0">', val, '</tspan></text>'
            ));
            y += 24;
        }
        return out;
    }

    function _svgSide2(uint256 tokenId) internal view returns (string memory) {
        (uint24 link, , ) = decodeTriad(tokenId);
        string memory parentInfo = link > 0 && tokenByNonce[link] != 0
            ? string(abi.encodePacked("Parent (Link ", uint256(link).toString(), "): ", resolvePath(tokenByNonce[link])))
            : "Root Constructor (Link 0)";
        return string(abi.encodePacked(
            '<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.32;0.34;0.65;0.67;1" dur="12s" repeatCount="indefinite"/>',
            '<text x="200" y="96" fill="#d500f9" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">[SIDE 2/3: ERC-7827 STATE VAULT]</text>',
            '<text x="200" y="122" fill="#00e5ff" font-family="monospace" font-size="11" text-anchor="middle">', parentInfo, '</text>',
            '<line x1="35" y1="136" x2="365" y2="136" stroke="#30363d" stroke-width="1"/>',
            _svgKvLines(tokenId, 164),
            '</g>'
        ));
    }

    function _svgSide3() internal view returns (string memory) {
        string memory rows = "";
        uint256 y = 158;
        for (uint24 n = 1; n <= totalShards && n <= 12; n++) {
            uint256 tid = tokenByNonce[n];
            (uint24 lk, , string memory asc) = decodeTriad(tid);
            rows = string(abi.encodePacked(
                rows,
                '<text x="38" y="', y.toString(), '" fill="#d500f9" font-family="monospace" font-size="11">N', uint256(n).toString(), ' (L', uint256(lk).toString(), ') <tspan fill="#00e676" font-weight="bold">', resolvePath(tid), '</tspan> <tspan fill="#888">["', asc, '"]</tspan></text>'
            ));
            y += 26;
        }
        return string(abi.encodePacked(
            '<g><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.65;0.67;1" dur="12s" repeatCount="indefinite"/>',
            '<text x="200" y="96" fill="#00e676" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">[SIDE 3/3: ON-CHAIN SEEDTREE ORACLE]</text>',
            '<text x="200" y="122" fill="#ECCA90" font-family="monospace" font-size="11" text-anchor="middle">Total Shards Minted: ', uint256(totalShards).toString(), '</text>',
            '<line x1="35" y1="136" x2="365" y2="136" stroke="#30363d" stroke-width="1"/>',
            rows,
            '</g>'
        ));
    }

    /**
     * @dev 3-Sided SMIL-Animated SVG (`data:image/svg+xml;base64,...`):
     * Automatically flips through Side 1 (LNA-33X Tile), Side 2 (ERC-7827 Vault), and Side 3 (SeedTree Oracle)
     * using pure SVG SMIL `<animate>` (just like Alchemy!), so all 3 sides flip inside `<img src=...>` on Blockscout!
     */
    function renderSVG(uint256 tokenId) public view returns (string memory) {
        (uint24 link, uint24 nonce, string memory ascii) = decodeTriad(tokenId);
        string memory fullPath = resolvePath(tokenId);
        string memory s1 = string(abi.encodePacked(
            '<g><animate attributeName="opacity" values="1;1;0;0;0;1" keyTimes="0;0.32;0.34;0.66;0.98;1" dur="12s" repeatCount="indefinite"/>',
            '<text x="200" y="96" fill="#00e5ff" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">[SIDE 1/3: LNA-33X SEEDTREE TILE]</text>',
            '<g transform="translate(152,115) scale(4)">', getScalesPath(), '</g>',
            '<text x="200" y="275" fill="#fdfcf0" font-family="monospace" font-size="22" font-weight="bold" text-anchor="middle">', fullPath, '</text>',
            '<text x="200" y="315" fill="#00e676" font-family="monospace" font-size="13" text-anchor="middle">ASCII: "', ascii, '"</text>',
            '<text x="200" y="350" fill="#d500f9" font-family="monospace" font-size="13" text-anchor="middle">LINK: ', uint256(link).toString(), ' | NONCE: ', uint256(nonce).toString(), '</text>',
            '<text x="200" y="390" fill="#888" font-family="monospace" font-size="9" text-anchor="middle">', tokenId.toHexString(32), '</text>',
            '<text x="200" y="455" fill="#ECCA90" font-family="monospace" font-size="12" text-anchor="middle">Link-as-Dot SeedTree Resolution</text></g>'
        ));
        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600"><rect width="400" height="600" fill="#050505"/>',
            '<rect x="20" y="20" width="360" height="560" rx="15" fill="none" stroke="#ECCA90" stroke-width="3"/>',
            '<text x="200" y="55" fill="#ECCA90" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle">', fullPath, ' | QGOV 35441</text>',
            s1, _svgSide2(tokenId), _svgSide3(),
            '<rect x="40" y="525" width="320" height="6" rx="3" fill="#1f2937"/>',
            '<rect x="40" y="525" width="106" height="6" rx="3" fill="#ECCA90"><animate attributeName="x" values="40;147;254;40" keyTimes="0;0.333;0.666;1" calcMode="discrete" dur="12s" repeatCount="indefinite"/></rect>',
            '<text x="200" y="555" fill="#888" font-family="monospace" font-size="10" text-anchor="middle">SMIL 3-SIDE AUTO-FLIP (4s/SIDE) + ON-CHAIN HTML</text></svg>'
        ));
        return string(abi.encodePacked("data:image/svg+xml;base64,", Base64.encode(bytes(svg))));
    }

    function _renderKvRows(uint256 tokenId, string memory label) internal view returns (string memory) {
        if (tokenId == 0) return "";
        string[] storage keys = _keys[tokenId];
        if (keys.length == 0) return "";
        string memory rows = string(abi.encodePacked('<div class="sec">[', label, ': ', resolvePath(tokenId), ']</div>'));
        for (uint256 i = 0; i < keys.length; i++) {
            string memory k = keys[i];
            if (keccak256(bytes(k)) == keccak256(bytes("pwa_js"))) continue;
            ValueVersion storage latest = _history[tokenId][k][_history[tokenId][k].length - 1];
            rows = string(abi.encodePacked(rows, '<div class="kv"><span class="k">', k, ' (v', _history[tokenId][k].length.toString(), '):</span> ', latest.value, '</div>'));
        }
        return rows;
    }

    function _renderInheritedVault(uint256 tokenId) internal view returns (string memory) {
        (uint24 link, uint24 nonce, ) = decodeTriad(tokenId);
        string memory out = _renderKvRows(tokenId, "Self");
        if (link > 0 && tokenByNonce[link] != 0) {
            out = string(abi.encodePacked(out, _renderKvRows(tokenByNonce[link], "Global <name>")));
            uint24 metaNonce = link + 1;
            if (metaNonce != nonce && tokenByNonce[metaNonce] != 0) {
                (uint24 mLink, , string memory mAsc) = decodeTriad(tokenByNonce[metaNonce]);
                if (mLink == link && keccak256(bytes(mAsc)) == keccak256(bytes("$0"))) {
                    out = string(abi.encodePacked(out, _renderKvRows(tokenByNonce[metaNonce], "Metadata <name>.$0")));
                }
            }
        }
        return out;
    }

    function renderHTML(uint256 tokenId) public view returns (string memory) {
        string memory fullPath = resolvePath(tokenId);
        string memory pwaJs = _hasKey[tokenId]["pwa_js"]
            ? getLatestValue(tokenId, "pwa_js")
            : (tokenByNonce[2] != 0 ? getLatestValue(tokenByNonce[2], "pwa_js") : "");
        string memory html = string(abi.encodePacked(
            '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>', fullPath, '</title></head>',
            '<body data-ca="', address(this).toHexString(), '" data-tid="', tokenId.toHexString(32), '" data-path="', fullPath, '">',
            '<div id="vaultData" style="display:none">', _renderInheritedVault(tokenId), '</div>',
            '<div id="app"></div><script>', pwaJs, '</script></body></html>'
        ));
        return string(abi.encodePacked("data:text/html;base64,", Base64.encode(bytes(html))));
    }

    function mintNextShard(address to, uint24 link, string calldata ascii, string[] calldata keys, string[] calldata values) external onlyOwner returns (uint256 tokenId) {
        uint24 nextNonce = totalShards + 1;
        if (nextNonce == 1) {
            require(link == 0, "LNA33X: Root Link 0");
        } else {
            require(link > 0 && link < nextNonce && tokenByNonce[link] != 0, "LNA33X: Invalid Link");
        }
        tokenId = encodeTriad(link, nextNonce, ascii);
        totalShards = nextNonce;
        tokenByNonce[nextNonce] = tokenId;
        _mint(to, tokenId, 1, "");
        if (keys.length > 0) {
            _writeInternal(tokenId, keys, values, true);
        }
        emit ShardMinted(to, tokenId, link, nextNonce, ascii, resolvePath(tokenId));
    }

    function _writeInternal(uint256 tokenId, string[] calldata keys, string[] calldata values, bool replace) internal {
        require(keys.length == values.length, "ERC7827: Length");
        for (uint256 i = 0; i < keys.length; i++) {
            if (!_hasKey[tokenId][keys[i]]) {
                _hasKey[tokenId][keys[i]] = true;
                _keys[tokenId].push(keys[i]);
            } else {
                require(replace, "ERC7827: Exists");
            }
            _history[tokenId][keys[i]].push(ValueVersion({value: values[i], timestamp: block.timestamp, updater: msg.sender}));
            emit TokenJsonValueSet(tokenId, keys[i], values[i], _history[tokenId][keys[i]].length, msg.sender);
        }
    }

    function write(uint256 tokenId, string[] calldata keys, string[] calldata values, bool replace) external override {
        require(balanceOf(msg.sender, tokenId) > 0 || owner() == msg.sender, "SIS-01: Auth");
        _writeInternal(tokenId, keys, values, replace);
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
        (uint24 link, uint24 nonce, string memory ascii) = decodeTriad(tokenId);
        string[] storage keys = _keys[tokenId];
        bytes memory attrs = abi.encodePacked(
            '{"trait_type":"SeedTree Path","value":"', resolvePath(tokenId), '"},',
            '{"trait_type":"LNA-33X Link","value":"', uint256(link).toString(), '"},',
            '{"trait_type":"LNA-33X Nonce","value":"', uint256(nonce).toString(), '"},',
            '{"trait_type":"LNA-33X ASCII","value":"', ascii, '"}'
        );
        for (uint256 i = 0; i < keys.length; i++) {
            if (keccak256(bytes(keys[i])) == keccak256(bytes("pwa_js"))) continue;
            ValueVersion storage latest = _history[tokenId][keys[i]][_history[tokenId][keys[i]].length - 1];
            attrs = abi.encodePacked(attrs, ',{"trait_type":"', keys[i], '","value":"', latest.value, '"}');
        }
        return string(attrs);
    }

    function json(uint256 tokenId) public view override returns (string memory) {
        string memory fullPath = resolvePath(tokenId);
        string memory cAddr = address(this).toHexString();
        string memory svgUri = renderSVG(tokenId);
        string memory htmlUri = renderHTML(tokenId);
        bool useHtmlAnim = tokenByNonce[2] != 0 && keccak256(bytes(getLatestValue(tokenByNonce[2], "animation_mode"))) == keccak256(bytes("html"));
        return string(abi.encodePacked(
            '{"type":"https://eips.ethereum.org/EIPS/eip-8004#registration-v1",',
            '"name":"', fullPath, '",',
            '"description":"Forensic SeedTree ERC-1155 Shard (LNA-33X + Tokenized ERC-7827 + ERC-8004 + x402 proto-iNFT PWA)",',
            '"image":"', svgUri, '",',
            '"animation_url":"', (useHtmlAnim ? htmlUri : svgUri), '",',
            '"html_url":"', htmlUri, '",',
            '"x402Support":true,"active":true,',
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
