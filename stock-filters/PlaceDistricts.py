import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions
from helper import *
from ChunkAnalysis import *


def getChunksAndDistricts(level, box):
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

	return chunks, [commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter, lowClassResidentialCenter]

