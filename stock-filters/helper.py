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
	162: {'Name': 'Dark Oak Wood', 'Type': 'B'},
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
        if id == 78:
                return False;
	return id in NATUAL_BLOCKS and not isPartOfTree(id) # Doesn't count the block as ground if it is air, wood, or plant material

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
				elif id in (17, 162): # If wood
					treeMap.add((x, z))
			_heightMap[x][z] = y
			z += 1
		# Resetting z and y
		z = box.minz
		# Incrementing x
		x += 1


treeMap = set()

MAX_TREE_RADIUS = 6
def deleteTree(level, x, z):
	if (x, z) in treeMap:
		treeMap.remove((x, z))
		y0 = getGroundYPos(x, z) + 1
		y = y0
		# Finding the bounds of the tree
		bounds = 0
		while True:
			for i in range(1, MAX_TREE_RADIUS + 1):
				if isPartOfTree(level.blockAt(x+i, y, z)) and isPartOfTree(level.blockAt(x-i, y, z)) and isPartOfTree(level.blockAt(x, y, z+i)) and isPartOfTree(level.blockAt(x, y, z-i)):
					continue
				else:
					if i > bounds:
						bounds = i
					break
			y += 1
			if isPartOfTree(level.blockAt(x, y, z)) and bounds < MAX_TREE_RADIUS: # If we are still finding tree material and bound is not max value, continue; there is more tree to explore
				continue
			else:
				break
		listOfTrees = list(treeMap)
		for i in range(len(listOfTrees) - 1, -1, -1): # Recurses on any tree that overlapped with the bounds we are removing
			tree = listOfTrees[i]
			if x-bounds <= tree[0] <= x+bounds and z-bounds <= tree[1] <= z+bounds:
				deleteTree(level, tree[0], tree[1])
		# Removing the tree material within the bounds
		for x1 in range(x-bounds, x+bounds + 1):
			if x1 in _heightMap:
				for z1 in range(z-bounds, z+bounds + 1):
					if z1 in _heightMap[x1]:
						for y1 in range(y0, y + 1):
							if isPartOfTree(level.blockAt(x1, y1, z1)):
								setBlock(level, (0, 0), x1, y1, z1) # Clears the block


def isPartOfTree(id):
	return id == 17 or id == 162 or id == 18 or id == 161 or id == 106



def getGroundYPos(x, z):
	return _heightMap[x][z]


def setBlock(level, id, x, y, z):
	utilityFunctions.setBlock(level, id, x, y, z)
	if id[0] == 0: # If placed an air-block
		if y == _heightMap[x][z]:
			for newY in xrange(y - 1, -1, -1):
				otherId = level.blockAt(x, newY, z)
				if isGround(otherId):
					_heightMap[x][z] = newY
					break
	else: # If placed a non-air block
		if y > _heightMap[x][z]:
			_heightMap[x][z] = y


def setHeight(level,x,y,z):
	_heightMap[x][z] = y


def lerpInt(min, max, t):
	return int(round(min + ((max - min) * t)))


def fenceInChunk(level, chunk, blockId):
	for x in xrange(chunk.box.minx, chunk.box.maxx):
		for z in (chunk.box.minz, chunk.box.maxz - 1):
			y = getGroundYPos(x, z)
			for yy in xrange(5):
				setBlock(level, blockId, x, y + 1 + yy, z)
	for z in xrange(chunk.box.minz + 1, chunk.box.maxz - 1):
		for x in (chunk.box.minx, chunk.box.maxx - 1):
			y = getGroundYPos(x, z)
			for yy in xrange(5):
				setBlock(level, blockId, x, y + 1 + yy, z)



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
