from abc import ABC, abstractmethod
from dataclasses import dataclass

"""
total bit encodings: 28

transposition - 28 possibilities

Code 0x0 represents no swap
Code 0x1 represents swap (0, 1)
Code 0x2 represents swap (0, 2)
Code 0x3 represents swap (0, 3)
Code 0x4 represents swap (0, 4)
Code 0x5 represents swap (0, 5)
Code 0x6 represents swap (0, 6)
Code 0x7 represents swap (0, 7)
Code 0x8 represents swap (1, 2)
Code 0x9 represents swap (1, 3)
Code 0xa represents swap (1, 4)
Code 0xb represents swap (1, 5)
Code 0xc represents swap (1, 6)
Code 0xd represents swap (1, 7)
Code 0xf represents swap (2, 3)
Code 0x10 represents swap (2, 4)
Code 0x11 represents swap (2, 5)
Code 0x12 represents swap (2, 6)
Code 0x13 represents swap (2, 7)
Code 0x16 represents swap (3, 4)
Code 0x17 represents swap (3, 5)
Code 0x18 represents swap (3, 6)
Code 0x19 represents swap (3, 7)
Code 0x1d represents swap (4, 5)
Code 0x1e represents swap (4, 6)
Code 0x1f represents swap (4, 7)
Code 0x24 represents swap (5, 6)
Code 0x25 represents swap (5, 7)
Code 0x2b represents swap (6, 7)
"""

def enc(i: str) -> list[int]:
    """
    Input: "E.g., "0 1 2 3 4 5 6 7" or "1 2 3 4 0 5 6 7"
    Output: A list of integers representing the swap operations needed to sort the permutation. 
    """

    perm = [int(x) for x in i.split()]
    
    if perm == list(range(8)):
        return [0x00]
    
    result = []
    target = list(range(8))
    current = perm.copy()
   
    # solver: swap until we reach the identity permutation
    while current != target:
        for i in range(8):
            if current[i] != target[i]:
                j = current.index(target[i])
                
                swap_code = encode_swap(i, j)
                result.append(swap_code)
                
                current[i], current[j] = current[j], current[i]
                break
    
    return result

def encode_swap(i: int, j: int) -> int:
    if i > j:
        i, j = j, i
    
    code = 0x01 + (i * 7) + (j - i - 1)
    return code

def dec(codes: list[int]) -> str:
    """
    Input: A list of integers representing swap operations.
    Output: "E.g., "0 1 2 3 4 5 6 7" or "1 2 3 4 0 5 6 7"
    """
    perm = list(range(8))
    
    if codes == [0x00]:
        return " ".join(str(x) for x in perm)
    
    for code in codes:
        if code == 0x00:
            continue
        
        i, j = decode_swap(code)
        
        perm[i], perm[j] = perm[j], perm[i]
    
    return " ".join(str(x) for x in perm)

def decode_swap(code: int) -> tuple[int, int]:
    code_idx = code - 0x01
    
    i = code_idx // 7
    j = i + 1 + (code_idx % 7)
    
    return (i, j)

def create_swap_table():
    table = {}
    for i in range(8):
        for j in range(i+1, 8):
            code = encode_swap(i, j)
            table[code] = (i, j)
    return table

swap_table = create_swap_table()
print("Swap table:")
print(len(swap_table))
for code, (i, j) in swap_table.items():
    print(f"Code {hex(code)} represents swap ({i}, {j})")




