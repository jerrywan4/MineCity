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
	("Remove Trees", "label"),
	("Number to Remove", (1, 10))
	)

displayName = "Remove Trees"


def perform(level, box, options):
	startTime = time.time()

	initializeHeightmap(level, box)

	for i in range(options["Number to Remove"]):
		listOfTrees = list(treeMap)
		if len(listOfTrees) == 0:
			break
		x = choice(listOfTrees)
	 	deleteTree(level, x[0], x[1])
	
	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	return

