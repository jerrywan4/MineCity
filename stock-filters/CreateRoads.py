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


def createRoad(level, box, startingChunk, endingChunk, roadWidth, material):
	class RoadNode:
		def __init__(self, x, z, goals, prior = None, additionalCost = 0):
			self.x = x
			self.z = z
			#self.y = getGroundYPos(x, z)
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
			else:
				self.deltaX = self.x - prior.x
				self.deltaZ = self.z - prior.z
			self.waterFraction = self.countWater() / (roadWidth ** 2.0)
			

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
					candidate = RoadNode(self.x + i[0], self.z + i[1], goals, self, i[2])
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

	def getPath():
		successorAttributes = RoadNode.getSuccessorAttributes()
		goals = []
		goals.append((endingChunk.box.minx, endingChunk.box.minz))
		goals.append((endingChunk.box.maxx, endingChunk.box.minz))
		goals.append((endingChunk.box.minx, endingChunk.box.maxz))
		goals.append((endingChunk.box.maxx, endingChunk.box.maxz))
		originX = startingChunk.box.minx + 8 - (roadWidth / 2)
		originZ = startingChunk.box.minz + 8 - (roadWidth / 2)
		originY = getGroundYPos(originX, originZ)
		openList = Queue.PriorityQueue()
		openList.put(RoadNode(originX, originZ, goals))
		closedSet = set()
		foundGoal = False
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
					foundGoal = True
					break
			if foundGoal:
				break
			# Adding current to the closed set
			closedSet.add(current)
			# Adding successors to the open list
			successors = current.getSuccessors(successorAttributes, goals)
			for i in successors:
				if i not in closedSet:
					openList.put(i)
		if foundGoal:
			return current.regeneratePath()
		else:
			return []

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

	# Builds a road on each path coordinate
	def constructRoadOnPath(pathCoordinates, material):
		for x, y, z in pathCoordinates:
			setBlock(level, material, x, y, z)
			for i in xrange(1, 5): # carving out space above the road
				setBlock(level, (0, 0), x, y + i, z)
		
	path = getPath()
	pathCoordinates = getCompletePathCoordinates(path)
	constructRoadOnPath(pathCoordinates, material)
	return path, pathCoordinates





