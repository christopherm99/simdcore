import os
import sys
import subprocess
import numpy as np
import ast
from config import testcases_config
from utils import write_float16_to_binary, read_float16_from_binary

if len(sys.argv) < 2:
  print("Usage: python3 test.py <result_register>  (e.g. v2 or s4)")
  sys.exit(1)
result_reg = sys.argv[1]

simd_directory = os.path.expanduser('~/simdcore/simd_programs')
bin_directory = os.path.expanduser('~/simdcore/bin')
input_directory = os.path.expanduser('~/simdcore/input')
output_directory = os.path.expanduser('~/simdcore/output')
expected_directory = os.path.expanduser('~/simdcore/expected')

os.makedirs(bin_directory, exist_ok=True)
os.makedirs(input_directory, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)
os.makedirs(expected_directory, exist_ok=True)

for root, _, files in os.walk(simd_directory):
  for file in files:
    if file.endswith('.s'):
      input_file = os.path.join(root, file)
      output_file = os.path.join(bin_directory, file.replace('.s', '.bin'))
      #print(f"Running: ./simd as {input_file} {output_file}")
      subprocess.run(["./simd", "as", input_file, output_file])

### Test cases ###
def vector_add():
  x = testcases_config["vector_add"]["inputs"]["v0"]["data"]
  y = testcases_config["vector_add"]["inputs"]["v1"]["data"]
  return np.add(x, y, dtype=np.half)

def hadamard_prod():
  x = testcases_config["hadamard"]["inputs"]["v0"]["data"]
  y = testcases_config["hadamard"]["inputs"]["v1"]["data"]
  return np.multiply(x, y, dtype=np.half)

def reverse():
  x = testcases_config["reverse"]["inputs"]["v0"]["data"]
  return np.flip(x)

def transpose():
  matrix = testcases_config["transpose"]["inputs"]["v0"]["data"]
  indices = [0, 4, 1, 5, 2, 6, 3, 7]
  return np.array([matrix[i] for i in indices], dtype=np.half)

def relu():
  x = testcases_config["relu"]["inputs"]["v0"]["data"]
  return np.maximum(x, 0)

def mse():
  x = testcases_config["mse"]["inputs"]["v0"]["data"]
  y = testcases_config["mse"]["inputs"]["v1"]["data"]
  mse = np.mean(np.square(x - y), dtype=np.half)
  return np.full(8, mse, dtype=np.half)

def sigmoid():
  x = testcases_config["sigmoid"]["inputs"]["v0"]["data"]
  return 1 / (1 + np.exp(-x))

def inner_product():
  x = testcases_config["inner_product"]["inputs"]["v0"]["data"]
  y = testcases_config["inner_product"]["inputs"]["v1"]["data"]
  inner_product = np.sum(np.multiply(x, y), dtype=np.half)
  return np.full(8, inner_product, dtype=np.half)

def matmul():
	a = testcases_config["matmul"]["inputs"]["matrix_a"]["data"]
	b = testcases_config["matmul"]["inputs"]["matrix_b"]["data"]
	result = np.matmul(a, b).astype(np.half)
	return result

# make the name of the test case the same as the name of assembly program 
testcase_mapping = {
  "vector_add": np.array(vector_add()),
  "hadamard": np.array(hadamard_prod()),
  "reverse": np.array(reverse()),
  "transpose": np.array(transpose()),
  "relu": np.array(relu()),
  "mse": np.array(mse()),
  "sigmoid": np.array(sigmoid()),
  "inner_product": np.array(inner_product()),
#  "matmul": np.array(matmul())
}

for prog_name, config in testcases_config.items():
  for vec_name, vec_info in config["inputs"].items():
    input_file = os.path.join(input_directory, f"{prog_name}_{vec_name}_{vec_info['addr']:04x}_input.bin")
    write_float16_to_binary(vec_info["data"], input_file)
    #print(f"Input file created: {input_file}")

  expected_output = testcase_mapping.get(prog_name)
  if expected_output is not None:
    expected_file = os.path.join(expected_directory, f"{prog_name}_expected.bin")
    write_float16_to_binary(expected_output, expected_file)

bin_files = sorted([f for f in os.listdir(bin_directory) if f.endswith('.bin')])
passed = 0
for file in bin_files:
  prog_name = file.replace('.bin', '')
  test = testcase_mapping.get(prog_name)
  
  # Check if test exists
  test = testcase_mapping.get(prog_name)
  if test is None:
      print(f"WARNING: No test case defined for {file}")
      continue
  
  # Check if config exists
  if prog_name not in testcases_config:
      print(f"WARNING: No configuration defined for {file}")
      continue
      
  program_bin = os.path.join(bin_directory, file)
  output_bin = os.path.join(output_directory, f"{prog_name}_output.bin")
    
  cmd = ["python3", "sim.py", program_bin, result_reg, "--output", output_bin]
  
  config = testcases_config[prog_name]
  for vec_name, vec_info in config["inputs"].items():
    input_file = os.path.join(input_directory, f"{prog_name}_{vec_name}_{vec_info['addr']:04x}_input.bin")
    if os.path.exists(input_file):
      cmd.extend([f"--input", input_file, f"--addr", str(vec_info['addr'])])
    
  print(f"\n### Running test {prog_name} ###")
  try:
    subprocess.run(cmd, check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error running sim.py: {e}")
    continue
    
  if os.path.exists(output_bin):
    actual_output = read_float16_from_binary(output_bin)
    if np.array_equal(actual_output, test):
      print(f"Test PASSED for {file}")
      passed += 1
    else:
      print(f"Test FAILED for {file}")
      print("Expected:", test)
      print("Got     :", actual_output)
  else:
    print(f"Output file not created: {output_bin}")
  
print(f"\n{passed}/{len(bin_files)} tests passed.")