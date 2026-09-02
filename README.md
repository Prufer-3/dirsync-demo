# dirsync-demo

This is a demo of the file chunking functionality described in the design document, written in Python.
I chose to implement this component since it's crucial for achieving the core requirement of bandwidth efficiency in my design.

It's different to how it might look in the completed system, since my proposed synchronisation protocol hasn't been implemented, but the core algorithm is the same.

Quick demo: `python3 chunker.py -d`

Alternatively, you can manually chunk and index files with chunker.py.
Use `python3 chunker.py -h` to see options.

Example workflow:
```
python3 chunker.py -i ./text_data/the_adventures_of_sherlock_holmes.txt
python3 chunker.py -i ./text_data/pride_and_prejudice.txt

python3 chunker.py -m ./text_data/the_pride_and_prejudice_of_sherlock_holmes.txt
python3 chunker.py -g ./text_data/the_pride_and_prejudice_of_sherlock_holmes.txt > /tmp/hashes.txt
python3 chunker.py -r /tmp/hashes.txt
```

Milestones:
- [x] Fixed-size chunks at boundary intervals
    - [x] Ingest small files and break them into fixed-size chunks.
    - [x] Hash each chunk and store in a database.
    - [x] Lookup chunk metadata by hash and retrieve from file system.
- [x] Reconstructing files with chunks from the same file
    - [x] Implement functionality to report statistics on chunk matches between files.
    - [x] Iteratively reconstruct files from hashes.
    - [x] Verify integrity of reconstructed files with a full file hash.
- [x] Variable-size chunks with content-defined chunking
    - [x] Add a mask heuristic along with chunk size limits to the Rabin fingerprinting rolling hash scheme.
    - [x] Confirm that files can still be reconstructed from indexed chunks, even with modified source files.
- [x] Multi-file support
    - [x] Preprocess multiple files for candidate chunks.
    - [x] Construct files that are a mixture of chunks from different files.