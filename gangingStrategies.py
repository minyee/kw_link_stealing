from enum import Enum

class GangingStrategy(Enum):
	BLOCK = 1
	STRIDE = 2
	BSSD = 3 # block-src-stride-dst