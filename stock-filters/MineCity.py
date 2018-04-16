import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions
from helper import *
from ChunkAnalysis import *
from PlaceDistricts import *
from CreateRoads import *

inputs = (
	("MineCity", "label"),
	)

displayName = "MineCity"


def perform(level, box, options):
	startTime = time.time()

	initializeHeightmap(level, box)

	
	# DISTRICT PLACEMENT
	chunks, districts = getChunksAndDistricts(level, box)
	# Districts is a list of the district centers in the following order:
	# [commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter, lowClassResidentialCenter]


	# ROAD CREATION
	material = (4, 0) # Cobblestone
	createRoad(level, box, districts[0], districts[1], 5, material) # Commercial to Industrial
	createRoad(level, box, districts[0], districts[2], 4, material) # Commercial to Agricultural
	createRoad(level, box, districts[0], districts[3], 3, material) # Commercial to High-Class Residential
	createRoad(level, box, districts[0], districts[4], 3, material) # Commercial to Low-Class Residential



	# Fencing in each district with a different color
	fenceInChunk(level, districts[0], (160, 2)) # Commercial = Purple
	fenceInChunk(level, districts[1], (160, 1)) # Industrial = Orange
	fenceInChunk(level, districts[2], (160, 4)) # Agricultural = Yellow
	fenceInChunk(level, districts[3], (160, 11)) # High-Class Residential = Dark Blue
	fenceInChunk(level, districts[4], (160, 9)) # Low-Class Residential = Light Blue


	# Analyzing the ground makeup of the industrial center
	# bHist, vHist = districts[1].analyzeGround(level, -5, 10)
	# print "Industrial District Building Materials: " + str(bHist);
	# print "Industrial District Valuables: " + str(vHist);

	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	return

