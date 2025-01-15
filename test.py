import random
def block_randomization(treatments, block_size, num_blocks):
    """``
    Perform block randomization for a clinical trial.
    Args:
    treatments (list): List of treatments (e.g., ["A", "B"]).
    block_size (int): Size of each block; must be a multiple of the number of treatments.
    num_blocks (int): Number of blocks to generate.
    Returns:
    list: A randomized list of treatment assignments.
    """
    if block_size % len(treatments) != 0:
        raise ValueError("Block size must be a multiple of the number of treatments.")
    # Generate one block of each treatment combination
    block_template = treatments * (block_size // len(treatments))
    randomization_list = []
    # Shuffle and append to the final list for the desired number of blocks
    for _ in range(num_blocks):
        block = block_template[:]
        random.shuffle(block)
        randomization_list.extend(block)
    return randomization_list
# Example usage:
if __name__ == "__main__":
    treatments = ["A", "B"] # Treatment A and B
    block_size = 4 # Each block contains 4 assignments
    num_blocks = 5 # Number of blocks needed
    result = block_randomization(treatments, block_size, num_blocks)
    print(result)