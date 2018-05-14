import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import Queue

import utilityFunctions
from helper import *
from ChunkAnalysis import *


def createHighways(level, box, segments, chunkMap, material, stairsId, entryPoints):
	def createHighway(roadWidth, allDistrictChunks, highwayNodes):
		class RoadNode:
			def __init__(self, x, z, goals, segmentIdentifier, roadWidth, prior = None, additionalCost = 0):
				self.x = x
				self.z = z
				#self.y = getGroundYPos(x, z)
				self.width = roadWidth
				self.medianY, self.stdDev = self.getYStats()
				self.prior = prior
				if prior is None:
					self.g = 0
				else:
					self.g = prior.g + additionalCost
					self.g += abs(self.medianY - prior.medianY)
				self.g += self.stdDev
				# Calculating h (heuristic)
				self.h = 999999
				for goal in goals:
					estimateToGoal = max(abs(goal[0] - self.x), abs(goal[1] - self.z))
					if estimateToGoal < self.h:
						self.h = estimateToGoal
				# Setting f (expected total cost to the closest goal)
				self.f = self.g + self.h

				if prior is None:
					self.deltaX = 0
					self.deltaZ = 0
					self.segmentIdentifier = segmentIdentifier
				else:
					self.deltaX = self.x - prior.x
					self.deltaZ = self.z - prior.z
					self.segmentIdentifier = prior.segmentIdentifier
				self.waterFraction = self.countWater() / (roadWidth ** 2.0)


			def clearHistory(self):
				self.prior = None
				self.g = self.stdDev
				self.f = self.g + self.h
				self.deltaX = 0
				self.deltaZ = 0

			def countWater(self):
				count = 0
				for x in xrange(self.x, self.x + roadWidth):
					for z in xrange(self.z, self.z + roadWidth):
						y = getGroundYPos(x, z)
						id = level.blockAt(x, y, z)
						if id == 8 or id == 9: # If liquid water
							count += 1
				return count

			def getYStats(self):
				yPositions = []
				for x in xrange(self.x, self.x + roadWidth):
					for z in xrange(self.z, self.z + roadWidth):
						yPositions.append(getGroundYPos(x, z))
				return numpy.median(yPositions), numpy.std(yPositions)

			@staticmethod
			def getSuccessorAttributes():
				# Successor attributes is just to make it easier to process successors (it lists deltaX, deltaZ, and cost from parent)
				successorAttributes = [(-1, 0, 1), (0, -1, 1), (0, 1, 1), (1, 0, 1)]
				if roadWidth > 1: # Can only move diagonally if road width is greater than 1
					successorAttributes += [(-1, -1, 1.5), (-1, 1, 1.5), (1, -1, 1.5), (1, 1, 1.5)]
				# Scaling successor attributes by the road width
				for i in xrange(len(successorAttributes)):
					successorAttributes[i] = (successorAttributes[i][0] * roadWidth, successorAttributes[i][1] * roadWidth, successorAttributes[i][2] * roadWidth)
				return successorAttributes

			def getSuccessors(self, successorAttributes, goals):
				successors = []
				for i in successorAttributes:
					# If the successor is within the box's bounds
					if box.minx <= (self.x + i[0]) < box.maxx - roadWidth and box.minz <= (self.z + i[1]) < box.maxz - roadWidth:
						candidate = RoadNode(self.x + i[0], self.z + i[1], goals, self.segmentIdentifier, self.width, self, i[2])
						if (candidate.medianY - self.medianY) <= roadWidth:
							if self.deltaX == 0 and self.deltaZ == 0:
								successors.append(candidate)
							# If self is mostly over water, only add candidates whos deltaX and deltaZ are equal to self's
							elif self.waterFraction > 0.5:
								if self.deltaX == candidate.deltaX and self.deltaZ == candidate.deltaZ:
									successors.append(candidate)
							# Can only go in a direction that is 45 degrees from the current direction
							elif roadWidth == 1: # Unless the road width is only 1
								successors.append(candidate)
							else:
								if self.deltaX == 0 and self.deltaZ > 0:
									if candidate.deltaZ > 0:
										successors.append(candidate)
								elif self.deltaX > 0 and self.deltaZ > 0:
									if candidate.deltaX >= 0 and candidate.deltaZ >= 0:
										successors.append(candidate)
								elif self.deltaX > 0 and self.deltaZ == 0:
									if candidate.deltaX > 0:
										successors.append(candidate)
								elif self.deltaX > 0 and self.deltaZ < 0:
									if candidate.deltaX >= 0 and candidate.deltaZ <= 0:
										successors.append(candidate)
								elif self.deltaX == 0 and self.deltaZ < 0:
									if candidate.deltaZ < 0:
										successors.append(candidate)
								elif self.deltaX < 0 and self.deltaZ < 0:
									if candidate.deltaX <= 0 and candidate.deltaZ <= 0:
										successors.append(candidate)
								elif self.deltaX < 0 and self.deltaZ == 0:
									if candidate.deltaX < 0:
										successors.append(candidate)
								else:
									if candidate.deltaX <= 0 and candidate.deltaZ >= 0:
										successors.append(candidate)
				return successors

			def regeneratePath(self, path = []):
				path.append(self)
				if self.prior is None:
					return path
				else:
					return self.prior.regeneratePath(path)

			def __lt__(self, other):
				return self.f < other.f

			def __hash__(self):
				return self.x + (512 * self.z)

			def __eq__(self, other):
				return self.x == other.x and self.z == other.z

		def getPath(startingChunk, endingChunks, startingSegment, otherSegments):
			successorAttributes = RoadNode.getSuccessorAttributes()
			goals = []
			for endingChunk in endingChunks:
				goals.append((endingChunk.box.minx + 8 - (roadWidth / 2), endingChunk.box.minz + 8 - (roadWidth / 2), endingChunk))
			resets = []
			for i in highwayNodes:
				if i.segmentIdentifier in startingSegment:
					resets.append((i.x, i.z, i.width))
				else:
					goals.append((i.x + (i.width / 2), i.z + (i.width / 2), i.segmentIdentifier))
			originX = startingChunk.box.minx + 8 - (roadWidth / 2)
			originZ = startingChunk.box.minz + 8 - (roadWidth / 2)
			originY = getGroundYPos(originX, originZ)
			openList = Queue.PriorityQueue()
			openList.put(RoadNode(originX, originZ, goals, startingChunk, roadWidth))
			closedSet = set()
			goalFound = None
			while openList.qsize() > 0:
				current = openList.get()
				# If we already checked this node, fetch the next best node in the open list
				# This check is necessary because when adding successors, we can't tell if it was already in the open list
				# Therefore, we will check if a better candidate at its position was already processed
				if current in closedSet:
					continue

				# Checking if a goal is within the road
				for goal in goals:
					if current.x <= goal[0] < current.x + roadWidth and current.z <= goal[1] < current.z + roadWidth:
						goalFound = goal[2]
						break
				if goalFound is not None:
					break

				# Checking if current overlaps with a chunk in another segment
				currentChunks = getChunksOverlappedWithBox(current.x, current.z, roadWidth)
				for i in currentChunks:
					if i in otherSegments:
						goalFound = i
						break
				if goalFound is not None:
					break

				# Checking if current and prior overlap with a chunk in startingSegment; if so, delete prior history from current
				if current.prior is not None:
					inStartingSegment = False
					for i in currentChunks:
						if i in startingSegment:
							inStartingSegment = True
							break
					if inStartingSegment:
						inStartingSegment = False
						priorChunks = getChunksOverlappedWithBox(current.prior.x, current.prior.z, roadWidth)
						for i in priorChunks:
							inStartingSegment = True
							break
						if inStartingSegment:
							# Remove history from current
							current.clearHistory()

				# Checking if we should restart the search from one of our previous roads we are near
				for i in resets:
					# If aligned horizontally
					if i[0] <= current.x <= i[0]+i[2] or i[0] <= current.x+roadWidth <= i[0]+i[2]:
						# If aligned vertically
						if i[1] <= current.z <= i[1]+i[2] or i[1] <= current.z+roadWidth <= i[1]+i[2]:
							# The overlap; clear history
							current.clearHistory()
							break

				# Adding current to the closed set
				closedSet.add(current)
				# Adding successors to the open list
				successors = current.getSuccessors(successorAttributes, goals)
				for i in successors:
					if i not in closedSet:
						openList.put(i)
			if goalFound is not None:
				return current.regeneratePath(), goalFound
			else:
				return [], None

		# Gets a list of all blocks along the path that will make up the road
		def getCompletePathCoordinates(path):
			pathCoordinates = []
			for i in xrange(len(path)):
				for xOffset in xrange(roadWidth):
					for zOffset in xrange(roadWidth):
						x = path[i].x + xOffset
						z = path[i].z + zOffset

						# Smoothing out the road's height
						# if path[i].deltaX > 0:
						# 	if xOffset < roadWidth / 2:
						# 		y = lerpInt(path[i - 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + xOffset) / float(roadWidth))
						# 	elif i < len(path) - 1:
						# 		y = lerpInt(path[i].medianY, path[i + 1].medianY, (xOffset - (roadWidth / 2)) / float(roadWidth))
						# 	else:
						# 		y = path[i].medianY
						# elif path[i].deltaX < 0:
						# 	if xOffset >= roadWidth / 2:
						# 		y = lerpInt(path[i].medianY, path[i - 1].medianY, (xOffset - (roadWidth / 2)) / float(roadWidth))
						# 	elif i < len(path) - 1:
						# 		y = lerpInt(path[i + 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + xOffset) / float(roadWidth))
						# 	else:
						# 		y = path[i].medianY
						# elif path[i].deltaZ > 0:
						# 	if zOffset < roadWidth / 2:
						# 		y = lerpInt(path[i - 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + zOffset) / float(roadWidth))
						# 	elif i < len(path) - 1:
						# 		y = lerpInt(path[i].medianY, path[i + 1].medianY, (zOffset - (roadWidth / 2)) / float(roadWidth))
						# 	else:
						# 		y = path[i].medianY
						# elif path[i].deltaZ < 0:
						# 	if zOffset >= roadWidth / 2:
						# 		y = lerpInt(path[i].medianY, path[i - 1].medianY, (zOffset - (roadWidth / 2)) / float(roadWidth))
						# 	elif i < len(path) - 1:
						# 		y = lerpInt(path[i + 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + zOffset) / float(roadWidth))
						# 	else:
						# 		y = path[i].medianY
						# else:
						# 	if i < len(path) - 1:
						# 		if path[i + 1].deltaX > 0:
						# 			if xOffset >= roadWidth / 2:
						# 				y = lerpInt(path[i].medianY, path[i + 1].medianY, (xOffset - (roadWidth / 2)) / float(roadWidth))
						# 			else:
						# 				y = path[i].medianY
						# 		elif path[i + 1].deltaX < 0:
						# 			if xOffset < roadWidth / 2:
						# 				y = lerpInt(path[i + 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + xOffset) / float(roadWidth))
						# 			else:
						# 				y = path[i].medianY
						# 		elif path[i + 1].deltaZ > 0:
						# 			if zOffset >= roadWidth / 2:
						# 				y = lerpInt(path[i].medianY, path[i + 1].medianY, (zOffset - (roadWidth / 2)) / float(roadWidth))
						# 			else:
						# 				y = path[i].medianY
						# 		else:
						# 			if zOffset < roadWidth / 2:
						# 				y = lerpInt(path[i + 1].medianY, path[i].medianY, (ceil(roadWidth / 2) + zOffset) / float(roadWidth))
						# 			else:
						# 				y = path[i].medianY
						# 	else:
						# 		y = path[i].medianY

						# y = int(round(y))


						y = getGroundYPos(x, z)

						pathCoordinates.append((x, y, z))
			# Determining road blocks between diagonal path coordinates
			for i in xrange(len(path) - 1):
				# If path[i] and path[i + 1] are diagonal from each other
				if path[i].x != path[i + 1].x and path[i].z != path[i + 1].z:
					# Getting the bounds of the 2x2 square containing the diagonal path coordinates
					minx = min(path[i].x, path[i + 1].x)
					maxx = max(path[i].x, path[i + 1].x)
					minz = min(path[i].z, path[i + 1].z)
					maxz = max(path[i].z, path[i + 1].z)
					maxx += roadWidth
					maxz += roadWidth
					# Diagonally along y = x line
					if (path[i + 1].x - path[i].x) == (path[i + 1].z - path[i].z):
						# Filling in the bottom right half of the top left box of the 2x2 square
						for x in xrange(minx + 1, minx + roadWidth):
							for z in xrange(minz + roadWidth, maxz - ((minx + roadWidth) - x)):
								y = getGroundYPos(x, z)
								pathCoordinates.append((x, y, z))
						# Filling in the top left half of the bottom right box of the 2x2 square
						for x in xrange(minx + roadWidth, maxx - 1):
							for z in xrange(minz + 1 + (x - (minx + roadWidth)), minz + roadWidth):
								y = getGroundYPos(x, z)
								pathCoordinates.append((x, y, z))
					# Diagonally along y = -x line
					else:
						# Filling in the top right half of the bottom left box of the 2x2 square
						for x in xrange(minx + 1, minx + roadWidth):
							for z in xrange(minz + ((minx + roadWidth) - x), minz + roadWidth):
								y = getGroundYPos(x, z)
								pathCoordinates.append((x, y, z))
						# Filling in the bottom left half of the top right box of the 2x2 square
						for x in xrange(minx + roadWidth, maxx - 1):
							for z in xrange(minz + roadWidth, maxz - 1 - (x - (minx + roadWidth))):
								y = getGroundYPos(x, z)
								pathCoordinates.append((x, y, z))
			return pathCoordinates

		def getChunkAtPos(x, z):
			return chunkMap[(x/16)*16][(z/16)*16][1]

		def getChunksOverlappedWithBox(x, z, roadWidth):
			result = [getChunkAtPos(x, z)]
			if x/16 == (x+roadWidth)/16:
				if z/16 == (z+roadWidth)/16:
					pass
				else:
					result.append(getChunkAtPos(x, z + roadWidth))
			else:
				result.append(getChunkAtPos(x + roadWidth, z))
				if z/16 == (z+roadWidth)/16:
					pass
				else:
					result.append(getChunkAtPos(x, z + roadWidth))
					result.append(getChunkAtPos(x + roadWidth, z + roadWidth))
			return result


		def addEntryPoints(roadNode, segment):
			chunks = getChunksOverlappedWithBox(roadNode.x, roadNode.z, roadWidth)
			for i in chunks:
				if i in segment:
					chunkType = chunkMap[i.box.minx][i.box.minz][0]
					roadX = roadNode.x + (roadWidth / 2)
					roadZ = roadNode.z + (roadWidth / 2)
					minDist = 99999999
					coordX = 0
					coordZ = 0
					for x in xrange(i.box.minx, i.box.maxx):
						for z in (i.box.minz, i.box.maxz - 1):
							dist = abs(x - roadX) + abs(z - roadZ)
							if dist < minDist:
								minDist = dist
								coordX = x
								coordZ = z
					for z in xrange(i.box.minz + 1, i.box.maxz - 1):
						for x in (i.box.minx, i.box.maxx - 1):
							dist = abs(x - roadX) + abs(z - roadZ)
							if dist < minDist:
								minDist = dist
								coordX = x
								coordZ = z
					entryPoints[chunkType].add((coordX, coordZ))
					break


					
		# createHighway function
		startingSegmentIndex = randint(0, len(segments) - 1)
		endingChunks = []
		otherSegments = set()
		for i in xrange(len(segments)):
			if i == startingSegmentIndex:
				startingSegment = segments[i]
				startingChunk = choice(list(startingSegment))
			else:
				otherSegments.union(segments[i])
				endingChunks.append(choice(list(segments[i])))
		
		path, stoppingChunkIdentifier = getPath(startingChunk, endingChunks, startingSegment, otherSegments)

		if stoppingChunkIdentifier is not None:
			# Determining which segment stoppingChunkIdentifier is in
			for i in xrange(len(segments)):
				if stoppingChunkIdentifier in segments[i]:
					stoppingSegmentIndex = i
					break

			# Adding the entry points where the road begins and ends
			if len(path) > 1:
				for i in xrange(len(path)):
					overlappedChunks = getChunksOverlappedWithBox(path[i].x, path[i].z, roadWidth)
					found = False
					for j in overlappedChunks:
						if j not in segments[stoppingSegmentIndex]:
							found = True
							break
					if found:
						break
				addEntryPoints(path[i], segments[stoppingSegmentIndex])
				addEntryPoints(path[-1], startingSegment)

			# Joining the two segments
			segments[startingSegmentIndex] = segments[startingSegmentIndex].union(segments[stoppingSegmentIndex])
			del segments[stoppingSegmentIndex]


		pathCoordinates = getCompletePathCoordinates(path)

		highwayNodes += path

		return pathCoordinates


	def getChunkAtPos(x, z):
		return chunkMap[(x/16)*16][(z/16)*16][1]

	# Builds a road on each path coordinate
	def constructRoadOnPath(pathCoordinates, allDistrictChunks):
		# Removing all invalid blocks
		for i in xrange(len(pathCoordinates) - 1, -1, -1):
			x = pathCoordinates[i][0]
			y = pathCoordinates[i][1]
			z = pathCoordinates[i][2]
			if getChunkAtPos(x, z) in allDistrictChunks:
				del pathCoordinates[i]
			else:
				deleteTree(level, x, z) # Removes any tree on the road
				for i in xrange(1, 5): # carving out space above the road
					setBlock(level, (0, 0), x, y + i, z)

		yLookup = {}
		for i in pathCoordinates:
			yLookup[(i[0], i[2])] = i[1]

		for x, y, z in pathCoordinates:
			if (x - 1, z) in yLookup and yLookup[(x - 1, z)] == y-1: # If downhill at x-1, add stairs facing -x (West)
				setBlock(level, (stairsId, 0), x, y, z)
			elif (x + 1, z) in yLookup and yLookup[(x + 1, z)] == y-1: # If downhill at x+1, add stairs facing +x (East)
				setBlock(level, (stairsId, 1), x, y, z)
			elif (x, z - 1) in yLookup and yLookup[(x, z - 1)] == y-1: # If downhill at z-1, add stairs facing -z (North)
				setBlock(level, (stairsId, 2), x, y, z)
			elif (x, z + 1) in yLookup and yLookup[(x, z + 1)] == y-1: # If downhill at z+1, add stairs facing +z (South)
				setBlock(level, (stairsId, 3), x, y, z)
			else: # Otherwise, set it as a regular block
				setBlock(level, material, x, y, z)



	# createHighways function
	allDistrictChunks = set()
	for i in segments:
		allDistrictChunks = allDistrictChunks.union(i)
	highwayNodes = []
	roadWidth = 3
	counter = 0
	pathCoordinates = []
	while len(segments) > 1:
		pathCoordinates += createHighway(roadWidth, allDistrictChunks, highwayNodes)
		counter += 1
		if counter >= 20:
			break

	constructRoadOnPath(pathCoordinates, allDistrictChunks)

	# Finalizing Entry Points
	for i in entryPoints:
		entryPoints[i] = list(entryPoints[i])

	return entryPoints



