import numpy as np

def num_to_fixed(val, frac_bits=15):
	return int(val * (1 << frac_bits))

"""Modify testcases_config to add new test cases."""
testcases_config = {
	"vector_add": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.0), num_to_fixed(-0.1), num_to_fixed(0.2), num_to_fixed(-0.3), 
					num_to_fixed(0.4), num_to_fixed(-0.5), num_to_fixed(0.6), num_to_fixed(-0.7)
				], dtype=np.int16),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([
					num_to_fixed(0.05), num_to_fixed(0.15), num_to_fixed(-0.05), num_to_fixed(0.25), 
					num_to_fixed(-0.15), num_to_fixed(0.35), num_to_fixed(-0.25), num_to_fixed(0.45)
				], dtype=np.int16),
				"addr": 0x20
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"hadamard": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.2), num_to_fixed(-0.2), num_to_fixed(0.1), num_to_fixed(-0.1), 
					num_to_fixed(0.5), num_to_fixed(-0.5), num_to_fixed(0.0), num_to_fixed(0.3)
				], dtype=np.int16),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([
					num_to_fixed(0.5), num_to_fixed(0.5), num_to_fixed(0.5), num_to_fixed(0.5), 
					num_to_fixed(0.5), num_to_fixed(0.5), num_to_fixed(0.5), num_to_fixed(0.5)
				], dtype=np.int16),
				"addr": 0x20
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"transpose": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(-0.1), num_to_fixed(0.2), num_to_fixed(-0.3), 
					num_to_fixed(0.4), num_to_fixed(-0.5), num_to_fixed(0.6), num_to_fixed(-0.7)
				], dtype=np.int16),
				"addr": 0x00
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"reverse": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(-0.1), num_to_fixed(0.2), num_to_fixed(-0.3), 
					num_to_fixed(0.4), num_to_fixed(-0.5), num_to_fixed(0.6), num_to_fixed(-0.7)
				], dtype=np.int16),
				"addr": 0x00
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"relu": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(-0.1), num_to_fixed(0.2), num_to_fixed(-0.3), 
					num_to_fixed(0.4), num_to_fixed(-0.5), num_to_fixed(0.6), num_to_fixed(-0.7)
				], dtype=np.int16),
				"addr": 0x00
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"mse": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(0.2), num_to_fixed(0.3), num_to_fixed(0.4), 
					num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8)
				], dtype=np.int16),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([
					num_to_fixed(0.05), num_to_fixed(0.05), num_to_fixed(0.05), num_to_fixed(0.05), 
					num_to_fixed(0.05), num_to_fixed(0.05), num_to_fixed(0.05), num_to_fixed(0.05)
				], dtype=np.int16),
				"addr": 0x20
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"sigmoid": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(-0.1), num_to_fixed(0.2), num_to_fixed(-0.3), 
					num_to_fixed(0.4), num_to_fixed(-0.5), num_to_fixed(0.6), num_to_fixed(-0.7)
				], dtype=np.int16),
				"addr": 0x00
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"inner_product": {
		"inputs": {
			"v0": {
				"data": np.array([
					num_to_fixed(0.1), num_to_fixed(0.2), num_to_fixed(0.3), num_to_fixed(0.4), 
					num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8)
				], dtype=np.int16),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([
					num_to_fixed(0.8), num_to_fixed(0.7), num_to_fixed(0.6), num_to_fixed(0.5), 
					num_to_fixed(0.4), num_to_fixed(0.3), num_to_fixed(0.2), num_to_fixed(0.1)
				], dtype=np.int16),
				"addr": 0x20
			}
		},
		"output_addr": 0x80,
		"output_size": 8
	},
	"matmul": {
		"inputs": {
			"matrix_a": {
				"data": np.array([
					[num_to_fixed(0.1), num_to_fixed(0.2), num_to_fixed(0.3), num_to_fixed(0.4), num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8)],
					[num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1), num_to_fixed(0.0)],
					[num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.0), num_to_fixed(0.1)]
				], dtype=np.int16),
				"addr": 0x0000
			},
			"matrix_b": {
				"data": np.array([
					[num_to_fixed(0.1), num_to_fixed(0.2), num_to_fixed(0.3), num_to_fixed(0.4), num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8)],
					[num_to_fixed(0.2), num_to_fixed(0.3), num_to_fixed(0.4), num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9)],
					[num_to_fixed(0.3), num_to_fixed(0.4), num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9)],  
					[num_to_fixed(0.4), num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9), num_to_fixed(-0.8)],
					[num_to_fixed(0.5), num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9), num_to_fixed(-0.8), num_to_fixed(-0.7)],
					[num_to_fixed(0.6), num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9), num_to_fixed(-0.8), num_to_fixed(-0.7), num_to_fixed(-0.6)],
					[num_to_fixed(0.7), num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9), num_to_fixed(-0.8), num_to_fixed(-0.7), num_to_fixed(-0.6), num_to_fixed(-0.5)],
					[num_to_fixed(0.8), num_to_fixed(0.9), num_to_fixed(-0.9), num_to_fixed(-0.8), num_to_fixed(-0.7), num_to_fixed(-0.6), num_to_fixed(-0.5), num_to_fixed(-0.4)]
				], dtype=np.int16),
				"addr": 0x0100
			}
		},
		"output_addr": 0x0180,
		"output_size": 64
	}
}
