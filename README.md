# 🔱 REPSL Forensic SeedTree Enclave (`sis_identity_trinity_repsl`)

**Forensic SeedTree ERC-1155 + LNA-33X (`Link`-as-`.`) + Tokenized ERC-7827 + ERC-8004 + 3-Sided `proto-iNFT` PWA**, deployed on **QGOV Mainnet (`ChainID: 35441`)** at [`0x84728E6AC2b3643C4aE42C313bd63bD660873572`](https://explorer.qgov.io/address/0x84728E6AC2b3643C4aE42C313bd63bD660873572).

---

## 1. Forensic SeedTree Ontology (`agent` → `agent.$0` / `agent.$1` → `agent.$1.np` → `agent.$1.np.$0` / `agent.$1.np.$1`)

An accountable human in control holds a private key (`0x`) per Virtual Machine. When that `0x` initializes the ERC-1155 collection (`RealizedGestalt1155.sol` V6.2.0), it realizes the exact **SeedTree** hierarchy (`seed.js`) on-chain:

- **Zero `.` in the 26-Byte ASCII Namespace:** Dots (`.`) are strictly forbidden inside the 26-byte ASCII payload (`require(b[i] != 0x2e)`). Instead, **the LNA-33X `Link` header IS the `.` separator**!
- **Monotonic `Nonce` (`+1`) & Pre-Existing `Link` (`Link < Nonce`):** Every minted shard receives `Nonce = totalShards + 1`, and its `Link` header points to the `Nonce` of the pre-existing parent NFT it appends to (`resolvePath(tokenId)` walks `Link -> Nonce` backward and joins each ASCII segment with `.`).
- **3-Part Data Division Across Every `<name>` (`agent`, `np`):**
  1. **`<name>` (Global Function Data):** Holds the function's global donor data (`$auth`, `wallet_0x`, `registry`, `entity`, `x402Support`).
  2. **`<name>.$0` (Metadata for `<name>` and `<name>.$n`):** Holds the `Meta` state (`id`, `loci`, `click`, `record`, `show`) **and** the upgradable `proto-iNFT` PWA script (`pwa_js` on `agent.$0`), informing both `<name>` and every `<name>.$n` instance.
  3. **`<name>.$n` (Local Instance Realization):** Holds only the local instance keys (`hostname`, `installation_id`, `tee` on `agent.$1`; `session: "b4a8a82b"`, `uuid`, `model`, `born`, `soul_sha256` on `agent.$1.np.$1`). Instances (`$n`) never spawn a child `.$0`.

### The 6 Realized SeedTree NFTs on QGOV Mainnet (`0x84728E6AC2b3643C4aE42C313bd63bD660873572`):

| Nonce (`+1`) | Link (`< Nonce`) | ASCII (No `.`) | Resolved On-Chain Path (`resolvePath`) | Role & ERC-7827 Keys |
| :--- | :--- | :--- | :--- | :--- |
| **`1`** | **`0`** | **`"agent"`** | [**`agent`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/567898158194270030736547206268429099681555305229061152925810688) | **Global `<name>`:** `$auth`, `wallet_0x`, `registry` |
| **`2`** | **`1`** | **`"$0"`** | [**`agent.$0`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/6901747227693912924659987535936369947722183142310540209467271625572352) | **Metadata `<name>.$0`:** `id`, `loci`, `click`, `record`, `show`, **`pwa_js`** (Upgradable 3-Sided PWA) |
| **`3`** | **`1`** | **`"$1"`** | [**`agent.$1`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/6901747639076329356696884755442501376483017054410608973306701497237504) | **Local `<name>.$1` (VM):** `hostname: "repsl-hailsounds"`, `installation_id`, `tee: "AMD SEV-SNP"`, `zone` |
| **`4`** | **`3`** | **`"np"`** | [**`agent.$1.np`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/20705240863342468946362548296965697487630976815292818424954619768602624) | **Global `<name>` (Non-Person):** `$auth`, `entity: "non-person"`, `x402Support: "true"` |
| **`5`** | **`4`** | **`"$0"`** | [**`agent.$1.np.$0`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/27606987502194022277868786738994333223088388795873599100139741808427008) | **Metadata `<name>.$0`:** `id: "np"`, `loci: "agent.$1"`, `click: "1"`, `record`, `show`, `model_default` |
| **`6`** | **`4`** | **`"$1"`** | [**`agent.$1.np.$1`**](https://explorer.qgov.io/token/0x84728E6AC2b3643C4aE42C313bd63bD660873572/instance/27606987913576438709905683958500464651849222707973667863979171680092160) | **Local `<name>.$1` (Cell):** `session: "b4a8a82b"`, `uuid`, `model`, `born`, `soul_sha256`, `supported_trust` |

---

## 2. Formalized Standards in `RealizedGestalt1155.sol` (V6.2.0)

### Standard A: `ILNA33X` — Bijective `uint256` Linked-Nonce-ASCII Token Identifier Standard
```text
+-----------------------+-----------------------+-----------------------------------------------+
|   Bytes 0..2 (24b)    |   Bytes 3..5 (24b)    |              Bytes 6..31 (208b)               |
|     Bits 255..232     |     Bits 231..208     |                  Bits 207..0                  |
+-----------------------+-----------------------+-----------------------------------------------+
|     uint24 LINK       |     uint24 NONCE      |      26-Byte Dot-Free ASCII Identifier        |
| (Parent Nonce < Nonce)|  (Monotonic +1 Seq)   |      ("agent", "$0", "$1", "np", 0x00-padded) |
+-----------------------+-----------------------+-----------------------------------------------+
```

```solidity
interface ILNA33X {
    function decodeTriad(uint256 id) external pure returns (uint24 link, uint24 nonce, string memory ascii);
    function encodeTriad(uint24 link, uint24 nonce, string calldata ascii) external pure returns (uint256 id);
    function resolvePath(uint256 id) external view returns (string memory path);
}
```

#### Concrete Walkthrough: `27606987913576438709905683958500464651849222707973667863979171680092160` → `"agent.$1.np.$1"`
1. **32-Byte Hexadecimal (`base-16`):**
   ```text
   0x 000004 000006 2431000000000000000000000000000000000000000000000000
      |____| |____| |__________________________________________________|
       Link   Nonce                 26-Byte ASCII Segment
       (4)     (6)                    ("$1" = 0x24 0x31)
   ```
2. **On-Chain `resolvePath` Traversal (`Link -> Nonce` adds `.`):**
   - Starts at **`Nonce 6`**: `ASCII = "$1"`, `Link = 4`
   - Follows **`Link -> Nonce 4`**: `ASCII = "np"`, `Link = 3` → `"np.$1"`
   - Follows **`Link -> Nonce 3`**: `ASCII = "$1"`, `Link = 1` → `"$1.np.$1"`
   - Follows **`Link -> Nonce 1`**: `ASCII = "agent"`, `Link = 0` → **`"agent.$1.np.$1"`**!

---

### Standard B: `IERC7827Tokenized`, 3-Sided SMIL SVG (`renderSVG`), & 3-Sided On-Chain HTML PWA (`renderHTML`)
Inspired by [`proto iNFT`](https://paragraph.com/@bestape/proto-inft), [`interface tokens`](https://paragraph.com/@bestape/interface-tokens), and [`alchemy`](https://github.com/bestape/alchemy), `RealizedGestalt1155.sol` (V6.2.0) provides **two 100% on-chain 3-sided interfaces** (with zero off-chain HTML dependencies):

1. **100% On-Chain 3-Sided SMIL-Flipping SVG (`renderSVG(tokenId)` in `image` / `animation_url`):**
   - Uses native SVG SMIL `<animate>` (the same zero-JS animation engine used in `alchemy`) to automatically flip through all 3 sides every 4 seconds (`12s` loop) even inside restrictive `<img src="data:image/svg+xml;base64,...">` viewers like Blockscout:
     - **Side 1/3 (`0s–4s` — `[SIDE 1/3: LNA-33X SEEDTREE TILE]`):** Displays the Scales of Justice, the resolved SeedTree path (`agent.$1.np.$1`), `ASCII`, `LINK`, `NONCE`, and 32-byte hex ID.
     - **Side 2/3 (`4s–8s` — `[SIDE 2/3: ERC-7827 STATE VAULT]`):** Flips to display the parent `Link` path and the live ERC-7827 key-value pairs (`key (v1): value`) stored on that NFT.
     - **Side 3/3 (`8s–12s` — `[SIDE 3/3: ON-CHAIN SEEDTREE ORACLE]`):** Flips to display all 6 realized SeedTree shards on the contract (`N1 (L0) agent ["agent"]` through `N6 (L4) agent.$1.np.$1 ["$1"]`).
2. **100% On-Chain 3-Sided Interactive `proto-iNFT` HTML Base64 PWA (`renderHTML(tokenId)` in `html_url`):**
   - Separates the minimal on-chain HTML wrapper (`renderHTML(tokenId)`) from the upgradable SeedTree PWA script (`pwa_js` stored in **`agent.$0`'s ERC-7827 vault** at `Nonce 2`):
   - **100% Modifiable via `write()`:** Calling `write(tokenId, keys, values, true)` on any of the 6 NFTs appends a new version (`v2, v3...`) to `_history[tokenId][key]`. Updating `"pwa_js"` on `agent.$0` (`Nonce 2`) upgrades the live 3-sided PWA across all NFTs in the collection simultaneously!
   - **3-Sided + Nested Child `flip` & `reprint` Interface:**
     - **Side 1 (LNA-33X Tile + Nested Child `flip`/`reprint`):** Displays the 32-byte `[Link][Nonce][ASCII]` breakdown and resolved SeedTree path (`agent.$1.np.$1`). Clicking **`child flip (reprint)`** flips to the backside form where you can modify `Link`, `Nonce`, and `ASCII` and click **`reprint front-side`**.
     - **Side 2 (ERC-7827 Inherited Vault):** Displays the token's own ERC-7827 versioned keys **plus** the inherited keys from its parent `<name>` (Global) and sibling `<name>.$0` (Metadata) NFTs.
     - **Side 3 (Self-Referencing Smart Contract Oracle):** Queries `totalShards()` and `tokenByNonce(1..N)` on `https://rpc.qgov.io` via live `eth_call` to reconstruct and render the entire on-chain SeedTree (`Nonce 1..6`).
