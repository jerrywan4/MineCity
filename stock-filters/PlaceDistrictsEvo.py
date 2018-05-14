import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
from collections import deque

import utilityFunctions
from helper import *
from ChunkAnalysis import *


class Genome:

	MIN_GROUND = 0.15

	def __init__(self):
		# Contains a list of chunk analysis objects for each district
		self.commercial = []
		self.highClassResidential = []
		self.lowClassResidential = []
		self.industrial = []
		self.agricultural = []
		self.map = {} # Maps all coordinates to a district denoted by a letter and a chunk as a tuple: C, I, A, H, or L (N = None)

	def calcFitness(self, maxScores, chunks, numNonWaterChunks):
		for i in self.commercial:
			if self.map[i.box.minx][i.box.minz][0] != "C":
				self.fitness = -999
				return
		for i in self.industrial:
			if self.map[i.box.minx][i.box.minz][0] != "I":
				self.fitness = -999
				return
		for i in self.agricultural:
			if self.map[i.box.minx][i.box.minz][0] != "A":
				self.fitness = -999
				return
		for i in self.highClassResidential:
			if self.map[i.box.minx][i.box.minz][0] != "H":
				self.fitness = -999
				return
		for i in self.lowClassResidential:
			if self.map[i.box.minx][i.box.minz][0] != "L":
				self.fitness = -999
				return

		idealNumAg = 0.4 * (len(self.highClassResidential) + len(self.lowClassResidential) + len(self.commercial))
		idealNumInd = 0.25 * (len(self.highClassResidential) + len(self.lowClassResidential) + len(self.commercial))
		idealNumHi = 0.5 * len(self.lowClassResidential)
		idealNumCom = 0.7 * len(self.highClassResidential)

		if idealNumAg == 0:
			idealNumAg = 1.0
		if idealNumInd == 0:
			idealNumInd = 1.0
		if idealNumHi == 0:
			idealNumHi = 1.0
		if idealNumCom == 0:
			idealNumCom = 1.0

		numAgScore = len(self.agricultural) / idealNumAg
		if numAgScore > 1:
			numAgScore = 1 / numAgScore

		numIndScore = len(self.industrial) / idealNumInd
		if numIndScore > 1:
			numIndScore = 1 / numIndScore

		numComScore = len(self.commercial) / idealNumCom
		if numComScore > 1:
			numComScore = 1 / numComScore

		numHiScore = len(self.highClassResidential) / idealNumHi
		if numHiScore > 1:
			numHiScore = 1 / numHiScore

		occurrenceFitness = numAgScore * numIndScore * numComScore * numHiScore # From 0 to 1 inclusive

		total = 0
		for i in self.commercial:
			i.calculateCommercialFitness(maxScores)
			total += i.fitness
		if len(self.commercial) == 0:
			comAvg = 0
		else:
			comAvg = total / float(len(self.commercial))
			comAvg /= 3.0 # Normalizing the fitness

		total = 0
		for i in self.industrial:
			i.calculateIndustrialFitness(maxScores, self.commercial)
			total += i.fitness
		if len(self.industrial) == 0:
			indAvg = 0
		else:
			indAvg = total / float(len(self.industrial))
			indAvg /= 3.0 # Normalizing the fitness

		total = 0
		for i in self.agricultural:
			i.calculateAgriculturalFitness(maxScores, self.commercial, self.industrial)
			total += i.fitness
		if len(self.agricultural) == 0:
			agAvg = 0
		else:
			agAvg = total / float(len(self.agricultural))
			agAvg /= 4.0 # Normalizing the fitness

		total = 0
		for i in self.highClassResidential:
			i.calculateHighClassResidentialFitness(maxScores, self.commercial, self.industrial, self.agricultural)
			total += i.fitness
		if len(self.highClassResidential) == 0:
			hiAvg = 0
		else:
			hiAvg = total / float(len(self.highClassResidential))
			hiAvg /= 6.0 # Normalizing the fitness

		total = 0
		for i in self.lowClassResidential:
			i.calculateLowClassResidentialFitness(maxScores, self.commercial, self.industrial, self.agricultural, self.highClassResidential)
			total += i.fitness
		if len(self.lowClassResidential) == 0:
			loAvg = 0
		else:
			loAvg = total / float(len(self.lowClassResidential))
			loAvg /= 4.0 # Normalizing the fitness

		allAvgs = [comAvg, indAvg, agAvg, hiAvg, loAvg]
		fitnessStddev = numpy.std(allAvgs)
		totalFitness = sum(allAvgs)

		totalDistricts = len(self.highClassResidential) + len(self.lowClassResidential) + len(self.commercial) + len(self.industrial) + len(self.agricultural)
		idealNumDistricts = numNonWaterChunks * 0.35
		if idealNumDistricts < 10:
			idealNumDistricts = 10
		numDistrictFitness = totalDistricts / idealNumDistricts
		if numDistrictFitness > 1:
			numDistrictFitness = 1 / numDistrictFitness

		self.fitness = ((totalFitness / 5.0) * 2.0) + (fitnessStddev * 1.0) + (occurrenceFitness * 2.5) + (numDistrictFitness * 1.25)

	def verifyDistrictExistance(self, chunks):
		i = 0
		while len(self.commercial) == 0 and i < 500:
			i += 1
			chunk = choice(chunks)
			if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[chunk.box.minx][chunk.box.minz][0] == "N":
				self.map[chunk.box.minx][chunk.box.minz] = ("C", chunk)
				self.commercial.append(chunk)
		i = 0
		while len(self.industrial) == 0 and i < 500:
			i += 1
			chunk = choice(chunks)
			if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[chunk.box.minx][chunk.box.minz][0] == "N":
				self.map[chunk.box.minx][chunk.box.minz] = ("I", chunk)
				self.industrial.append(chunk)
		i = 0
		while len(self.agricultural) == 0 and i < 500:
			i += 1
			chunk = choice(chunks)
			if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[chunk.box.minx][chunk.box.minz][0] == "N":
				self.map[chunk.box.minx][chunk.box.minz] = ("A", chunk)
				self.agricultural.append(chunk)
		i = 0
		while len(self.highClassResidential) == 0 and i < 500:
			i += 1
			chunk = choice(chunks)
			if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[chunk.box.minx][chunk.box.minz][0] == "N":
				self.map[chunk.box.minx][chunk.box.minz] = ("H", chunk)
				self.highClassResidential.append(chunk)
		i = 0
		while len(self.lowClassResidential) == 0 and i < 500:
			i += 1
			chunk = choice(chunks)
			if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[chunk.box.minx][chunk.box.minz][0] == "N":
				self.map[chunk.box.minx][chunk.box.minz] = ("L", chunk)
				self.lowClassResidential.append(chunk)

	def setToNone(self, x, z):
		if self.map[x][z][0] == "C":
			self.commercial.remove(self.map[x][z][1])
		elif self.map[x][z][0] == "I":
			self.industrial.remove(self.map[x][z][1])
		elif self.map[x][z][0] == "A":
			self.agricultural.remove(self.map[x][z][1])
		elif self.map[x][z][0] == "H":
			self.highClassResidential.remove(self.map[x][z][1])
		elif self.map[x][z][0] == "L":
			self.lowClassResidential.remove(self.map[x][z][1])
		self.map[x][z] = ("N", self.map[x][z][1])

	def randomize(self, chunks):
		for i in chunks:
			if i.box.minx not in self.map:
				self.map[i.box.minx] = {}
			self.map[i.box.minx][i.box.minz] = ("N", i)
		num = randint(int(ceil(len(chunks) * 0.2)), int(ceil(len(chunks) * 0.8)))
		for i in range(num):
			index = randint(1,5)
			if index == 1:
				if len(self.commercial) >= 1:
					chunkIndex = randint(0, len(self.commercial) - 1)
					chunk = self.getBorderChunk(self.commercial[chunkIndex], False)
					self.setToNone(chunk.box.minx, chunk.box.minz)
					self.map[chunk.box.minx][chunk.box.minz] = ("C", chunk)
					self.commercial.append(chunk)
				else:
					self.verifyDistrictExistance(chunks)
			elif index == 2:
				if len(self.industrial) >= 1:
					chunkIndex = randint(0, len(self.industrial) - 1)
					chunk = self.getBorderChunk(self.industrial[chunkIndex], False)
					self.setToNone(chunk.box.minx, chunk.box.minz)
					self.map[chunk.box.minx][chunk.box.minz] = ("I", chunk)
					self.industrial.append(chunk)
				else:
					self.verifyDistrictExistance(chunks)
			elif index == 3:
				if len(self.agricultural) >= 1:
					chunkIndex = randint(0, len(self.agricultural) - 1)
					chunk = self.getBorderChunk(self.agricultural[chunkIndex], False)
					self.setToNone(chunk.box.minx, chunk.box.minz)
					self.map[chunk.box.minx][chunk.box.minz] = ("A", chunk)
					self.agricultural.append(chunk)
				else:
					self.verifyDistrictExistance(chunks)
			elif index == 4:
				if len(self.highClassResidential) >= 1:
					chunkIndex = randint(0, len(self.highClassResidential) - 1)
					chunk = self.getBorderChunk(self.highClassResidential[chunkIndex], False)
					self.setToNone(chunk.box.minx, chunk.box.minz)
					self.map[chunk.box.minx][chunk.box.minz] = ("H", chunk)
					self.highClassResidential.append(chunk)
				else:
					self.verifyDistrictExistance(chunks)
			elif index == 5:
				if len(self.lowClassResidential) >= 1:
					chunkIndex = randint(0, len(self.lowClassResidential) - 1)
					chunk = self.getBorderChunk(self.lowClassResidential[chunkIndex], False)
					self.setToNone(chunk.box.minx, chunk.box.minz)
					self.map[chunk.box.minx][chunk.box.minz] = ("L", chunk)
					self.lowClassResidential.append(chunk)
				else:
					self.verifyDistrictExistance(chunks)


	def randomize_old(self, chunks):
		for i in chunks:
			if i.box.minx not in self.map:
				self.map[i.box.minx] = {}
			self.map[i.box.minx][i.box.minz] = ("N", i)
		num = randint(int(ceil(len(chunks) * 0.2)), int(ceil(len(chunks) * 0.8)))
		for i in range(num):
			self.assignChunk(choice(chunks))
		# Verifying that all districts exist
		self.verifyDistrictExistance(chunks)
		# Verifying continguousness of commercial chunks
		contiguous = self.getMaxSegment(self.commercial)
		toRemove = []
		for i in self.commercial:
			if i not in contiguous:
				toRemove.append(i)
		for i in toRemove:
			self.commercial.remove(i)
			self.map[i.box.minx][i.box.minz] = ("N", i)
		# Verifying continguousness of high class chunks
		contiguous = self.getMaxSegment(self.highClassResidential)
		toRemove = []
		for i in self.highClassResidential:
			if i not in contiguous:
				toRemove.append(i)
		for i in toRemove:
			self.highClassResidential.remove(i)
			self.map[i.box.minx][i.box.minz] = ("N", i)
		# Verifying continguousness of low class chunks
		contiguous = self.getMaxSegment(self.lowClassResidential)
		toRemove = []
		for i in self.lowClassResidential:
			if i not in contiguous:
				toRemove.append(i)
		for i in toRemove:
			self.lowClassResidential.remove(i)
			self.map[i.box.minx][i.box.minz] = ("N", i)
		# Verifying continguousness of industrial chunks
		contiguous = self.getMaxSegment(self.industrial)
		toRemove = []
		for i in self.industrial:
			if i not in contiguous:
				toRemove.append(i)
		for i in toRemove:
			self.industrial.remove(i)
			self.map[i.box.minx][i.box.minz] = ("N", i)
		# Verifying continguousness of agricultural chunks
		contiguous = self.getMaxSegment(self.agricultural)
		toRemove = []
		for i in self.agricultural:
			if i not in contiguous:
				toRemove.append(i)
		for i in toRemove:
			self.agricultural.remove(i)
			self.map[i.box.minx][i.box.minz] = ("N", i)

	def getNumSegments(self, chunks):
		chunkType = self.map[chunks[0].box.minx][chunks[0].box.minz][0]
		seen = set()
		segments = []
		for chunk in chunks:
			if chunk in seen:
				continue
			# Run DFS from this chunk
			contiguous = set()
			openList = [chunk]
			while len(openList) > 0:
				current = openList.pop()
				if current in contiguous:
					continue
				seen.add(current)
				contiguous.add(current)
				if current.box.minx - 16 in self.map and self.map[current.box.minx - 16][current.box.minz][0] == chunkType:
					openList.append(self.map[current.box.minx - 16][current.box.minz][1])
				if current.box.minx + 16 in self.map and self.map[current.box.minx + 16][current.box.minz][0] == chunkType:
					openList.append(self.map[current.box.minx + 16][current.box.minz][1])
				if current.box.minz - 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz - 16][0] == chunkType:
					openList.append(self.map[current.box.minx][current.box.minz - 16][1])
				if current.box.minz + 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz + 16][0] == chunkType:
					openList.append(self.map[current.box.minx][current.box.minz + 16][1])
			segments.append(contiguous)
		return len(segments)

	def getSegments(self, chunks):
		entryPoints = {"C": set(), "I": set(), "A": set(), "H": set(), "L": set() }
		seen = set()
		segments = []
		for chunk in chunks:
			if chunk in seen:
				continue
			# Run DFS from this chunk
			districtsInContiguous = set()
			contiguous = set()
			contiguousSeen = set()
			openList = [chunk]
			while len(openList) > 0:
				current = openList.pop()
				if current in contiguous:
					continue
				seen.add(current)
				contiguous.add(current)
				contiguousSeen.add(current)
				# Getting entry points between different district types
				districtType = self.map[current.box.minx][current.box.minz][0]
				if districtType not in districtsInContiguous:
					districtsInContiguous.add(districtType)
					if len(districtsInContiguous) > 1:
						# Add an entry point to both bordering districts
						# Need to first find out which other district current came from
						if current.box.minx - 16 in self.map and self.map[current.box.minx - 16][current.box.minz][0] != districtType and self.map[current.box.minx - 16][current.box.minz][1] in contiguousSeen:
							otherType, otherChunk = self.map[current.box.minx - 16][current.box.minz] # Came from the left
							offset = randint(0, 15)
							entryPoints[otherType].add((current.box.minx - 1, current.box.minz + offset))
							entryPoints[districtType].add((current.box.minx, current.box.minz + offset))
						elif current.box.minx + 16 in self.map and self.map[current.box.minx + 16][current.box.minz][0] != districtType and self.map[current.box.minx + 16][current.box.minz][1] in contiguousSeen:
							otherType, otherChunk = self.map[current.box.minx + 16][current.box.minz] # Came from the right
							offset = randint(0, 15)
							entryPoints[otherType].add((current.box.minx + 16, current.box.minz + offset))
							entryPoints[districtType].add((current.box.minx + 15, current.box.minz + offset))
						elif current.box.minz - 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz - 16][0] != districtType and self.map[current.box.minx][current.box.minz - 16][1] in contiguousSeen:
							otherType, otherChunk = self.map[current.box.minx][current.box.minz - 16] # Came from the bottom
							offset = randint(0, 15)
							entryPoints[otherType].add((current.box.minx + offset, current.box.minz - 1))
							entryPoints[districtType].add((current.box.minx + offset, current.box.minz))
						elif current.box.minz + 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz + 16][0] != districtType and self.map[current.box.minx][current.box.minz + 16][1] in contiguousSeen:
							otherType, otherChunk = self.map[current.box.minx][current.box.minz + 16] # Came from the top
							offset = randint(0, 15)
							entryPoints[otherType].add((current.box.minx + offset, current.box.minz + 16))
							entryPoints[districtType].add((current.box.minx + offset, current.box.minz + 15))
				# Getting successors
				if current.box.minx - 16 in self.map and self.map[current.box.minx - 16][current.box.minz][0] != "N":
					openList.append(self.map[current.box.minx - 16][current.box.minz][1])
				if current.box.minx + 16 in self.map and self.map[current.box.minx + 16][current.box.minz][0] != "N":
					openList.append(self.map[current.box.minx + 16][current.box.minz][1])
				if current.box.minz - 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz - 16][0] != "N":
					openList.append(self.map[current.box.minx][current.box.minz - 16][1])
				if current.box.minz + 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz + 16][0] != "N":
					openList.append(self.map[current.box.minx][current.box.minz + 16][1])
			segments.append(contiguous)
		return segments, entryPoints

	def getMaxSegment(self, chunks):
		chunkType = self.map[chunks[0].box.minx][chunks[0].box.minz][0]
		seen = set()
		segments = []
		for chunk in chunks:
			if chunk in seen:
				continue
			# Run DFS from this chunk
			contiguous = set()
			openList = [chunk]
			while len(openList) > 0:
				current = openList.pop()
				if current in contiguous:
					continue
				seen.add(current)
				contiguous.add(current)
				if current.box.minx - 16 in self.map and self.map[current.box.minx - 16][current.box.minz][0] == chunkType:
					openList.append(self.map[current.box.minx - 16][current.box.minz][1])
				if current.box.minx + 16 in self.map and self.map[current.box.minx + 16][current.box.minz][0] == chunkType:
					openList.append(self.map[current.box.minx + 16][current.box.minz][1])
				if current.box.minz - 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz - 16][0] == chunkType:
					openList.append(self.map[current.box.minx][current.box.minz - 16][1])
				if current.box.minz + 16 in self.map[current.box.minx] and self.map[current.box.minx][current.box.minz + 16][0] == chunkType:
					openList.append(self.map[current.box.minx][current.box.minz + 16][1])
			segments.append(contiguous)
		maxSet = set()
		maxSize = 0
		for i in segments:
			if len(i) > maxSize:
				maxSize = len(i)
				maxSet = i
		return maxSet


	def assignChunk(self, chunk):
		x = chunk.box.minx
		z = chunk.box.minz
		if chunk.groundPercentage >= Genome.MIN_GROUND and self.map[x][z][0] == "N":
			possibilities = set()
			# Assign chunk to a district
			if x-1 in self.map:
				letter = self.map[x-1][z][0]
				if letter != "N":
					possibilities.add(letter)
			if x+1 in self.map:
				letter = self.map[x+1][z][0]
				if letter != "N":
					possibilities.add(letter)
			if z-1 in self.map[x]:
				letter = self.map[x][z-1][0]
				if letter != "N":
					possibilities.add(letter)
			if z+1 in self.map[x]:
				letter = self.map[x][z+1][0]
				if letter != "N":
					possibilities.add(letter)
			if len(possibilities) == 0:
				possibilities.add("C")
				possibilities.add("I")
				possibilities.add("A")
				possibilities.add("H")
				possibilities.add("L")
			district = choice(list(possibilities))
			self.map[x][z] = (district, chunk)
			if district == "C":
				self.commercial.append(chunk)
			elif district == "I":
				self.industrial.append(chunk)
			elif district == "A":
				self.agricultural.append(chunk)
			elif district == "H":
				self.highClassResidential.append(chunk)
			elif district == "L":
				self.lowClassResidential.append(chunk)


	def mutate(self, chunks):
		g = Genome()
		# Copying the map from the parent
		g.map = {}
		mapSize = 0
		for i in self.map:
			g.map[i] = {}
			for j in self.map[i]:
				g.map[i][j] = self.map[i][j]
				mapSize += 1
		# Copying the districts from the parent
		g.commercial = self.commercial[:]
		g.industrial = self.industrial[:]
		g.agricultural = self.agricultural[:]
		g.highClassResidential = self.highClassResidential[:]
		g.lowClassResidential = self.lowClassResidential[:]
		r = randint(1, ceil(mapSize * 0.2))
		for i in range(r):
			if random() < 0.5: # Add a chunk
				index = randint(1,5)
				if index == 1:
					if len(g.commercial) >= 1:
						chunkIndex = randint(0, len(g.commercial) - 1)
						chunk = g.getBorderChunk(g.commercial[chunkIndex], False)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						g.map[chunk.box.minx][chunk.box.minz] = ("C", chunk)
						g.commercial.append(chunk)
					else:
						g.verifyDistrictExistance(chunks)
				elif index == 2:
					if len(g.industrial) >= 1:
						chunkIndex = randint(0, len(g.industrial) - 1)
						chunk = g.getBorderChunk(g.industrial[chunkIndex], False)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						g.map[chunk.box.minx][chunk.box.minz] = ("I", chunk)
						g.industrial.append(chunk)
					else:
						g.verifyDistrictExistance(chunks)
				elif index == 3:
					if len(g.agricultural) >= 1:
						chunkIndex = randint(0, len(g.agricultural) - 1)
						chunk = g.getBorderChunk(g.agricultural[chunkIndex], False)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						g.map[chunk.box.minx][chunk.box.minz] = ("A", chunk)
						g.agricultural.append(chunk)
					else:
						g.verifyDistrictExistance(chunks)
				elif index == 4:
					if len(g.highClassResidential) >= 1:
						chunkIndex = randint(0, len(g.highClassResidential) - 1)
						chunk = g.getBorderChunk(g.highClassResidential[chunkIndex], False)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						g.map[chunk.box.minx][chunk.box.minz] = ("H", chunk)
						g.highClassResidential.append(chunk)
					else:
						g.verifyDistrictExistance(chunks)
				elif index == 5:
					if len(g.lowClassResidential) >= 1:
						chunkIndex = randint(0, len(g.lowClassResidential) - 1)
						chunk = g.getBorderChunk(g.lowClassResidential[chunkIndex], False)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						g.map[chunk.box.minx][chunk.box.minz] = ("L", chunk)
						g.lowClassResidential.append(chunk)
					else:
						g.verifyDistrictExistance(chunks)
			else: # Remove a chunk
				index = randint(1,5)
				if index == 1:
					if len(g.commercial) > 1:
						chunkIndex = randint(0, len(g.commercial) - 1)
						chunk = g.getBorderChunk(g.commercial[chunkIndex], True)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						if g.getNumSegments(g.commercial) > 1:
							g.map[chunk.box.minx][chunk.box.minz] = ("C", chunk)
							g.commercial.append(chunk)
				elif index == 2:
					if len(g.industrial) > 1:
						chunkIndex = randint(0, len(g.industrial) - 1)
						chunk = g.getBorderChunk(g.industrial[chunkIndex], True)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						if g.getNumSegments(g.industrial) > 1:
							g.map[chunk.box.minx][chunk.box.minz] = ("I", chunk)
							g.industrial.append(chunk)
				elif index == 3:
					if len(g.agricultural) > 1:
						chunkIndex = randint(0, len(g.agricultural) - 1)
						chunk = g.getBorderChunk(g.agricultural[chunkIndex], True)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						if g.getNumSegments(g.agricultural) > 1:
							g.map[chunk.box.minx][chunk.box.minz] = ("A", chunk)
							g.agricultural.append(chunk)
				elif index == 4:
					if len(g.highClassResidential) > 1:
						chunkIndex = randint(0, len(g.highClassResidential) - 1)
						chunk = g.getBorderChunk(g.highClassResidential[chunkIndex], True)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						if g.getNumSegments(g.highClassResidential) > 1:
							g.map[chunk.box.minx][chunk.box.minz] = ("H", chunk)
							g.highClassResidential.append(chunk)
				elif index == 5:
					if len(g.lowClassResidential) > 1:
						chunkIndex = randint(0, len(g.lowClassResidential) - 1)
						chunk = g.getBorderChunk(g.lowClassResidential[chunkIndex], True)
						g.setToNone(chunk.box.minx, chunk.box.minz)
						if g.getNumSegments(g.lowClassResidential) > 1:
							g.map[chunk.box.minx][chunk.box.minz] = ("L", chunk)
							g.lowClassResidential.append(chunk)
		return g

	def getBorderChunk(self, startingChunk, returnChunkOfStartingType):
		chunkType = self.map[startingChunk.box.minx][startingChunk.box.minz][0]
		# Performs BFS until it finds a chunk that is not the same district type
		openList = deque([startingChunk])
		closed = set()
		while len(openList) > 0:
			current = openList.popleft()
			if current in closed:
				continue
			closed.add(current)
			successors = [(current.box.minx-16, current.box.minz), (current.box.minx+16, current.box.minz), (current.box.minx, current.box.minz-16), (current.box.minx, current.box.minz+16)]
			for i in successors:
				if i[0] not in self.map or i[1] not in self.map[i[0]]:
					continue
				if self.map[i[0]][i[1]][1] in closed or self.map[i[0]][i[1]][1].groundPercentage < Genome.MIN_GROUND:
					continue
				if self.map[i[0]][i[1]][0] != chunkType:
					# Done
					if returnChunkOfStartingType:
						return current
					else:
						return self.map[i[0]][i[1]][1]
				openList.append(self.map[i[0]][i[1]][1])
		return current


	def crossover(self, other):
		g = Genome()
		# Denoting which districts will be taken from each parent
		while True:
			distsFrom1 = []
			distsFrom2 = []
			for i in ["C", "I", "A", "H", "L"]:
				if random() < 0.5:
					distsFrom1.append(i)
				else:
					distsFrom2.append(i)
			if len(distsFrom1) > 0 and len(distsFrom2) > 0:
				break
		# Copying the map from the parents
		g.map = {}
		for i in self.map:
			g.map[i] = {}
			for j in self.map[i]:
				if self.map[i][j][0] in distsFrom1:
					g.map[i][j] = self.map[i][j]
				elif other.map[i][j][0] in distsFrom2:
					g.map[i][j] = other.map[i][j]
				else:
					g.map[i][j] = ("N", self.map[i][j][1])
		# Copying the districts from the parent
		if "C" in distsFrom1:
			g.commercial = self.commercial[:]
		else:
			g.commercial = other.commercial[:]
		if "I" in distsFrom1:
			g.industrial = self.industrial[:]
		else:
			g.industrial = other.industrial[:]
		if "A" in distsFrom1:
			g.agricultural = self.agricultural[:]
		else:
			g.agricultural = other.agricultural[:]
		if "H" in distsFrom1:
			g.highClassResidential = self.highClassResidential[:]
		else:
			g.highClassResidential = other.highClassResidential[:]
		if "L" in distsFrom1:
			g.lowClassResidential = self.lowClassResidential[:]
		else:
			g.lowClassResidential = other.lowClassResidential[:]
		return g


	# Necessary for sorting
	def __lt__(self, other):
		return self.fitness < other.fitness




def getChunksAndDistricts(level, box):
	# Breaks up the selection box into chunks and performs an analysis on them
	chunks = []
	for (chunk, slices, point) in level.getChunkSlices(box):
		chunks.append(ChunkAnalysis(level, chunk, slices))

	# Analyzes distances to other resources
	maxScores = {"B": 1, "W": 1, "V": 1}
	for i in chunks:
		i.calculateResourceProximity(chunks, maxScores)

	numNonWaterChunks = 0
	for i in chunks:
		if i.groundPercentage >= Genome.MIN_GROUND:
			numNonWaterChunks += 1

	# Initializing the population
	mu = 20 # Num elite
	lamb = 30 # Num children
	population = [Genome() for i in range(mu + lamb)]
	for i in population:
		i.randomize(chunks)

	# Simulating generations
	for i in range(20):
		# Fitness evaluation
		for j in population:
			j.calcFitness(maxScores, chunks, numNonWaterChunks)
		population.sort()
		# Removing worst of the population
		population = population[lamb:]
		# Generating offspring
		for j in range(lamb):
			parent = choice(population)
			if random() < 0.8: # Mutation
				population.append(parent.mutate(chunks))
			else: # Crossover
				otherParent = parent
				while otherParent == parent:
					otherParent = choice(population)
				population.append(parent.crossover(otherParent))
		
	# Selecting the most fit genome after all the generations are over
	for j in population:
		j.calcFitness(maxScores, chunks, numNonWaterChunks)
	population.sort()
	mostFit = population[-1]

	segments, entryPoints = mostFit.getSegments(mostFit.commercial + mostFit.industrial + mostFit.agricultural + mostFit.highClassResidential + mostFit.lowClassResidential)

	return chunks, [mostFit.commercial, mostFit.industrial, mostFit.agricultural, mostFit.highClassResidential, mostFit.lowClassResidential], segments, mostFit.map, entryPoints

