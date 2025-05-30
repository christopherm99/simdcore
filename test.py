import os
import sys
import subprocess
import numpy as np
import mmap
from config import testcases_config
from utils import write_float16_to_binary

if len(sys.argv) < 2:
  print("Usage: python3 test.py <result_register>  (e.g. v2 or s4)")
  sys.exit(1)
result_reg = sys.argv[1]

simd_directory = os.path.expanduser('~/simdcore/simd_programs')
bin_directory = os.path.expanduser('~/simdcore/bin')
memory_directory = os.path.expanduser('~/simdcore/memory')
expected_directory = os.path.expanduser('~/simdcore/expected')

os.makedirs(bin_directory, exist_ok=True)
os.makedirs(memory_directory, exist_ok=True)
os.makedirs(expected_directory, exist_ok=True)

for root, _, files in os.walk(simd_directory):
  for file in files:
    if file.endswith('.s'):
      input_file = os.path.join(root, file)
      output_file = os.path.join(bin_directory, file.replace('.s', '.bin'))
      subprocess.run(["./simd", "as", input_file, output_file])

### Test cases ###
def vector_add():
  x = testcases_config["vector_add"]["inputs"]["v0"]["data"]
  y = testcases_config["vector_add"]["inputs"]["v1"]["data"]
  return x + y

def hadamard_prod():
  x = testcases_config["hadamard"]["inputs"]["v0"]["data"]
  y = testcases_config["hadamard"]["inputs"]["v1"]["data"]
  result = np.array([(a * b) >> 15 for a, b in zip(x, y)], dtype=np.int16)
  return result

def reverse():
  x = testcases_config["reverse"]["inputs"]["v0"]["data"]
  return np.flip(x)

def transpose():
  matrix = testcases_config["transpose"]["inputs"]["v0"]["data"]
  indices = [0, 4, 1, 5, 2, 6, 3, 7]
  return np.array([matrix[i] for i in indices], dtype=np.int16)

def relu():
  x = testcases_config["relu"]["inputs"]["v0"]["data"]
  return np.maximum(x, 0)

def mse():
  x = testcases_config["mse"]["inputs"]["v0"]["data"]
  y = testcases_config["mse"]["inputs"]["v1"]["data"]
  diff = x - y
  squared_diff = np.array([(d * d) >> 15 for d in diff], dtype=np.int16)
  mse_val = np.mean(squared_diff)
  return np.full(8, mse_val, dtype=np.int16)

def inner_product():
  x = testcases_config["inner_product"]["inputs"]["v0"]["data"]
  y = testcases_config["inner_product"]["inputs"]["v1"]["data"]
  inner_product = np.sum([(a * b) >> 15 for a, b in zip(x, y)], dtype=np.int32)
  return np.full(8, inner_product, dtype=np.int16)

def matmul():
  a = testcases_config["matmul"]["inputs"]["matrix_a"]["data"]
  b = testcases_config["matmul"]["inputs"]["matrix_b"]["data"]
  result = np.matmul(a, b).astype(np.int16)
  return np.array(result).flatten() 

testcase_mapping = {
  "vector_add": np.array(vector_add()),
  "hadamard": np.array(hadamard_prod()),
  "reverse": np.array(reverse()),
  "transpose": np.array(transpose()),
  "relu": np.array(relu()),
  "mse": np.array(mse()),
  "inner_product": np.array(inner_product()),
  "matmul": np.array(matmul())
}

def create_memory_file(prog_name, config):
  """Create a memory-mapped file with test data at the correct addresses"""
  memory_size = 64 * 1024  # 64KB memory
  memory_file = os.path.join(memory_directory, f"{prog_name}_memory.bin")
  with open(memory_file, 'wb') as f:
    f.write(b'\x00' * memory_size)
  with open(memory_file, 'r+b') as f:
    with mmap.mmap(f.fileno(), 0) as mm:
      for vec_name, vec_info in config["inputs"].items():
        addr = vec_info['addr']
        data = vec_info['data']
        if data.ndim == 2:
          flat_data = data.flatten().astype(np.int16)
          data_bytes = flat_data.tobytes()
        else:
          data_bytes = data.astype(np.int16).tobytes()
        
        mm[addr:addr + len(data_bytes)] = data_bytes
        print(f"  Wrote {len(data_bytes)} bytes to address 0x{addr:04x} for {vec_name}")
  
  return memory_file

def read_result_from_memory(memory_file, output_addr, output_size):
  """Read test results directly from memory file"""
  with open(memory_file, 'rb') as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
      start_addr = output_addr
      end_addr = start_addr + (output_size * 2)  # 2 bytes per int16
      result_bytes = mm[start_addr:end_addr]
      return np.frombuffer(result_bytes, dtype=np.int16)

bin_files = sorted([f for f in os.listdir(bin_directory) if f.endswith('.bin')])
passed = 0

for file in bin_files:
  prog_name = file.replace('.bin', '')
  test = testcase_mapping.get(prog_name)
  
  if test is None:
      print(f"WARNING: No test case defined for {file}")
      continue
  
  if prog_name not in testcases_config:
      print(f"WARNING: No configuration defined for {file}")
      continue
      
  config = testcases_config[prog_name]
  output_size = config.get("output_size", 8)
  output_addr = config.get("output_addr", 0x80)
  
  print(f"\n### Running test {prog_name} ###")
  print(f"Output size: {output_size}, Output addr: 0x{output_addr:04x}")
  
  memory_file = create_memory_file(prog_name, config)
  
  program_bin = os.path.join(bin_directory, file)
  cmd = ["python3", "sim.py", program_bin, result_reg, 
         "--memory", memory_file,
         "--output-size", str(output_size),
         "--output-addr", str(output_addr)]
  
  try:
    subprocess.run(cmd, check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error running sim.py: {e}")
    continue
    
  actual_output = read_result_from_memory(memory_file, output_addr, output_size)

  if np.array_equal(actual_output, test):
    print(f"Test PASSED for {file}")
    passed += 1
  else:
    print(f"Test FAILED for {file}")
    print("Expected:", test)
    print("Got     :", actual_output)
    from utils import fixed_to_float
  #  print("Expected (float):", [fixed_to_float(x) for x in test])
  #  print("Got      (float):", [fixed_to_float(x) for x in actual_output])

print(f"\n{passed}/{len(bin_files)} tests passed.")