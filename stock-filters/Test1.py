import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions
from helper import *

inputs = (
	("Place Districts", "label"),
	("Material", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	)

displayName = "Place Districts"


def perform(level, box, options):
	startTime = time.time()

	def fenceInChunk(level, chunk, blockId):
		for x in xrange(chunk.box.minx, chunk.box.maxx):
			for z in (chunk.box.minz, chunk.box.maxz - 1):
				y = getGroundYPos(x, z)
				for yy in range(10):
                                        setBlock(level, blockId, x, y + 1 + yy, z)
		for z in xrange(chunk.box.minz + 1, chunk.box.maxz - 1):
			for x in (chunk.box.minx, chunk.box.maxx - 1):
				y = getGroundYPos(x, z)
				for yy in range(10):
                                        setBlock(level, blockId, x, y + 1 + yy, z)


	initializeHeightmap(level, box)
	
	# Breaks up the selection box into chunks and performs an analysis on them
	chunks = []
	for (chunk, slices, point) in level.getChunkSlices(box):
		chunks.append(ChunkAnalysis(level, chunk, slices))

	# Analyzes distances to other resources
	maxScores = {"B": 1, "W": 1, "V": 1}
	for i in chunks:
		i.calculateResourceProximity(chunks, maxScores)

	# Calculating the fitness for the financial/commercial district
	commercialCenter = chunks[0]
	for i in chunks:
		i.calculateCommercialFitness(maxScores)
		if i.fitness > commercialCenter.fitness:
			commercialCenter = i

	# Calculating the fitness for the industrial district
	industrialCenter = chunks[0]
	for i in chunks:
		i.calculateIndustrialFitness(maxScores, commercialCenter)
		if i.fitness > industrialCenter.fitness:
			industrialCenter = i

	# Calculating the fitness for the agricultural district
	agriculturalCenter = chunks[0]
	for i in chunks:
		i.calculateAgriculturalFitness(maxScores, commercialCenter, industrialCenter)
		if i.fitness > agriculturalCenter.fitness:
			agriculturalCenter = i

	# Calculating the fitness for the high-class residential district
	highClassResidentialCenter = chunks[0]
	for i in chunks:
		i.calculateHighClassResidentialFitness(maxScores, commercialCenter, industrialCenter, agriculturalCenter)
		if i.fitness > highClassResidentialCenter.fitness:
			highClassResidentialCenter = i

	# Calculating the fitness for the low-class residential district
	lowClassResidentialCenter = chunks[0]
	for i in chunks:
		i.calculateLowClassResidentialFitness(maxScores, commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter)
		if i.fitness > lowClassResidentialCenter.fitness:
			lowClassResidentialCenter = i


	# Fencing in each district with a different color
	fenceInChunk(level, commercialCenter, (160, 2)) # Purple
	fenceInChunk(level, industrialCenter, (160, 1)) # Orange
	fenceInChunk(level, agriculturalCenter, (160, 4)) # Yellow
	fenceInChunk(level, highClassResidentialCenter, (160, 11)) # Dark Blue
	fenceInChunk(level, lowClassResidentialCenter, (160, 9)) # Light Blue



	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	return




class ChunkAnalysis:
	MOST_BUMPY_STDDEV = 10.

	def __init__(self, level, chunk, slices):
		self.box = chunk.bounds
		self.histogram = self.calculateHistogram(level, chunk, slices)
		self.resourceTypeHistogram = self.calculateResourceTypeHistogram() # A dict of floats from 0 to 1 denoting the fraction of all
																		   # blocks in the chunk that are of a particular resource type
		self.flatness = self.calculateFlatness(level) # A float from 0 to 1, 1 being the most flat and 0 being the most bumpy
		# self.numBlocks = 0 # A total count of all non-air blocks within the chunk
		# self.groundPercentage = 0 # A float from 0 to 1 denoting the fraction of the chunk's ground that is not liquid water
		# self.resourceProximity = {}
		# self.fitness = 0

	def calculateHistogram(self, level, chunk, slices):
		types = numpy.zeros(65536, dtype='uint32')
		blocks = numpy.array(chunk.Blocks[slices], dtype='uint16')
		b = numpy.bincount(blocks.ravel())
		types[:b.shape[0]] = types[:b.shape[0]].astype(int) + b
		presentTypes = types.nonzero()
		histogram = { level.materials[t & 0xfff, t >> 12].ID : types[t] for t in presentTypes[0] }
		self.numBlocks = 65536. - histogram[0]
		del histogram[0] # Removing air from the histogram
		return histogram

	def calculateResourceTypeHistogram(self):
		histogram = {"B": 0, "W": 0, "V": 0, "N": 0}
		for id in self.histogram:
			if id in NATUAL_BLOCKS:
				histogram[NATUAL_BLOCKS[id]['Type']] += self.histogram[id]
		for key in histogram:
			histogram[key] /= self.numBlocks
		return histogram

	def calculateFlatness(self, level):
		yPositions = []
		for x in xrange(self.box.minx, self.box.maxx):
			for z in xrange(self.box.minz, self.box.maxz):
				y = getGroundYPos(x, z)
				# Skip areas where the surface is liquid water
				if not isLiquidWater(level.blockAt(x, y, z)):
					yPositions.append(y)
		#self.numGroundBlocks = len(yPositions)
		self.groundPercentage = len(yPositions) / 256.
		if len(yPositions) < 1:
			heightStdDev = ChunkAnalysis.MOST_BUMPY_STDDEV
		else:
			heightStdDev = numpy.std(yPositions)
		# Determining a flatness score from 0 to 1 based on the standard deviation in the height
		return max(1 - (heightStdDev / ChunkAnalysis.MOST_BUMPY_STDDEV), 0)

	def calculateResourceProximity(self, allChunks, maxScores):
		self.resourceProximity = {"B": 0, "W": 0, "V": 0}
		for chunk in allChunks:
			sqrDist = self.sqrDistance(chunk)
			sqrDist += 1 # To prevent divide by 0 errors
			self.resourceProximity["B"] += chunk.resourceTypeHistogram["B"] / sqrDist
			self.resourceProximity["W"] += chunk.resourceTypeHistogram["W"] / sqrDist
			self.resourceProximity["V"] += chunk.resourceTypeHistogram["V"] / sqrDist
		if self.resourceProximity["B"] > maxScores["B"]:
			maxScores["B"] = self.resourceProximity["B"]
		if self.resourceProximity["W"] > maxScores["W"]:
			maxScores["W"] = self.resourceProximity["W"]
		if self.resourceProximity["V"] > maxScores["V"]:
			maxScores["V"] = self.resourceProximity["V"]

	# Returns the squared distance between the 2 chunks (the distance is in terms of chunks; a return value of 1 = 16 blocks)
	def sqrDistance(self, other):
		# Delta x and z between chunk origins is divided by 16 so 1 chunk over corresponds to a distance of 1
		return (((self.box.minx - other.box.minx)/16) ** 2.) + (((self.box.minz - other.box.minz)/16) ** 2.)

	# Returns the distance between the 2 chunks (the distance is in terms of chunks; a return value of 1 = 16 blocks)
	def distance(self, other):
		return sqrt(self.sqrDistance(other))

	def calculateCommercialFitness(self, maxScores):
		# Identifying fitness parameters
		idealFlatness = 1
		idealWater = 1
		idealGround = 0.8
		minGround = 0.15
		# Calculating each parameter's score
		if self.groundPercentage < minGround:
			self.fitness = -999999
			return
		flatnessFitness = abs(self.flatness - idealFlatness) * -1
		waterFitness = abs((self.resourceProximity["W"] / maxScores["W"]) - idealWater) * -1
		groundFitness = abs(self.groundPercentage - idealGround) * -1
		# Summing the fitness parameters
		self.fitness = flatnessFitness + waterFitness + groundFitness

	def calculateIndustrialFitness(self, maxScores, commercialCenter):
		# Identifying fitness parameters
		idealValuable = 1
		idealBuildingMaterial = 1
		idealDistFromCommercial = 5
		minGround = 0.15
		# Calculating each parameter's score
		if self.groundPercentage < minGround or self == commercialCenter:
			self.fitness = -999999
			return
		valuableFitness = abs((self.resourceProximity["V"] / maxScores["V"]) - idealValuable) * -1.25
		buildingMaterialFitness = abs((self.resourceProximity["B"] / maxScores["B"]) - idealBuildingMaterial) * -1
		distFitness = abs(self.distance(commercialCenter) - idealDistFromCommercial) * -0.25
		# Summing the fitness parameters
		self.fitness = valuableFitness + buildingMaterialFitness + distFitness

	def calculateAgriculturalFitness(self, maxScores, commercialCenter, industrialCenter):
		# Identifying fitness parameters
		idealFlatness = 1
		idealWater = 0.25
		idealGround = 1
		idealDistFromCommercial = 3.5
		minGround = 0.5
		# Calculating each parameter's score
		if self.groundPercentage < minGround or self in [commercialCenter, industrialCenter]:
			self.fitness = -999999
			return
		flatnessFitness = abs(self.flatness - idealFlatness) * -1.5
		waterFitness = abs((self.resourceProximity["W"] / maxScores["W"]) - idealWater) * -1
		groundFitness = abs(self.groundPercentage - idealGround) * -1.25
		distFitness = abs(self.distance(commercialCenter) - idealDistFromCommercial) * -0.25
		# Summing the fitness parameters
		self.fitness = flatnessFitness + waterFitness + groundFitness + distFitness

	def calculateHighClassResidentialFitness(self, maxScores, commercialCenter, industrialCenter, agriculturalCenter):
		# Identifying fitness parameters
		idealFlatness = 0.8
		idealWater = 0.25
		idealGround = 1
		idealDistFromCommercial = 0
		idealDistFromIndustrial = 6
		idealDistFromAgricultural = 2.5
		minGround = 0.5
		# Calculating each parameter's score
		if self.groundPercentage < minGround or self in [commercialCenter, industrialCenter, agriculturalCenter]:
			self.fitness = -999999
			return
		flatnessFitness = abs(self.flatness - idealFlatness) * -1
		waterFitness = abs((self.resourceProximity["W"] / maxScores["W"]) - idealWater) * -1
		groundFitness = abs(self.groundPercentage - idealGround) * -0.5
		distFitness1 = abs(self.distance(commercialCenter) - idealDistFromCommercial) * -0.75
		distFitness2 = abs(self.distance(industrialCenter) - idealDistFromIndustrial) * -0.5
		distFitness3 = abs(self.distance(agriculturalCenter) - idealDistFromAgricultural) * -0.25
		# Summing the fitness parameters
		self.fitness = flatnessFitness + waterFitness + groundFitness + distFitness1 + distFitness2 + distFitness3

	def calculateLowClassResidentialFitness(self, maxScores, commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter):
		# Identifying fitness parameters
		idealFlatness = 1
		idealGround = 1
		idealDistFromCommercial = 4
		idealDistFromIndustrial = 0
		minGround = 0.5
		# Calculating each parameter's score
		if self.groundPercentage < minGround or self in [commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter]:
			self.fitness = -999999
			return
		flatnessFitness = abs(self.flatness - idealFlatness) * -1
		groundFitness = abs(self.groundPercentage - idealGround) * -1
		distFitness1 = abs(self.distance(commercialCenter) - idealDistFromCommercial) * -0.5
		distFitness2 = abs(self.distance(industrialCenter) - idealDistFromIndustrial) * -0.75
		# Summing the fitness parameters
		self.fitness = flatnessFitness + groundFitness + distFitness1 + distFitness2

	# Necessary for sorting
	def __lt__(self, other):
		return self.fitness < other.fitness



