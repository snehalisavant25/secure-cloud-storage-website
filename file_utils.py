import os

BLOCK_SIZE = 1024 * 1024

def split_file(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    blocks = []

    with open(file_path, "rb") as f:
        index = 0
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break

            block_path = os.path.join(output_dir, f"block_{index:04d}.bin")
            with open(block_path, "wb") as block:
                block.write(data)

            blocks.append(block_path)
            index += 1

    return blocks

def reconstruct_file(block_paths, output_path):
    with open(output_path, "wb") as output:
        for block_path in block_paths:
            with open(block_path, "rb") as block:
                output.write(block.read())

    return output_path