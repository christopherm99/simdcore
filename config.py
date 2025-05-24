
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
				"data": np.array([10, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
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
				"data": np.array([10, -10, 20, -30, 40, -50, 60, -70], dtype=np.half),
				"addr": 0x00
			},
			"v1": {
				"data": np.array([5, 5, 5, 5, 5, 5, 5, 5], dtype=np.half),
				"addr": 0x20
			}
		},
		"output_addr": 0x80
	},
}
