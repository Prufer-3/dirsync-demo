# dirsync-demo

This is a demo of the file chunking functionality described in the design document, written in Python.
It's not reflective of how it might look in the actual system, since the synchronisation protocol hasn't been implemented. Instead, it serves to demonstrate the effectiveness of cached chunks in reducing bandwidth requirements.

Milestones:
- [x] Fixed-size chunks at boundary intervals
    - [x] Ingest small files and break them into fixed-size chunks.
    - [x] Hash each chunk and store in a database.
    - [x] Lookup chunk metadata by hash and retrieve from file system.
- [ ] Reconstructing files with chunks from the same file
    - [ ] Implement functionality to report statistics on chunk matches between files.
    - [ ] Iteratively reconstruct files (and slightly modified files) with preprocessed chunks.
    - [ ] Verify integrity of reconstructed files with a full file hash.
- [ ] Fixed-size chunks at all offsets
    - [ ] Start with brute force by reading each chunk and hashing individually.
    - [ ] Implement a rolling hash with Rabin fingerprinting.
    - [ ] Add timing reports for both approaches.
    - [ ] Check that files are still reconstructed correctly.
- [ ] Multi-file support
    - [ ] Preprocess multiple files for candidate chunks.
    - [ ] Construct files that are a mixture of chunks from different files.
- [ ] Variable-size chunks with content-defined chunking
    - [ ] Add a mask heuristic along with chunk size limits to the Rabin fingerprinting rolling hash scheme.
    - [ ] Create a separate database for variable-size chunks.
    - [ ] Compare index size and performance against fixed-size approach.