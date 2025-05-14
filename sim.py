import struct, sys
import numpy as np

def as_np(arr: bytearray) -> np.ndarray: return np.frombuffer(arr, dtype=np.half)
def from_np(arr: np.ndarray) -> bytearray: return arr.tobytes()
def apply_func(func, *args) -> bytearray: return from_np(func(*[as_np(arg) for arg in args]))
def pack2(arg1: int, arg2: int) -> int: return arg1 << 8 | arg2

SF = 0b00000001
ZF = 0b00000010

def get_flags(val:int) -> int: return ((val == 0x00 & ZF) | (val & 0x8000 & SF))

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python sim2.py <input_file>")
    sys.exit(1)

  with open(sys.argv[1], 'rb') as f: data = f.read()

  pc = 0
  memory = bytearray(2 ** 16)
  sregs = [0] * 256
  vregs = [bytearray(16) for _ in range(256)]
  flags = 0

  while True:
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
      case "00010", "100": vregs[arg1] = apply_func(np.bitwise_and, vregs[arg2], vregs[arg3])
      case "00010", "101": vregs[arg1] = apply_func(np.bitwise_or, vregs[arg2], vregs[arg3])
      case "00010", "110": vregs[arg1] = apply_func(np.bitwise_xor, vregs[arg2], vregs[arg3])
      case "00010", "111": vregs[arg1] = apply_func(np.bitwise_not, vregs[arg2])
      case "00100", "000": # J (unconditional)
        pc = pack2(arg1, arg2)
        continue
      case "00100", "001": # JE (ZF == 1)
        if flags & ZF: pc = pack2(arg1, arg2)
        continue
      case "00100", "010": # JNE (ZF == 0)
        if not (flags & ZF): pc = pack2(arg1, arg2)
        continue
      case "00100", "011": # JGE (SF == 0 | ZF == 1)
        if (~(flags & SF)) | (flags & ZF): pc = pack2(arg1, arg2)
        continue
      case "00100", "100": # JLE (SF == 1 | ZF == 1)
        if (flags & SF) | (flags & ZF): pc = pack2(arg1, arg2)
        continue
      case "00100", "101": # JGT (SF == 0 & ZF == 0)
        if not (flags & SF) & (flags & ZF): pc = pack2(arg1, arg2)
        continue
      case "00100", "110": # JLT (SF == 1)
        if flags & SF: pc = pack2(arg1, arg2)
        continue
      case "00101", "000": flags = get_flags(sregs[arg1] - sregs[arg2])
      case "00101", "001": flags = get_flags(sregs[arg1] - pack2(arg2, arg3))
      case "00101", "010": flags = get_flags(pack2(arg1, arg2) - sregs[arg3])
      case "00101", "011": flags = arg1 & (SF | ZF)
    pc += 1

    if pc >= 0xf: break
  print("Sregs:")
  for i in range(5):
    print(f"s{i:2}: {sregs[i]:4}")
  print("Vregs:")
  for i in range(5):
    print(f"v{i:2}: {as_np(vregs[i])}")



