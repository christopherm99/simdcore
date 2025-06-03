import os
import sys
import subprocess
import numpy as np
import tempfile
import mmap
from config import testcases_config

def create_expected_binary_output(config, prog_name):
  expected_memory = bytearray(64 * 1024)
  output_addr = config["output_addr"]
  if prog_name == "vector_add":
    v0 = config["inputs"]["v0"]["data"]
    v1 = config["inputs"]["v1"]["data"]
    result = v0 + v1
  elif prog_name == "hadamard":
    v0 = config["inputs"]["v0"]["data"]
    v1 = config["inputs"]["v1"]["data"]
    result = v0 * v1
  elif prog_name == "transpose":
    v0 = config["inputs"]["v0"]["data"]
    indices = [0, 4, 1, 5, 2, 6, 3, 7]
    result = np.array([v0[i] for i in indices], dtype=np.int16)
  elif prog_name == "reverse":
    v0 = config["inputs"]["v0"]["data"]
    result = np.flip(v0)
  elif prog_name == "relu":
    v0 = config["inputs"]["v0"]["data"]
    result = np.maximum(v0, 0)
  elif prog_name == "mse":
    v0 = config["inputs"]["v0"]["data"]
    v1 = config["inputs"]["v1"]["data"]
    diff = v0 - v1
    result = np.divide(np.array([np.sum(diff * diff)], dtype=np.int16), 8)
  elif prog_name == "inner_product":
    v0 = config["inputs"]["v0"]["data"]
    v1 = config["inputs"]["v1"]["data"]
    result = np.array([np.dot(v0, v1)], dtype=np.int16)
  elif prog_name == "matmul":
    matrix_a = config["inputs"]["matrix_a"]["data"]
    matrix_b = config["inputs"]["matrix_b"]["data"]
    result_matrix = np.matmul(matrix_a, matrix_b).astype(np.int16)
    result = result_matrix.flatten()
  else:
    return None
  
  for i, value in enumerate(result):
    byte_addr = output_addr + (i * 2)
    if byte_addr + 1 < len(expected_memory):
      unsigned_value = int(value) & 0xFFFF
      expected_memory[byte_addr] = (unsigned_value >> 8) & 0xFF      # High byte
      expected_memory[byte_addr + 1] = unsigned_value & 0xFF         # Low byte
  
  return expected_memory

def create_memory_with_data(program_file, config):
  with open(program_file, 'rb') as f:
    program_data = f.read()
  memory = bytearray(64 * 1024)
  memory[:len(program_data)] = program_data

  for vec_name, vec_info in config["inputs"].items():
    addr = vec_info['addr']
    data = vec_info['data']
    if data.ndim == 2:
      flat_data = data.flatten().astype(np.int16)
    else:
      flat_data = data.astype(np.int16)
    for i, value in enumerate(flat_data):
      byte_addr = addr + (i * 2)
      if byte_addr + 1 < len(memory):
        unsigned_value = int(value) & 0xFFFF
        memory[byte_addr] = (unsigned_value >> 8) & 0xFF      # High byte
        memory[byte_addr + 1] = unsigned_value & 0xFF         # Low byte
  
  temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
  temp_file.write(memory)
  temp_file.close()
  
  return temp_file.name

def compare_memory_at_address(actual_memory_file, expected_memory, output_addr, output_size):
  try:
    with open(actual_memory_file, 'rb') as f:
      with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as actual_mm:
        start_byte = output_addr
        end_byte = output_addr + (output_size * 2) 
        if end_byte > len(actual_mm):
          print(f"    Error: Output address range exceeds file size")
          return False, None, None
        actual_bytes = actual_mm[start_byte:end_byte]
        expected_bytes = expected_memory[start_byte:end_byte]
        actual_values = []
        expected_values = []
        
        for i in range(0, len(actual_bytes), 2):
          if i + 1 < len(actual_bytes):
            actual_val = (actual_bytes[i] << 8) | actual_bytes[i + 1]
            expected_val = (expected_bytes[i] << 8) | expected_bytes[i + 1]
            if actual_val >= 0x8000:
              actual_val = actual_val - 0x10000
            if expected_val >= 0x8000:
              expected_val = expected_val - 0x10000
            actual_values.append(actual_val)
            expected_values.append(expected_val)
        
        match = actual_bytes == expected_bytes
        return match, np.array(actual_values), np.array(expected_values)
  except Exception as e:
    print(f"    Error comparing memory: {e}")
    return False, None, None

def assemble_programs():
  simd_directory = "simd_programs"
  bin_directory = "bin"
  os.makedirs(bin_directory, exist_ok=True)
  print("Assembling programs...")
  success = True
  source_dirs = ["."]
  if os.path.exists(simd_directory):
    source_dirs.append(simd_directory)
  
  for source_dir in source_dirs:
    if not os.path.exists(source_dir):
      continue
      
    for file in os.listdir(source_dir):
      if file.endswith('.s'):
        input_file = os.path.join(source_dir, file)
        output_file = os.path.join(bin_directory, file.replace('.s', '.o'))
        try:
          result = subprocess.run(["./simd", "as", input_file, output_file])
          print(f"Assembled {file} -> {output_file}")
        except subprocess.CalledProcessError as e:
          print(f"Failed to assemble {file}: {e}")
          success = False
        except FileNotFoundError:
          print("./simd assembler not found")
          success = False
          break
  if success:
    print(f"Successfully assembled programs from current directory and {simd_directory}/")
  return success

def run_tests():
  bin_directory = "bin"
  bin_files = sorted([f for f in os.listdir(bin_directory) if f.endswith('.o')])
  passed = 0
  total = 0

  print(f"\n=== Running Tests ===")
  for file in bin_files:
    prog_name = file.replace('.o', '')
    if prog_name not in testcases_config:
      print(f"\nWARNING: No test case defined for {prog_name}")
      continue
    config = testcases_config[prog_name]
    expected_memory = create_expected_binary_output(config, prog_name)
    if expected_memory is None:
      print(f"\nWARNING: No expected result defined for {prog_name}")
      continue
    total += 1
    print(f"\n### Testing {prog_name} ###")
    program_file = os.path.join(bin_directory, file)
    memory_file = create_memory_with_data(program_file, config)
    
    try:
      result = subprocess.run(["./sim", memory_file], capture_output=True, text=True, timeout=10)
      if result.returncode != 0:
        print(f"Simulator failed for {prog_name}")
        continue
      output_addr = config["output_addr"]
      output_size = config["output_size"]
      match, actual_values, expected_values = compare_memory_at_address(memory_file, expected_memory, output_addr, output_size)
      if actual_values is None or expected_values is None:
        continue
      print(f"  Expected: {expected_values}")
      print(f"  Got:      {actual_values}")
      print(f"  Memory address: 0x{output_addr:04x}")
      if match:
        print(f"Test PASSED for {prog_name}")
        passed += 1
      else:
        print(f"Test FAILED for {prog_name}")
    except Exception as e:
      print(f"Error running {prog_name}: {e}")
    finally:
      if os.path.exists(memory_file):
        os.unlink(memory_file)
  
  print(f"\n=== Test Results ===")
  print(f"{passed}/{total} tests passed.")

if __name__ == "__main__":
  run_tests()