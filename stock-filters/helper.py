import utilityFunctions

# Lists each naturally occurring block by their ID
# Type denotes the resource type: B = Building Material, W = Water, V = Valuable, N = None
NATUAL_BLOCKS = {
	1: {'Name': 'Stone', 'Type': 'B'},
	2: {'Name': 'Grass', 'Type': 'N'},
	3: {'Name': 'Dirt', 'Type': 'N'},
	4: {'Name': 'Cobblestone', 'Type': 'B'},
	7: {'Name': 'Bedrock', 'Type': 'N'},
	8: {'Name': 'Flowing water', 'Type': 'W'},
	9: {'Name': 'Still water', 'Type': 'W'},
	10: {'Name': 'Flowing lava', 'Type': 'N'},
	11: {'Name': 'Still lava', 'Type': 'N'},
	12: {'Name': 'Sand', 'Type': 'N'},
	13: {'Name': 'Gravel', 'Type': 'B'},
	14: {'Name': 'Gold ore', 'Type': 'V'},
	15: {'Name': 'Iron ore', 'Type': 'V'},
	16: {'Name': 'Coal ore', 'Type': 'V'},
	17: {'Name': 'Wood', 'Type': 'B'},
	21: {'Name': 'Lapis Lazuli ore', 'Type': 'V'},
	24: {'Name': 'Sandstone', 'Type': 'N'},
	48: {'Name': 'Moss Stone', 'Type': 'N'},
	49: {'Name': 'Obsidian', 'Type': 'V'},
	56: {'Name': 'Diamond ore', 'Type': 'V'},
	73: {'Name': 'Redstone ore', 'Type': 'V'},
	78: {'Name': 'Snow', 'Type': 'W'},
	79: {'Name': 'Ice', 'Type': 'W'},
	80: {'Name': 'Snow block', 'Type': 'W'},
	82: {'Name': 'Clay', 'Type': 'B'},
	98: {'Name': 'Stone brick', 'Type': 'B'},
	129: {'Name': 'Emerald ore', 'Type': 'V'},
	179: {'Name': 'Red sandstone', 'Type': 'N'}
}

def isLiquidWater(id):
	return id == 8 or id == 9

def isBuildingMaterial(id):
	return NATUAL_BLOCKS[id]['Type'] == 'B'

def isWater(id):
	return NATUAL_BLOCKS[id]['Type'] == 'W'

def isValuable(id):
	return NATUAL_BLOCKS[id]['Type'] == 'V'

def isNotResource(id):
	return NATUAL_BLOCKS[id]['Type'] == 'N'

def isGround(id):
	return id in NATUAL_BLOCKS and id != 17 # Doesn't count the block as ground if it is air, wood, or plant material

_heightMap = {}

# # Calculates the heightmap by going down the y axis until it hits ground, 
# # and then starts checking neighboring coordinates starting from the last known heightmap value
# # This version of initializeHeightmap is might be inaccurate, but runs 10x faster
# def initializeHeightmap(level, box):
# 	# Getting the height of the ground at the box origin
# 	x = box.minx
# 	z = box.minz
# 	for y in xrange(255, -1, -1):
# 		id = level.blockAt(x, y, z)
# 		if isGround(id):
# 			_heightMap[x] = {z: y}
# 			z += 1
# 			break
# 	# Looping over each x-z coordinate
# 	while x < box.maxx:
# 		while z < box.maxz:
# 			# Calculating the height at (x, z)
# 			id = level.blockAt(x, y, z)
# 			if isGround(id):
# 				# Moving y up until it is no longer ground
# 				while True:
# 					y += 1
# 					id = level.blockAt(x, y, z)
# 					if not isGround(id):
# 						break
# 				# Moving y back down 1 so it is pointing to the ground block
# 				y -= 1
# 			else:
# 				# Moving y down until we hit ground
# 				while True:
# 					y -= 1
# 					id = level.blockAt(x, y, z)
# 					if isGround(id):
# 						break
# 			# Setting the heightmap at (x, z)
# 			_heightMap[x][z] = y
# 			# Incrementing z
# 			z += 1
# 		# Resetting z and y
# 		z = box.minz
# 		y = _heightMap[x][z]
# 		# Incrementing x
# 		x += 1
# 		# Adding a new dictionary to heightMap at _heightMap[x]
# 		_heightMap[x] = {}
# 	# Removing the unused dictionary (because we added a new dictionary just before we finished the loop)
# 	del _heightMap[x]

# Calculates the heightmap by going down the y axis until it hits ground for each x-z coordinate
# This version of initializeHeightmap is more accurate, but takes about 10x longer to run
def initializeHeightmap(level, box):
	x = box.minx
	z = box.minz
	while x < box.maxx:
		# Adding a new dictionary to heightMap at _heightMap[x]
		_heightMap[x] = {}
		while z < box.maxz:
			for y in xrange(255, -1, -1):
				id = level.blockAt(x, y, z)
				if isGround(id):
					break
			_heightMap[x][z] = y
			z += 1
		# Resetting z and y
		z = box.minz
		# Incrementing x
		x += 1



def getGroundYPos(x, z):
	return _heightMap[x][z]


def setBlock(level, id, x, y, z):
	utilityFunctions.setBlock(level, id, x, y, z)
	if y > _heightMap[x][z]:
		_heightMap[x][z] = y



# def getHistogram(level, box):
# 	histogram = {}
# 	types = numpy.zeros(65536, dtype='uint32')
# 	for (chunk, slices, point) in level.getChunkSlices(box):
# 		blocks = numpy.array(chunk.Blocks[slices], dtype='uint16')
# 		b = numpy.bincount(blocks.ravel())
# 		types[:b.shape[0]] = types[:b.shape[0]].astype(int) + b
# 	presentTypes = types.nonzero()
# 	blockCounts = [(level.materials[t & 0xfff, t >> 12], types[t]) for t in presentTypes[0]]
# 	for block, count in blockCounts:
# 		histogram[block.ID] = count
# 	return histogram