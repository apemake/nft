import struct

def encode_joyfork_id(name, nonce=0, link=0):
    """
    Encodes a name, nonce, and link into a 32-byte Joyfork ID (uint256).
    Layout: [3 bytes Link] [3 bytes Nonce] [26 bytes ASCII Payload]
    Standard: Triad-Nonce (LNA-33X)
    """
    # 1. Prepare the parts (3 bytes each for Link and Nonce)
    # Using struct.pack(">I", ...) and slicing [1:] to get 3 bytes from 4
    link_bytes = struct.pack(">I", link & 0xFFFFFF)[1:]
    nonce_bytes = struct.pack(">I", nonce & 0xFFFFFF)[1:]
    
    # 2. Prepare the ASCII payload (max 26 bytes to fit in 32 bytes total)
    ascii_bytes = name.encode('ascii', 'ignore')[:26]
    # Pad with zeros if less than 26
    ascii_bytes = ascii_bytes.ljust(26, b'\x00')
    
    # 3. Concatenate
    joyfork_bytes = link_bytes + nonce_bytes + ascii_bytes
    
    # 4. Convert to uint256 integer
    return int.from_bytes(joyfork_bytes, byteorder='big')

def decode_joyfork_id(joyfork_id):
    """
    Decodes a 32-byte Joyfork ID back into its components.
    """
    joyfork_bytes = joyfork_id.to_bytes(32, byteorder='big')
    
    # Extract 3-byte segments by prepending a null byte for struct.unpack(">I", ...)
    link = struct.unpack(">I", b'\x00' + joyfork_bytes[0:3])[0]
    nonce = struct.unpack(">I", b'\x00' + joyfork_bytes[3:6])[0]
    ascii_payload = joyfork_bytes[6:].decode('ascii').rstrip('\x00')
    
    return ascii_payload, nonce, link

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        name = sys.argv[1]
        nonce = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        link = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        
        encoded = encode_joyfork_id(name, nonce, link)
        print(f"Name:    {name}")
        print(f"Nonce:   {nonce}")
        print(f"Link:    {link}")
        print(f"Encoded: {hex(encoded)}")
        
        decoded_name, decoded_nonce, decoded_link = decode_joyfork_id(encoded)
        print(f"Decoded: {decoded_name} (Nonce: {decoded_nonce}, Link: {decoded_link})")
