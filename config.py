
import numpy as np

"""Modify testcases_config to add new test cases."""
testcases_config = {
	"vector_add": {
		"inputs": {
			"v0": {
				"data": np.array([0, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([5, 15, -5, 25, -15, 35, -25, 45], dtype=np.half),
				"addr": 0x20
			}
		},
		"output_addr": 0x80
	},
	"hadamard": {
		"inputs": {
			"v0": {
				"data": np.array([2.0, -2.0, 1.0, -1.0, 0.5, -0.5, 0.0, 3.0],dtype=np.half),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([5, 5, 5, 5, 5, 5, 5, 5], dtype=np.half),
				"addr": 0x20
			}
		},
		"output_addr": 0x80
	},
	"transpose": {
		"inputs": {
			"v0": {
				"data": np.array([10, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
				"addr": 0x00
			}
		},
		"output_addr": 0x80
	},
	"reverse": {
		"inputs": {
			"v0": {
				"data": np.array([10, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
				"addr": 0x00
			}
		},
		"output_addr": 0x80
	},
	"relu": {
		"inputs": {
			"v0": {
				"data": np.array([10, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
				"addr": 0x00
			}
		},
		"output_addr": 0x80
	},
	"mse": {
		"inputs": {
			"v0": {
				"data": np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=np.half),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([5, 5, 5, 5, 5, 5, 5, 5], dtype=np.half),
				"addr": 0x20
			}
		},
		"output_addr": 0x80
	},
 "sigmoid": {
		"inputs": {
			"v0": {
				"data": np.array([1, -1, 2, -3, 4, -5, 6, -7], dtype=np.half),
				"addr": 0x00
			}
		},
		"output_addr": 0x80
	},
 "inner_product": {
		"inputs": {
			"v0": {
				"data": np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.half),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([8, 7, 6, 5, 4, 3, 2, 1], dtype=np.half),
				"addr": 0x20
			}
		},
		"output_addr": 0x80
	},
 	"matmul": {
		"inputs": {
			"matrix_a": {
				"data": np.array([
					[1, 0, 0, 0, 0, 0, 0, 0],  # row 0
					[0, 1, 0, 0, 0, 0, 0, 0],  # row 1
					[0, 0, 1, 0, 0, 0, 0, 0],  # row 2
					[0, 0, 0, 1, 0, 0, 0, 0],  # row 3
					[0, 0, 0, 0, 1, 0, 0, 0],  # row 4
					[0, 0, 0, 0, 0, 1, 0, 0],  # row 5
					[0, 0, 0, 0, 0, 0, 1, 0],  # row 6
					[0, 0, 0, 0, 0, 0, 0, 1]   # row 7
				], dtype=np.half),
				"addr": 0x0000
			},
			"matrix_b": {
				"data": np.array([
					[1, 2, 3, 4, 5, 6, 7, 8],      # row 0
					[2, 3, 4, 5, 6, 7, 8, 9],      # row 1
					[3, 4, 5, 6, 7, 8, 9, 10],     # row 2
					[4, 5, 6, 7, 8, 9, 10, 11],    # row 3
					[5, 6, 7, 8, 9, 10, 11, 12],   # row 4
					[6, 7, 8, 9, 10, 11, 12, 13],  # row 5
					[7, 8, 9, 10, 11, 12, 13, 14], # row 6
					[8, 9, 10, 11, 12, 13, 14, 15] # row 7
				], dtype=np.half),
				"addr": 0x0080
			}
		},
		"output_addr": 0x0100 
	}
}
