import hashlib

def hash_document(file_path: str, chunk_size: int = 4096) -> str:
    """
    Generates a SHA-256 hash of a file, reading it in chunks for memory efficiency.
    
    Args:
        file_path (str): The path to the file to be hashed.
        chunk_size (int): The size of the chunks to read. Defaults to 4096 bytes.
        
    Returns:
        str: The hexadecimal SHA-256 hash of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
