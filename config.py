import numpy as np

testcases_config = {
	"vector_add": {
		"inputs": {
			"v0": {
				"data": np.array([0, -1, 2, -3, 4, -5, 6, -7], dtype=np.int16),
				"addr": 0x8000
			},
			"v1": {
				"data": np.array([0, 1, 0, 2, -1, 3, -2, 4], dtype=np.int16),
				"addr": 0x8020
			}
		},
		"output_addr": 0x8040,
		"output_size": 8,
		"result_register": "v2"
	},
	"hadamard": {
		"inputs": {
			"v0": {
				"data": np.array([2, -2, 1, -1, 5, -5, 0, 3], dtype=np.int16),
				"addr": 0x8000
			},
			"v1": {
				"data": np.array([5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int16),
				"addr": 0x8020
			}
		},
		"output_addr": 0x8040,
		"output_size": 8,
		"result_register": "v2"
	},
	"transpose": {
		"inputs": {
			"v0": {
				"data": np.array([1, -1, 2, -3, 4, -5, 6, -7], dtype=np.int16),
				"addr": 0x8000
			}
		},
		"output_addr": 0x8040,
		"output_size": 8,
		"result_register": "v1"
	},
	"reverse": {
		"inputs": {
			"v0": {
				"data": np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.int16),
				"addr": 0x8000
			}
		},
		"output_addr": 0x8020,
		"output_size": 8,
		"result_register": "v1"
	},
	"relu": {
		"inputs": {
			"v0": {
				"data": np.array([1, -1, 2, -3, 4, -5, 6, -7], dtype=np.int16),
				"addr": 0x8000
			}
		},
		"output_addr": 0x8020,
		"output_size": 8,
		"result_register": "v1"
	},
	"mse": {
		"inputs": {
			"v0": {
				"data": np.array([2, 4, 6, 8, 10, 12, 14, 16], dtype=np.int16),
				"addr": 0x8000
			},
			"v1": {
				"data": np.array([0, 2, 4, 6, 8, 10, 12, 14], dtype=np.int16),
				"addr": 0x8020
			}
		},
		"output_addr": 0x8040,
		"output_size": 1,
		"result_register": "s0"
	},
	"inner_product": {
		"inputs": {
			"v0": {
				"data": np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.int16),
				"addr": 0x8000
			},
			"v1": {
				"data": np.array([8, 7, 6, 5, 4, 3, 2, 1], dtype=np.int16),
				"addr": 0x8020
			}
		},
		"output_addr": 0x8040,
		"output_size": 1,
		"result_register": "s0"
	},
	"matmul": {
		"inputs": {
			"matrix_a": {
				"data": np.array([
					[1, 2, 3, 4, 5, 6, 7, 8],
					[0, 1, 0, 0, 0, 0, 0, 0],
					[0, 0, 1, 0, 0, 0, 0, 0],
					[0, 0, 0, 1, 0, 0, 0, 0],
					[0, 0, 0, 0, 1, 0, 0, 0],
					[0, 0, 0, 0, 0, 1, 0, 0],
					[0, 0, 0, 0, 0, 0, 1, 0],
					[0, 0, 0, 0, 0, 0, 0, 1]
				], dtype=np.int16),
				"addr": 0x8000
			},
			"matrix_b": {
				"data": np.array([
					[1, 2, 3, 4, 5, 6, 7, 8],
					[2, 3, 4, 5, 6, 7, 8, 9],
					[3, 4, 5, 6, 7, 8, 9, -9],  
					[4, 5, 6, 7, 8, 9, -9, -8],
					[5, 6, 7, 8, 9, -9, -8, -7],
					[6, 7, 8, 9, -9, -8, -7, -6],
					[7, 8, 9, -9, -8, -7, -6, -5],
					[8, 9, -9, -8, -7, -6, -5, -4]
				], dtype=np.int16),
				"addr": 0x8200
			}
		},
		"output_addr": 0x8400,
		"output_size": 64,
		"result_register": "memory"
	}
}