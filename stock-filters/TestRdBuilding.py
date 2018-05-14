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
import rdbuild
import build;
import structure
inputs = (
	("TestBuilding", "label"),
	)

displayName = "TestBuilding"


def perform(level, box, options):
        startTime = time.time()

	initializeHeightmap(level, box)
        structure.init()

	chunks = []
	for (chunk, slices, point) in level.getChunkSlices(box):
		chunks.append(ChunkAnalysis(level, chunk, slices))
        minx = box.minx;
        minz = box.minz;
        maxx = box.maxx;
        maxz = box.maxz
        rdbuild.init(level,minx,maxx,minz,maxz,chunks);
        entrys = [(minx,minz)];


        #print(level.blockAt(minx,getGroundYPos(minx,minz),minz))
        
        rdbuild.LowBuild(level, chunks,25,25,[(minx,minz)]);
        


        #rdbuild.flatGround(level,[minx,minz,6,6]);
        #height = getGroundYPos(minx+1,minz+1)
        #rdbuild.buildWell(level,minx,minz,height,(24,0),(17,0));
        

        

	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	return

