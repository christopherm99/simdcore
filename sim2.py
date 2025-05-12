import struct, sys
import numpy as np

def as_np(arr: bytearray, dtype:np.dtype) -> np.ndarray: return np.frombuffer(arr, dtype=dtype)
def from_np(arr: np.ndarray) -> bytearray: return arr.tobytes()
def apply_func(func, *args) -> bytearray: return from_np(func(*[as_np(arg, np.half) for arg in args]))
def extract_indices(arg1, arg2, arg3): return [(((arg1 << 16) | (arg2 << 8) | arg3) >> (21 - (i*3))) & 0x7 for i in range(8)]

if __name__ == "__main__":
  with open(sys.argv[1], 'rb') as f: data = f.read()
  pc = 0
  memory = bytearray(2 ** 16)
  sregs = [0] * 256
  vregs = [bytearray(16) for _ in range(255)]
  vperm = bytearray(16)
  
  while pc * 4 < len(data):
      opcode, arg1, arg2, arg3 = struct.unpack("BBBB", data[pc * 4:(pc * 4) + 4])
      op = bin(opcode)[2:].zfill(8)
      
      match op[:5], op[5:]:
          case "00000", "000": sregs[arg1] = sregs[arg2]
          case "00000", "001": sregs[arg1] = memory[sregs[arg2] + arg3] << 8 | memory[sregs[arg2] + arg3 + 1]
          case "00000", "010":
              memory[sregs[arg1] + arg2] = sregs[arg3] >> 8
              memory[sregs[arg1] + arg2 + 1] = sregs[arg3] & 0xFF
          case "00000", "011": sregs[arg1] = arg2 << 8 | arg3
          case "00000", "100": vregs[arg1][:] = vregs[arg2]
          case "00000", "101":
              for i in range(16): vregs[arg1][i] = memory[sregs[arg2] + arg3 + i]
          case "00000", "110":
              for i in range(16): memory[sregs[arg1] + arg2 + i] = vregs[arg3][i]
          case "00000", "111":
              mask = arg3
              for i in range(8):
                  if (mask >> i) & 1:
                      vregs[arg1][(i*2):(i*2)+2] = from_np(np.array([sregs[arg2]], dtype=np.half))
          case "00001", "000": sregs[arg1] = sregs[arg2] + sregs[arg3]
          case "00001", "001": sregs[arg1] = sregs[arg2] * sregs[arg3]
          case "00001", "010": sregs[arg1] = -sregs[arg2]
          case "00001", "011": sregs[arg1] = sregs[arg2] // sregs[arg3]
          case "00001", "100": sregs[arg1] = sregs[arg2] & sregs[arg3]
          case "00001", "101": sregs[arg1] = sregs[arg2] | sregs[arg3]
          case "00001", "110": sregs[arg1] = sregs[arg2] ^ sregs[arg3]
          case "00001", "111": sregs[arg1] = ~sregs[arg2]
          case "00010", "000": vregs[arg1] = apply_func(np.add, vregs[arg2], vregs[arg3])
          case "00010", "001": vregs[arg1] = apply_func(np.multiply, vregs[arg2], vregs[arg3])
          case "00010", "010": vregs[arg1] = apply_func(np.negative, vregs[arg2])
          case "00010", "011": vregs[arg1] = apply_func(np.divide, vregs[arg2], vregs[arg3])
          case "00010", "100": vregs[arg1] = apply_func(np.bitwise_and, vregs[arg2], vregs[arg3])
          case "00010", "101": vregs[arg1] = apply_func(np.bitwise_or, vregs[arg2], vregs[arg3])
          case "00010", "110": vregs[arg1] = apply_func(np.bitwise_xor, vregs[arg2], vregs[arg3])
          case "00010", "111": vregs[arg1] = apply_func(np.bitwise_not, vregs[arg2])
          case "00011", "010": vperm[:] = vregs[arg1][:]
          case "00011", "011": vregs[arg1][:] = vperm[:]
          case "00011", "000":
              indices = extract_indices(arg1, arg2, arg3)
              print(f"  Scatter with indices: {indices}")
              src_values = as_np(vperm, np.half)
              print(f"  Source values: {src_values}")
              result = np.zeros(8, dtype=np.half)
              for i in range(8): result[indices[i]] = src_values[i]
              vperm[:] = from_np(result)
              print(f"  Result after scatter: {as_np(vperm, np.half)}")
          case "00011", "001":
              indices = extract_indices(arg1, arg2, arg3)
              print(f"  Gather with indices: {indices}")
              src_values = as_np(vperm, np.half)
              print(f"  Source values: {src_values}")
              result = np.zeros(8, dtype=np.half)
              for i in range(8): result[i] = src_values[indices[i]]
              vperm[:] = from_np(result)
              print(f"  Result after gather: {as_np(vperm, np.half)}")    
      pc += 1
  
  print("\nVregs:")
  print(f"vperm: {as_np(vperm, np.half)}")