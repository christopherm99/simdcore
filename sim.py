import argparse, struct, sys
import numpy as np
from utils import load_memory_from_binary_at_address, save_memory_to_binary, hex_char_to_int, int_to_hex_char

def as_np(arr: bytearray) -> np.ndarray: return np.frombuffer(arr, dtype=np.half)
def from_np(arr: np.ndarray) -> bytearray: return arr.tobytes()
def apply_func(func, *args) -> bytearray: return from_np(func(*[as_np(arg) for arg in args]))
def pack2(arg1: int, arg2: int) -> int: return arg1 << 8 | arg2
def pack3(arg1: int, arg2: int, arg3: int) -> int: return arg1 << 16 | arg2 << 8 | arg3
def extract_indices(arg1, arg2, arg3): return [((pack3(arg1, arg2, arg3)) >> (21 - (i*3))) & 0x7 for i in range(8)]
def initialize_memory(memory: bytearray, values) -> None: memory[base_addr:base_addr+len(values)*2] = from_np(np.array(values, dtype=np.half))

### bitwise operations ###
def vector_or(x, y): return np.bitwise_or(x.view(np.uint16), y.view(np.uint16)).view(np.half)
def vector_xor(x, y): return np.bitwise_xor(x.view(np.uint16), y.view(np.uint16)).view(np.half)
def vector_and(x, y): return np.bitwise_and(x.view(np.uint16), y.view(np.uint16)).view(np.half)
def vector_not(x): return np.bitwise_not(x.view(np.uint16)).view(np.half)
def greater(x, y): return np.where(x > y, np.uint16(0xFFFF), np.uint16(0))
#def less(x, y): return np.where(x < y, np.uint16(0xFFFF), np.uint16(0))


SF = 0b00000001
ZF = 0b00000010
base_addr = 0x00
output_addr = 0x80
    
def get_flags(val: int) -> int:
  val &= 0xFFFF
  zf = ZF if val == 0 else 0
  sf = SF if val & 0x8000 else 0
  return zf | sf

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="SIMD Core Simulator")
  parser.add_argument("program", help="Program binary file to execute")
  parser.add_argument("result_register", help="Register to display after execution")
  parser.add_argument("--output", help="Binary file to write output data")
  parser.add_argument("--input", action='append', help="Binary file containing input data")
  parser.add_argument("--addr", action='append', type=int, help="Memory address for input data")
  args = parser.parse_args()

  with open(sys.argv[1], 'rb') as f: data = f.read()

  pc = 0
  memory = bytearray(2 ** 16)
  sregs = [0] * 256
  vregs = [bytearray(16) for _ in range(256)]
  vperm = bytearray(16)
  flags = 0
  
  max_elements = 0
  if args.input and args.addr:
    for input_file, address in zip(args.input, args.addr):
      num_elements = load_memory_from_binary_at_address(input_file, memory, address)
      max_elements = max(max_elements, num_elements)
      #print(f"Loaded input at address 0x{address:04x}")
  else:
    values = [10, -10, 20, -30, 40, -50, 60, -70]
    initialize_memory(memory, values)
    max_elements = len(values)
    
  for addr in args.addr if args.addr else [base_addr]:
    print(f"Initial Memory at 0x{addr:02x}:", as_np(memory[addr:addr+max_elements*2]).tolist())
  instr_count = len(data) // 4
  while pc < instr_count:
  # for (opcode, arg1, arg2, arg3) in [struct.unpack("BBBB", b) for b in [data[i:i+4] for i in range(0, len(data), 4)]]:
  # PC * 4 : PC * 4 + 4
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
        for i in range(16): vregs[arg1][(i*2):(i*2)+2] = from_np(np.half(sregs[arg2])) if (arg3 >> i) & 1 else vregs[arg1][(i*2):(i*2)+2]
      case "00001", "000": sregs[arg1] = sregs[arg2] + sregs[arg3]
      case "00001", "001": sregs[arg1] = sregs[arg2] * sregs[arg3]
      case "00001", "010": sregs[arg1] = -sregs[arg2]
      case "00001", "011": sregs[arg1] = sregs[arg2] // sregs[arg3] # Need to set a flag for div by zero.
      case "00001", "100": sregs[arg1] = sregs[arg2] & sregs[arg3]
      case "00001", "101": sregs[arg1] = sregs[arg2] | sregs[arg3]
      case "00001", "110": sregs[arg1] = sregs[arg2] ^ sregs[arg3]
      case "00001", "111": sregs[arg1] = ~sregs[arg2]
      case "00010", "000": vregs[arg1] = apply_func(np.add, vregs[arg2], vregs[arg3])
      case "00010", "001": vregs[arg1] = apply_func(np.multiply, vregs[arg2], vregs[arg3])
      case "00010", "010": vregs[arg1] = apply_func(np.negative, vregs[arg2])
      case "00010", "011": vregs[arg1] = apply_func(np.divide, vregs[arg2], vregs[arg3]) # Need to set a flag for div by zero.
      case "00010", "100": vregs[arg1] = apply_func(vector_and, vregs[arg2], vregs[arg3])
      case "00010", "101": vregs[arg1] = apply_func(np.bitwise_or, vregs[arg2], vregs[arg3])
      case "00010", "110": vregs[arg1] = apply_func(np.bitwise_xor, vregs[arg2], vregs[arg3])
      case "00010", "111": vregs[arg1] = apply_func(np.bitwise_not, vregs[arg2])
      case "00011", "000": vregs[arg1] = apply_func(np.equal, vregs[arg2], vregs[arg3])
      case "00011", "001": vregs[arg1] = apply_func(greater, vregs[arg2], vregs[arg3])
      case "00100", "000": # J (unconditional)
        pc = pack2(arg1, arg2)
        continue
      case "00100", "001": # JE
        if flags & ZF: 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "010": # JNE
        if not (flags & ZF): 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "011": # JGE
        if (flags & SF) == 0 or (flags & ZF): 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "100": # JLE
        if (flags & SF) or (flags & ZF): 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "101": # JGT
        if (flags & SF) == 0 and not (flags & ZF): 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "110": # JLT
        if flags & SF: 
          pc = pack2(arg1, arg2)
          continue
      case "00100", "111": # JR
        pc = sregs[arg1]
        continue
      case "00101", "000": flags = get_flags(sregs[arg1] - sregs[arg2])
      case "00101", "001": flags = get_flags(sregs[arg1] - pack2(arg2, arg3))
      case "00101", "010": flags = get_flags(pack2(arg1, arg2) - sregs[arg3])
      case "00101", "011": flags = arg1 & (SF | ZF)
      case "00011", "100": # load vperm
        vperm[:] = vregs[arg1][:]
        #print("vperm loaded:", as_np(vperm).tolist())
      case "00011", "101":  # store vperm
        vregs[arg1][:] = vperm[:]
        #print("vperm stored:", as_np(vregs[arg1]).tolist())
      case "00011", "010": # scatter
        indices = extract_indices(arg1, arg2, arg3)
        src_values = as_np(vperm)
        result = np.zeros(8, dtype=np.half)
        for i in range(8): result[indices[i]] = src_values[i]
        vperm[:] = from_np(result)
      case "00011", "011": # gather
        indices = extract_indices(arg1, arg2, arg3)
        src_values = as_np(vperm)
        result = np.zeros(8, dtype=np.half)
        for i in range(8): result[i] = src_values[indices[i]]
        vperm[:] = from_np(result) 
      case "00110", "000": # inl
        while True:
          byte_val = sys.stdin.read(1)
          if byte_val and byte_val != '\n':
            val = hex_char_to_int(byte_val)
            sregs[arg1] = (sregs[arg1] & 0xFFF0) | (val & 0x0F)
            break
      case "00110", "001": # inh
        while True:
          byte_val = sys.stdin.read(1)
          if byte_val and byte_val != '\n':
            val = hex_char_to_int(byte_val)
            sregs[arg1] = (sregs[arg1] & 0xFF0F) | ((val & 0x0F) << 4)
            break
      case "00110", "010": # outl 
        val = sregs[arg1] & 0xFF
        sys.stdout.write(f"{val:02X}")
        sys.stdout.write("\n")
        sys.stdout.flush()
      case "00110", "011": # outh 
        val = (sregs[arg1] >> 8) & 0xFF
        sys.stdout.write(f"{val:02X}")
        sys.stdout.flush()
    pc += 1

  print("\nAfter Memory at 0x80:", as_np(memory[output_addr:output_addr+max_elements*2]).tolist())
  if args.output:
    save_memory_to_binary(args.output, memory[output_addr:output_addr+max_elements*2])

result_reg = args.result_register.lower()
if result_reg.startswith("v"):
  reg_index = int(result_reg[1:])
  reg_value = as_np(vregs[reg_index]).tolist()
  print(f"Register v{reg_index} value: {reg_value}")
elif result_reg.startswith("s"):
  reg_index = int(result_reg[1:])
  print(f"Register s{reg_index} value: {sregs[reg_index]} (0x{sregs[reg_index]:04x})")



