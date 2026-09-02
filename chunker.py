import hashlib
import sqlite3
import argparse

chunk_size = 1024

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
""")

def save_chunks(file_path):
    """
    Breaks a file into chunks and saves it into the hash index.
    """
    with open(file_path, "rb") as f:
        offset = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            db.execute("INSERT OR IGNORE INTO chunks (chunk_hash, file_path, file_offset, chunk_size) VALUES (?, ?, ?, ?)",
                    (chunk_hash, file_path, offset, len(chunk_data)))
            offset += len(chunk_data)
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
        print("Hash collision!!")

    path, offset, size = matches[0]
    with open(path, "rb") as f:
        f.seek(offset)
        chunk_data = f.read(size)
        return chunk_data        

def count_matches(file_path):
    """
    Counts how many chunks in file already exists in index.
    """
    count = 0
    with open(file_path, "rb") as f:
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            if retrieve_chunk(chunk_hash):
                count += 1
    print("{} has {} chunk matches in index".format(file_path, count))
    return count

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-i", "--input", metavar="file_path", help="Adds file to chunk index")
group.add_argument("-g", "--generate", metavar="file_path", help="Outputs chunk hashes for file")
group.add_argument("-m", "--matches", metavar="file_path", help="Checks how many chunk matches in index")
group.add_argument("-r", "--reconstruct", nargs=2, metavar=("target_file", "hash_file"), help="Reconstructs a file from a series of hashes specified in [hash_file]. Output stored as ./text_data/[target_file].copy")
args = parser.parse_args()

if args.input:
    save_chunks(args.input)

if args.generate:
    with open(args.generate, "rb") as f:
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            print(chunk_hash)

if args.matches:
    count_matches(args.matches)

if args.reconstruct:
    target_file, hash_file = args.reconstruct
    with open(hash_file) as hashes, open(target_file+".copy", "wb") as out:
        for target_hash in hashes:
            chunk = retrieve_chunk(target_hash.strip())
            if chunk:
                out.write(chunk)
            else:
                out.write(b"?"*chunk_size) # TODO: Change to seek from original file to simulate sending from client