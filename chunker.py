import hashlib
import sqlite3
import argparse
import os

from rolling_hash import rabin_karp_chunks

def save_chunks(file_path):
    """
    Breaks a file into chunks and saves it into the hash index.
    Overwrites any existing entries associated with that file.
    """
    db.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))
    with open(file_path, "rb") as f:
        data = f.read()

    for offset, chunk_data in rabin_karp_chunks(data):
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        db.execute("INSERT OR IGNORE INTO chunks (chunk_hash, file_path, file_offset, chunk_size) VALUES (?, ?, ?, ?)",
                    (chunk_hash, file_path, offset, len(chunk_data)))
    conn.commit()

def retrieve_chunk(target_hash):
    """
    Retrieves the chunk data of the first matching entry in the hash index.
    """
    db.execute("SELECT file_path, file_offset, chunk_size FROM chunks WHERE chunk_hash = ?", (target_hash,))
    matches = db.fetchall()
    if (len(matches) == 0):
        return
    if (len(matches) > 1):
        print("Hash collision!!") # Not handling it in this demo as it requires the full synchronisation protocol

    path, offset, size = matches[0]
    with open(path, "rb") as f:
        f.seek(offset)
        chunk_data = f.read(size)
        return chunk_data        

def count_matches(file_path):
    """
    Counts how many chunks in file already exists in index.
    """
    with open(file_path, "rb") as f:
        data = f.read()

    chunk_hits = 0
    total_chunks = 0
    for _, chunk_data in rabin_karp_chunks(data):
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        total_chunks += 1
        if retrieve_chunk(chunk_hash):
            chunk_hits += 1
    return (chunk_hits, total_chunks)



parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--demo", help="Runs through a test suite to demo functionality", action="store_true")
group.add_argument("-i", "--input", metavar="file_path", help="Adds file to chunk index")
group.add_argument("-g", "--generate", metavar="file_path", help="Outputs chunk hashes for file")
group.add_argument("-m", "--matches", metavar="file_path", help="Checks how many chunk matches in index")
group.add_argument("-r", "--reconstruct", metavar=("hash_file"), help="Reconstructs a file from a series of hashes specified in [hash_file].")
args = parser.parse_args()

if args.demo:
    print("=== Running demo ===")

    conn = sqlite3.connect(":memory:")
    db = conn.cursor()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_hash TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_offset INTEGER NOT NULL,
            chunk_size INTEGER NOT NULL,
            UNIQUE(chunk_hash, file_path, file_offset, chunk_size)
        );
        CREATE INDEX IF NOT EXISTS hash_index ON chunks(chunk_hash);
        CREATE INDEX IF NOT EXISTS file_index ON chunks(file_path);
    """)

    # No chunks cached. File needs to be transferred from client.
    sherlock_file = "./text_data/the_adventures_of_sherlock_holmes.txt"
    print("Test 1: Checking existing chunks of the_adventures_of_sherlock_holmes.txt")
    hits, total = count_matches(sherlock_file)
    print("{} / {} chunks available in index\n".format(hits, total))

    print("Test 2: Chunking and indexing file")
    save_chunks(sherlock_file)
    hits, total = count_matches(sherlock_file)
    print("{} / {} chunks available in index\n".format(hits, total))

    print("Test 3: Generating hashes for the_adventures_of_sherlock_holmes.txt")
    with open(sherlock_file, "rb") as f:
        data = f.read()
    hash_file = "/tmp/temp.txt"
    with open(hash_file, "wb") as f:
        for offset, chunk_data in rabin_karp_chunks(data):
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            f.write(chunk_hash.encode() + b"\n")
    print("Hashes written to {}\n".format(hash_file))

    print("Test 4: Reconstructing the_adventures_of_sherlock_holmes.txt from hashes")
    out_file = "/tmp/temp.out"
    with open(hash_file) as hashes, open(out_file, "wb") as out:
        for target_hash in hashes:
            chunk = retrieve_chunk(target_hash.strip())
            if chunk:
                out.write(chunk)
            else:
                out.write(b"#### [missing chunk] ####")
    print("Reconstructed file written to {}\n".format(out_file))

    print("Test 5: Comparing SHA256 hashes of original and reconstructed file")
    with open(sherlock_file, "rb") as f:
        print("SHA256 of {}: {}\n".format(
                sherlock_file, hashlib.file_digest(f, "sha256").hexdigest())
        )
    with open(out_file, "rb") as f:
        print("SHA256 of {}: {}\n".format(
                out_file, hashlib.file_digest(f, "sha256").hexdigest())
        )
    
    print("Test 6: Appending data to source file")
    with open(sherlock_file, "a") as f:
        f.write("\n and they lived happily ever after. The End.\n")
    hits, total = count_matches(sherlock_file)
    print("{} / {} chunks still available in index\n".format(hits, total))

else:
    conn = sqlite3.connect("chunks.db")
    db = conn.cursor()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_hash TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_offset INTEGER NOT NULL,
            chunk_size INTEGER NOT NULL,
            UNIQUE(chunk_hash, file_path, file_offset, chunk_size)
        );
        CREATE INDEX IF NOT EXISTS hash_index ON chunks(chunk_hash);
        CREATE INDEX IF NOT EXISTS file_index ON chunks(file_path);
    """)

if args.input:
    save_chunks(args.input)

if args.generate:
    with open(args.generate, "rb") as f:
        data = f.read()
    for offset, chunk_data in rabin_karp_chunks(data):
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        print(chunk_hash)

if args.matches:
    hits, total = count_matches(args.matches)
    print("{} / {} chunks available in index".format(hits, total))

if args.reconstruct:
    hash_file = args.reconstruct
    with open(hash_file) as hashes, open("/tmp/copy.txt", "wb") as out:
        for target_hash in hashes:
            chunk = retrieve_chunk(target_hash.strip())
            if chunk:
                out.write(chunk)
            else:
                # This functionality cannot be implemented seperately from the synchronisation protocol.
                # It relies on the client keeping track of where it's up to in the source file.
                print("Missing chunk. Fetching directly from file")
                out.write(b"#### [missing chunk] ####")
    print("Reconstructed file saved at /tmp/copy.txt")