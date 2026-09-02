import hashlib
import sqlite3

chunk_size = 1024

conn = sqlite3.connect("chunks.db")
db = conn.cursor()

db.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_hash TEXT PRIMARY KEY NOT NULL,
        file_path TEXT NOT NULL,
        file_offset INTEGER NOT NULL,
        chunk_size INTEGER NOT NULL
    )
""")

with open("./text_data/the_adventures_of_sherlock_holmes.txt", "rb") as f:
    offset = 0
    while True:
        chunk_data = f.read(chunk_size)
        if not chunk_data:
            break
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        db.execute("INSERT INTO chunks (chunk_hash, file_path, file_offset, chunk_size) VALUES (?, ?, ?, ?)",
                (chunk_hash, "./text_data/the_adventures_of_sherlock_holmes.txt", offset, len(chunk_data)))
        offset += len(chunk_data)

target_hash = "3d09046fb9f5602d3da116ec06e69d8fc956987cd984f67b26f3f6645231166d"
db.execute("SELECT file_path, file_offset, chunk_size FROM chunks WHERE chunk_hash = ?", (target_hash,))
matches = db.fetchall()
if (len(matches) > 1):
    print("Hash collision!!")

for chunk in matches:
    path, offset, size = chunk
    print(path, offset, size)
    with open(path, "rb") as f:
        f.seek(offset)
        chunk_data = f.read(size)
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        print(chunk_hash)