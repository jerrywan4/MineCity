import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import random
import utilityFunctions
from helper import *

inputs = (
	("Place Districts", "label"),
	("Material", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	)

displayName = "YY Build"


def perform(level, box, options):
	startTime = time.time()

        def buildhouse1(level, chunk,material):
                minx = random.randint(chunk.box.minx,chunk.box.maxx-11);
                minz = random.randint(chunk.box.minz,chunk.box.maxz-11);


                bx = minx+10;
                bz = minz+7;


                minh = 255;
                maxh = 0;

                for x in xrange(minx,bx+1):
                        for z in xrange(minz,bz+1):
                                minh = min(minh,getGroundYPos(x,z))
                                maxh = max(maxh,getGroundYPos(x,z))

                if maxh-minh>2:
                        return False;


                table = ((minx+1,minz+1),(minx+1,bz-1),(bx-1,minz+1),(bx-1,bz-1));
                for (x,z) in table:
                        y = getGroundYPos(x,z)
                        if level.blockAt(x,y,z) in [8,9]:
                                return False;
                        
                



                # build house
                height = 0;
                for x in xrange(minx+1,bx):
                        for z in xrange(minz+1,bz):
                                height = max(height, getGroundYPos(x,z));

                # for four angles
                table = ((minx+1,minz+1),(minx+1,bz-1),(bx-1,minz+1),(bx-1,bz-1));
                for (x,z) in table:



                        
                        he = getGroundYPos(x,z)
                        for y in xrange(he+1,height+1):
                                setBlock(level, material, x, y , z)

                # ground
                for x in xrange(minx+1,bx):
                        for z in xrange(minz+1,bz):
                                setBlock(level, material,x,height+1,z)
                
                for x in xrange(minx+1,bx):
                        for z in (minz+1,bz-1):
                                for he in xrange(2,5):
                                        setBlock(level, material,x,height+he,z)

                for x in (minx+1,bx-1):
                        for z in xrange(minz+2,bz-1):
                                for he in xrange(2,5):
                                        setBlock(level, material,x,height+he,z)


                for x in (minx,bx):
                        for i in range(3):
                                for z in xrange(minz+1+i,bz-i):
                                        setBlock(level, (5,1),x,height+4+i,z)

                for x in xrange(minx,bx+1):
                        setBlock(level, (134,3),x,height+4,bz)
                        setBlock(level, (134,3),x,height+5,bz-1)
                        setBlock(level, (134,3),x,height+6,bz-2)
                        setBlock(level, (134,2),x,height+5,minz+1)
                        setBlock(level, (134,2),x,height+6,minz+2)
                        setBlock(level, (134,2),x,height+4,minz)

                for x in xrange(minx+1,bx):
                        for z in xrange(minz+3,bz-2):
                                setBlock(level,(5,1),x,height+6,z);
                #window
                x = minx+1;
                z = random.randint(minz+2,bz-2)

                setBlock(level, (20,0),x,height+3,z);
                        
                x = bx-1;
                z = random.randint(minz+2,bz-2)

                setBlock(level, (20,0),x,height+3,z);

                x = random.randint(minx+2,bx-2);
                z = minz+1;

                setBlock(level, (20,0),x,height+3,z);
                

                #door
                x = random.randint(minx+2,bx-2);
                z = bz-1;

                  
                setBlock(level, (64,3),x,height+2,z);
                setBlock(level, (64,9),x,height+3,z);



                
                while (level.blockAt(x,height+1,z+1)==0):
                        setBlock(level, (134,3),x,height+1,z+1);
                        z+=1;
                        height-=1;
                        if level.blockAt(x,height+1,z)==0:
                                setBlock(level, (134,6),x,height+1,z);







                return True;

        def flatGround(level,chunks,fence):
                #height = 0;
                #total = 0;
                #for chunk in chunks:
                #        for x in xrange(chunk.box.minx,chunk.box.maxx):
                #                for z in xrange(chunk.box.minz,chunk.box.maxz):
                #                        if level.blockAt(x,getGroundYPos(x,z),z) in [8,9]:
                #                                continue;
                #                        height += getGroundYPos(x,z)
                #                        total +=1 ;
                #average = height / total;

                for chunk in chunks:
                        for x in xrange(chunk.box.minx,chunk.box.maxx):
                                for z in xrange(chunk.box.minz,chunk.box.maxz):
                                        he = getGroundYPos(x,z);
                                        for y in xrange(he+1,256):
                                                setBlock(level, (0,0), x, y , z)
                                        setHeight(level,x,he,z);
             
                        #fenceInChunk(level, chunk, fence) # Purple

                        
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


        flatGround(level,chunks,(0,0));
        for chunk in chunks:
                for i in range(10):
                        if buildhouse1(level,chunk,(5,1)):
                                break;
                

	endTime = time.time()
	print "Finished in " + str(endTime - startTime) + " seconds"
	

	return;



                        

        
                
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

                self.role = 0;
                # 0:spare
                # 1:center
                # 2:living
                # 3:agricultrue
		

	def calculateHistogram(self, level, chunk, slices):


                histogram = {};
                self.numBlocks = 0;
                for x in xrange(self.box.minx,self.box.maxx):
                        for z in xrange(self.box.minz,self.box.maxz):
                                yg = getGroundYPos(x,z)
                                ymin = max(0,yg-3)
                                ymax = max(256,yg+10);
                                for y in xrange(ymin,ymax):
                                        self.numBlocks+=1;
                                        b = level.blockAt(x,y,z);
                                        if b in histogram:
                                                histogram[b]+=1;
                                        else:
                                                histogram[b]=1;
                self.numBlocks -= histogram[0];
                
                del histogram[0];
                
		
		return histogram

	def calculateResourceTypeHistogram(self):
		histogram = {"B": 0, "W": 0, "V": 0, "N": 0}
		for id in self.histogram:
			if id in NATUAL_BLOCKS:
				histogram[NATUAL_BLOCKS[id]['Type']] += self.histogram[id]
		return histogram

	def calculateFlatness(self, level):
		yPositions = []
		self.averageHeight = 0.0
		for x in xrange(self.box.minx, self.box.maxx):
			for z in xrange(self.box.minz, self.box.maxz):
				y = getGroundYPos(x, z)
				self.averageHeight += y;
				# Skip areas where the surface is liquid water
				if not isLiquidWater(level.blockAt(x, y, z)):
					yPositions.append(y)

                self.averageHeight /= 256;
		#self.numGroundBlocks = len(yPositions)
		self.groundPercentage = len(yPositions) / 256.
		if len(yPositions) < 1:
			heightStdDev = ChunkAnalysis.MOST_BUMPY_STDDEV
		else:
			heightStdDev = numpy.std(yPositions) / self.groundPercentage
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



