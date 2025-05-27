import numpy as np

def as_np(arr: bytearray) -> np.ndarray: return np.frombuffer(arr, dtype=np.half)
def from_np(arr: np.ndarray) -> bytearray: return arr.tobytes()
def write_float16_to_binary(array, filename): open(filename, 'wb').write(array.tobytes())
def read_float16_from_binary(filename, count=None): return np.fromfile(filename, dtype=np.half)[:count] if count else np.fromfile(filename, dtype=np.half)
def save_memory_to_binary(filename, memory, count=None): np.frombuffer(memory[:count*2 if count else len(memory)], dtype=np.half).tofile(filename)
def load_memory_from_binary_at_address(filename, memory, address):
	array = np.frombuffer(open(filename, 'rb').read(), dtype=np.half)
	memory_bytes = from_np(array)
	memory[address:address+len(memory_bytes)] = memory_bytes[:min(len(memory_bytes), len(memory) - address)]
	return len(array)
def hex_char_to_int(char):
    if '0' <= char <= '9':
        return ord(char) - ord('0')
    elif 'A' <= char <= 'F':
        return ord(char) - ord('A') + 10
    elif 'a' <= char <= 'f':
        return ord(char) - ord('a') + 10
    else:
        return 0
def int_to_hex_char(val):
    if 0 <= val <= 9:
        return chr(ord('0') + val)
    elif 10 <= val <= 15:
        return chr(ord('A') + val - 10)
    else:
        return '0'
