def rabin_karp_chunks(
        data: bytes,
        min_chunk_size = 2 * 1024, # 2KiB
        max_chunk_size = 64 * 1024, # 64KiB
        target_chunk_size = 8 * 1024 # 8KiB
    ):
    """
    Splits data into variable-sized chunks based on content.

    min/max_chunk_size are self explanatory.
    
    target_chunk_size allows the user to specify a desired average chunk size.
        Must be a power of 2 to ensure a correct heuristic due to how bitmasking works.

        Assuming the rolling hash is reasonably uniformly distributed,
        the heuristic (hash & mask) == 0 with mask = target_chunk_size - 1
        has a probability of roughly 1/target_chunk_size to hit a boundary.
    """

    window_size = 48
    mask =  target_chunk_size - 1
    base = 257
    m = 2**31-1

    # Used to remove the first/outgoing byte from the hash
    degree = pow(base, window_size - 1, m)
    rolling_hash = 0
    chunk_start = 0

    for i, curr_byte in enumerate(data):
        if i < window_size:
            rolling_hash = (rolling_hash * base + curr_byte) % m
            continue

        outgoing_byte = data[i - window_size]
        rolling_hash = (rolling_hash - outgoing_byte * degree) % m
        rolling_hash = (rolling_hash * base + curr_byte) % m

        chunk_size = i - chunk_start + 1

        boundary_hit = (chunk_size >= min_chunk_size and (rolling_hash & mask) == 0)
        if chunk_size >= max_chunk_size or boundary_hit:
            yield (
                chunk_start,
                data[chunk_start:i + 1]
            )
            chunk_start = i + 1
    if chunk_start < len(data):
        yield (
            chunk_start,
            data[chunk_start:]
        )