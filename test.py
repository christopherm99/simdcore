import os
import sys
import subprocess
import numpy as np
import ast

if len(sys.argv) < 2:
    print("Usage: python3 test.py <result_register>  (e.g. v2 or s4)")
    sys.exit(1)
result_reg = sys.argv[1]

simd_directory = os.path.expanduser('~/simdcore/simd_programs')
bin_directory = os.path.expanduser('~/simdcore/bin')
os.makedirs(bin_directory, exist_ok=True)

for root, _, files in os.walk(simd_directory):
    for file in files:
        if file.endswith('.s'):
            input_file = os.path.join(root, file)
            output_file = os.path.join(bin_directory, file.replace('.s', '.bin'))
            print(f"Running: ./simd as {input_file} {output_file}")
            subprocess.run(["./simd", "as", input_file, output_file])

### Test cases ###
def vector_add():
    x = np.array([0, 10, 20, 30, 40, 50, 60, 70], dtype=np.half)
    y = np.array([0, 10, 20, 30, 40, 50, 60, 70], dtype=np.half)
    return np.add(x, y, dtype=np.half)

def hadamard_prod():
    x = np.array([0, 10, 20, 30, 40, 50, 60, 70], dtype=np.half)
    y = np.array([0, 10, 20, 30, 40, 50, 60, 70], dtype=np.half)
    return np.multiply(x, y, dtype=np.half)

def reverse():
    x = np.array([70, 60, 50, 40, 30, 20, 10, 0], dtype=np.half)
    return np.flip(x)

def transpose():
    matrix = np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=np.half)
    indices = [0, 4, 1, 5, 2, 6, 3, 7]
    return np.array([matrix[i] for i in indices], dtype=np.half)


# make the name of the test case the same as the name of assembly program 
testcase_mapping = {
    "vector_add": np.array(vector_add()),
    "hadamard": np.array(hadamard_prod()),
    "reverse": np.array(reverse()),
    "transpose": np.array(transpose()),
}

print(f"Expected output for vector_add: {testcase_mapping['vector_add']}")
print(f"Expected output for hadamard: {testcase_mapping['hadamard']}")
print(f"Expected output for reverse: {testcase_mapping['reverse']}")
print(f"Expected output for transpose: {testcase_mapping['transpose']}")

bin_files = sorted([f for f in os.listdir(bin_directory) if f.endswith('.bin')])
passed = 0
for file in bin_files:
    prog_name = file.replace('.bin', '')
    test = testcase_mapping.get(prog_name)
    if test is None:
        print("No test case defined for", file)
        continue
    input_file = os.path.join(bin_directory, file)
    print(f"\nRunning sim.py {file} {result_reg}")
    output = subprocess.check_output(["python3", "sim.py", input_file, result_reg], universal_newlines=True).strip()
    print("Full Output:\n", output)
   
   # Parse the output to extract the register value 
    start_idx = output.find('[')
    end_idx = output.rfind(']')
    if start_idx == -1 or end_idx == -1:
        print("Could not find register value in output for", file)
        continue
    value_str = output[start_idx:end_idx+1]
    try:
        parsed_list = ast.literal_eval(value_str)
        result_reg_value = np.array(parsed_list)
    except Exception as e:
        print("Error parsing register value for", file, ":", e)
        continue
    
    # Compare the result with the expected value
    if np.array_equal(result_reg_value, test):
        print(f"Test PASSED for {file}")
        passed += 1
    else:
        print(f"Test FAILED for {file}")
        print("Expected:", test)
        print("Got     :", result_reg_value)
    
print(f"\n{passed}/{len(bin_files)} tests passed.")