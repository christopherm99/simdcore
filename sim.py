import argparse, struct, sys, mmap, os
import numpy as np
from utils import save_memory_to_binary, hex_char_to_int, int_to_hex_char

def as_np(arr: bytearray) -> np.ndarray: return np.frombuffer(arr, dtype=np.int16)
def from_np(arr: np.ndarray) -> bytearray: return arr.tobytes()
def pack2(arg1: int, arg2: int) -> int: return arg1 << 8 | arg2
def pack3(arg1: int, arg2: int, arg3: int) -> int: return arg1 << 16 | arg2 << 8 | arg3
def extract_indices(arg1, arg2, arg3): return [((pack3(arg1, arg2, arg3)) >> (21 - (i*3))) & 0x7 for i in range(8)]
def initialize_memory(memory: bytearray, values) -> None: memory[base_addr:base_addr+len(values)*2] = from_np(np.array(values, dtype=np.int16))
def apply_func(func, *args) -> bytearray: return from_np(func(*[as_np(arg) for arg in args]))

def vadd(a: np.ndarray, b: np.ndarray) -> np.ndarray: return (a + b).astype(np.int16)
def vsub(a: np.ndarray, b: np.ndarray) -> np.ndarray: return (a - b).astype(np.int16)
def vmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
  tmp = (a.astype(np.int16) * b.astype(np.int16)) >> FRAC_BITS
  return np.clip(tmp, -32768, 32767).astype(np.int16)
def vneg(a: np.ndarray) -> np.ndarray: return (-a).astype(np.int16)
def vdiv(a: np.ndarray, b: np.ndarray) -> np.ndarray:
  tmp = (a.astype(np.int16) << FRAC_BITS) // b.astype(np.int16)
  return np.clip(tmp, -32768, 32767).astype(np.int16)

### bitwise operations ###
def vector_or(x, y): return np.bitwise_or(x.view(np.uint16), y.view(np.uint16)).view(np.uint16)
def vector_xor(x, y): return np.bitwise_xor(x.view(np.uint16), y.view(np.uint16)).view(np.uint16)
def vector_and(x, y): return np.bitwise_and(x.view(np.uint16), y.view(np.uint16)).view(np.uint16)
def vector_not(x): return np.bitwise_not(x.view(np.uint16)).view(np.uint16)
def greater(x, y): return np.where(x > y, np.uint16(0xFFFF), np.uint16(0))

SF = 0b00000001
ZF = 0b00000010
FRAC_BITS = 15
base_addr = 0x00
    
def get_flags(val: int) -> int:
  val &= 0xFFFF
  zf = ZF if val == 0 else 0
  sf = SF if val & 0x8000 else 0
  return zf | sf

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="SIMD Core Simulator")
  parser.add_argument("program", help="Program binary file to execute")
  parser.add_argument("result_register", help="Register to display after execution")
  parser.add_argument("--memory", help="Memory-mapped binary file containing all data")
  parser.add_argument("--output", help="Binary file to write output data")
  parser.add_argument('--output-size', type=int, default=8, help='Number of elements to display from output address')
  parser.add_argument('--output-addr', type=int, default=0x180, help='Memory address to read output from (default: 0x180)')
  args = parser.parse_args()

  output_addr = args.output_addr

  with open(sys.argv[1], 'rb') as f: data = f.read()

  pc = 0
  memory = bytearray(2 ** 16)
  sregs = [0] * 256
  vregs = [bytearray(16) for _ in range(256)]
  vperm = bytearray(16)
  flags = 0
  
  max_elements = 0
  
  if args.memory:
    with open(args.memory, 'rb') as f:
      memory_data = f.read()
      memory[:len(memory_data)] = memory_data
      print(f"Loaded memory from {args.memory} ({len(memory_data)} bytes)")
  else:
    values = [10, -10, 20, -30, 40, -50, 60, -70]
    initialize_memory(memory, values)
    max_elements = len(values)
  
  if args.memory:
    for addr in [0x00, 0x20, 0x40]:
      mem_data = as_np(memory[addr:addr+16]).tolist()
      if any(x != 0 for x in mem_data): 
        print(f"Initial Memory at 0x{addr:02x}:", mem_data)

  instr_count = len(data) // 4
  while pc < instr_count:
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
      case "00000", "111": as_np(vregs[arg1])[[(arg3 >> i) & 1 for i in range(8)]] = np.int16(sregs[arg2])
      case "00001", "000": sregs[arg1] = sregs[arg2] + sregs[arg3]
      case "00001", "001": sregs[arg1] = sregs[arg2] * sregs[arg3]
      case "00001", "010": sregs[arg1] = -sregs[arg2]
      case "00001", "011": sregs[arg1] = sregs[arg2] // sregs[arg3]
      case "00001", "100": sregs[arg1] = sregs[arg2] & sregs[arg3]
      case "00001", "101": sregs[arg1] = sregs[arg2] | sregs[arg3]
      case "00001", "110": sregs[arg1] = sregs[arg2] ^ sregs[arg3]
      case "00001", "111": sregs[arg1] = ~sregs[arg2]
      case "00010", "000": vregs[arg1] = apply_func(vadd, vregs[arg2], vregs[arg3])
      case "00010", "001": vregs[arg1] = apply_func(vmul, vregs[arg2], vregs[arg3])
      case "00010", "010": vregs[arg1] = apply_func(vneg, vregs[arg2])
      case "00010", "011": vregs[arg1] = apply_func(vdiv, vregs[arg2], vregs[arg3])
      case "00010", "100": vregs[arg1] = apply_func(vector_and, vregs[arg2], vregs[arg3])
      case "00010", "101": vregs[arg1] = apply_func(np.bitwise_or, vregs[arg2], vregs[arg3])
      case "00010", "110": vregs[arg1] = apply_func(np.bitwise_xor, vregs[arg2], vregs[arg3])
      case "00010", "111": vregs[arg1] = apply_func(np.bitwise_not, vregs[arg2])
      case "00011", "000": vregs[arg1] = apply_func(np.equal, vregs[arg2], vregs[arg3])
      case "00011", "001": vregs[arg1] = apply_func(greater, vregs[arg2], vregs[arg3])
      case "00100", "000": pc = pack2(arg1, arg2); continue
      case "00100", "001": 
        if flags & ZF: pc = pack2(arg1, arg2); continue
      case "00100", "010": 
        if not (flags & ZF): pc = pack2(arg1, arg2); continue
      case "00100", "011": 
        if (flags & SF) == 0 or (flags & ZF): pc = pack2(arg1, arg2); continue
      case "00100", "100": 
        if (flags & SF) or (flags & ZF): pc = pack2(arg1, arg2); continue
      case "00100", "101": 
        if (flags & SF) == 0 and not (flags & ZF): pc = pack2(arg1, arg2); continue
      case "00100", "110": 
        if flags & SF: pc = pack2(arg1, arg2); continue
      case "00100", "111": pc = sregs[arg1]; continue
      case "00101", "000": flags = get_flags(sregs[arg1] - sregs[arg2])
      case "00101", "001": flags = get_flags(sregs[arg1] - pack2(arg2, arg3))
      case "00101", "010": flags = get_flags(pack2(arg1, arg2) - sregs[arg3])
      case "00101", "011": flags = arg1 & (SF | ZF)
      case "00011", "100": vperm[:] = vregs[arg1][:]
      case "00011", "101": vregs[arg1][:] = vperm[:]
      case "00011", "010": 
        indices = extract_indices(arg1, arg2, arg3)
        src_values = as_np(vperm)
        result = np.zeros(8, dtype=np.int16)
        for i in range(8): result[indices[i]] = src_values[i]
        vperm[:] = from_np(result)
      case "00011", "011": 
        indices = extract_indices(arg1, arg2, arg3)
        src_values = as_np(vperm)
        result = np.zeros(8, dtype=np.int16)
        for i in range(8): result[i] = src_values[indices[i]]
        vperm[:] = from_np(result) 
      case "00110", "000": 
        while True:
          byte_val = sys.stdin.read(1)
          if byte_val and byte_val != '\n':
            val = hex_char_to_int(byte_val)
            sregs[arg1] = (sregs[arg1] & 0xFFF0) | (val & 0x0F)
            break
      case "00110", "001": 
        while True:
          byte_val = sys.stdin.read(1)
          if byte_val and byte_val != '\n':
            val = hex_char_to_int(byte_val)
            sregs[arg1] = (sregs[arg1] & 0xFF0F) | ((val & 0x0F) << 4)
            break
      case "00110", "010": 
        val = sregs[arg1] & 0xFF
        sys.stdout.write(f"{val:02X}")
        sys.stdout.write("\n")
        sys.stdout.flush()
      case "00110", "011": 
        val = (sregs[arg1] >> 8) & 0xFF
        sys.stdout.write(f"{val:02X}")
        sys.stdout.flush()
    pc += 1

  print(f"\nAfter Memory at 0x{output_addr:03x}:")
  output_size = args.output_size
  memory_data = as_np(memory[output_addr:output_addr+output_size*2]).tolist()
  print(memory_data)

  if args.memory:
    with open(args.memory, 'r+b') as f:
      f.seek(0)
      f.write(memory)
      print(f"Updated memory file: {args.memory}")

  result_reg = args.result_register.lower()
  if result_reg.startswith("v"):
    reg_index = int(result_reg[1:])
    reg_value = as_np(vregs[reg_index]).tolist()
    print(f"Register v{reg_index} value: {reg_value}")
  elif result_reg.startswith("s"):
    reg_index = int(result_reg[1:])
    print(f"Register s{reg_index} value: {sregs[reg_index]} (0x{sregs[reg_index]:04x})")