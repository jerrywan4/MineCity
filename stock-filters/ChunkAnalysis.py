import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions
from helper import *


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
		if self.groundPercentage < minGround or self in commercialCenter:
			self.fitness = -999999
			return
		valuableFitness = abs((self.resourceProximity["V"] / maxScores["V"]) - idealValuable) * -1.25
		buildingMaterialFitness = abs((self.resourceProximity["B"] / maxScores["B"]) - idealBuildingMaterial) * -1
		avgDist1 = 0
		for i in commercialCenter:
			avgDist1 += self.distance(i)
		if len(commercialCenter) > 0:
			avgDist1 /= float(len(commercialCenter))
		distFitness = abs(avgDist1 - idealDistFromCommercial) * -0.0625#-0.25
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
		if self.groundPercentage < minGround or self in commercialCenter or self in industrialCenter:
			self.fitness = -999999
			return
		flatnessFitness = abs(self.flatness - idealFlatness) * -1.5
		waterFitness = abs((self.resourceProximity["W"] / maxScores["W"]) - idealWater) * -1
		groundFitness = abs(self.groundPercentage - idealGround) * -1.25
		avgDist1 = 0
		for i in commercialCenter:
			avgDist1 += self.distance(i)
		if len(commercialCenter) > 0:
			avgDist1 /= float(len(commercialCenter))
		distFitness = abs(avgDist1 - idealDistFromCommercial) * -0.0625#-0.25
		# Summing the fitness parameters
		self.fitness = flatnessFitness + waterFitness + groundFitness + distFitness

	def calculateHighClassResidentialFitness(self, maxScores, commercialCenter, industrialCenter, agriculturalCenter):
		# Identifying fitness parameters
		idealFlatness = 0.9
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
		avgDist1 = 0
		for i in commercialCenter:
			avgDist1 += self.distance(i)
		if len(commercialCenter) > 0:
			avgDist1 /= float(len(commercialCenter))
		avgDist2 = 0
		for i in industrialCenter:
			avgDist2 += self.distance(i)
		if len(industrialCenter) > 0:
			avgDist2 /= float(len(industrialCenter))
		avgDist3 = 0
		for i in agriculturalCenter:
			avgDist3 += self.distance(i)
		if len(agriculturalCenter) > 0:
			avgDist3 /= float(len(agriculturalCenter))
		distFitness1 = abs(avgDist1 - idealDistFromCommercial) * -0.1875#-0.75
		distFitness2 = abs(avgDist2 - idealDistFromIndustrial) * -0.125#-0.5
		distFitness3 = abs(avgDist3 - idealDistFromAgricultural) * -0.0625#-0.25
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
		avgDist1 = 0
		for i in commercialCenter:
			avgDist1 += self.distance(i)
		if len(commercialCenter) > 0:
			avgDist1 /= float(len(commercialCenter))
		avgDist2 = 0
		for i in industrialCenter:
			avgDist2 += self.distance(i)
		if len(industrialCenter) > 0:
			avgDist2 /= float(len(industrialCenter))
		distFitness1 = abs(avgDist1 - idealDistFromCommercial) * -0.125#-0.5
		distFitness2 = abs(avgDist2 - idealDistFromIndustrial) * -0.1875#-0.75
		# Summing the fitness parameters
		self.fitness = flatnessFitness + groundFitness + distFitness1 + distFitness2


	def analyzeGround(self, level, distBelowGround, distAboveGround):
		bHist = {}
		vHist = {}
		for x in xrange(self.box.minx, self.box.maxx):
			for z in xrange(self.box.minz, self.box.maxz):
				groundY = getGroundYPos(x, z)
				for y in xrange(groundY - distBelowGround, groundY + distAboveGround + 1):
					id = level.blockAt(x, y, z)
					if id in NATUAL_BLOCKS:
						if NATUAL_BLOCKS[id]["Type"] == "B":
							if id in bHist:
								bHist[id] += 1
							else:
								bHist[id] = 1
						elif NATUAL_BLOCKS[id]["Type"] == "V":
							if id in vHist:
								vHist[id] += 1
							else:
								vHist[id] = 1
		sortedBHist = [(bHist[key], key) for key in bHist]
		sortedBHist.sort()
		sortedBHist.reverse()
		sortedBHist = [(i[1], i[0]) for i in sortedBHist]
		sortedVHist = [(vHist[key], key) for key in vHist]
		sortedVHist.sort()
		sortedVHist.reverse()
		sortedVHist = [(i[1], i[0]) for i in sortedVHist]
		return sortedBHist, sortedVHist


	# Necessary for sorting
	def __lt__(self, other):
		return self.fitness < other.fitness



