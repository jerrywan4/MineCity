import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions
from helper import *
from ChunkAnalysis import *
from PlaceDistrictsEvo import *
# from CreateRoads import *
from CreateHighways import *
# from BuildHouse1 import *
import rdbuild
import structure

inputs = (
	("MineCity", "label"),
	)

displayName = "MineCity"


def perform(level, box, options):
	startTime = time.time()
        structure.init();
	initializeHeightmap(level, box)

	
	# DISTRICT PLACEMENT
	chunks, districts, segments, chunkMap, entryPoints = getChunksAndDistricts(level, box)
	# Districts is a list of the district centers in the following order:
	# [commercialCenter, industrialCenter, agriculturalCenter, highClassResidentialCenter, lowClassResidentialCenter]


	# # ROAD CREATION
	# material = (4, 0) # Cobblestone
	# createRoad(level, box, districts[0], districts[1], 4, material) # Commercial to Industrial
	# createRoad(level, box, districts[0], districts[2], 3, material) # Commercial to Agricultural
	# createRoad(level, box, districts[0], districts[3], 3, material) # Commercial to High-Class Residential
	# createRoad(level, box, districts[0], districts[4], 3, material) # Commercial to Low-Class Residential

	# HIGHWAY CREATION
	material = (4, 0) # Cobblestone
	stairId = 67 # Cobblestone stairs
	entryPoints = createHighways(level, box, segments, chunkMap, material, stairId, entryPoints)
        print(entryPoints)
	# Use entryPoints to build the internal district streets

	


	# # BUILD HOUSES
	# for districtIndex in range(len(districts)):
	# 	chunk = districts[districtIndex]
	# 	for i in range(10):
	# 		if districtIndex == 2: # farm
	# 			if buildhouse(level,[chunk],"Farm"):
	# 				break
	# 		else:
	# 			if buildhouse(level,[chunk],"SmallHouse"):
	# 				break


	# Fencing in each district with a different color
	#for i in districts[0]:
	#	fenceInChunk(level, i, (160, 2)) # Commercial = Purple
	#for i in districts[1]:
	#	fenceInChunk(level, i, (160, 1)) # Industrial = Orange
	#for i in districts[2]:
	#	fenceInChunk(level, i, (160, 4)) # Agricultural = Yellow
	#for i in districts[3]:
	#	fenceInChunk(level, i, (160, 11)) # High-Class Residential = Dark Blue
	#for i in districts[4]:
	#	fenceInChunk(level, i, (160, 9)) # Low-Class Residential = Light Blue
        rdbuild.coBuild(level,districts[0],entryPoints['C']);
        rdbuild.idBuild(level,districts[1],entryPoints['I']);
        rdbuild.agriBuild(level, districts[2],entryPoints['A']);
        rdbuild.HighBuild(level, districts[3],25,25,entryPoints['H']);
        rdbuild.LowBuild(level, districts[4],25,25,entryPoints['L']);

	# Clears all trees from each district chunk
	#for i in districts:
	#	for j in i:
	#		removeAllTrees(level, j)

	# Analyzing the ground makeup of the industrial center
	# bHist, vHist = districts[1].analyzeGround(level, -5, 10)
	# print "Industrial District Building Materials: " + str(bHist);
	# print "Industrial District Valuables: " + str(vHist);

	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	return

def removeAllTrees(level, chunk):
	for x in xrange(chunk.box.minx, chunk.box.maxx):
		for z in xrange(chunk.box.minz, chunk.box.maxz):
			deleteTree(level, x, z)




