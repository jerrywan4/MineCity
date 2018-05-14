import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
import random
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import Queue

import utilityFunctions
from helper import *
from ChunkAnalysis import *

def build(level, chunks, function):
    flatGround(level,chunks)
    buildBase(level, chunks, function)


def buildBase(level, chunks, function):
    for chunk in chunks:
        minx = chunk.box.minx;
        minz = chunk.box.minz;
        maxx = chunk.box.maxx;
        maxz = chunk.box.maxz;

        if function == "Farm":
            width = 9;
            length = 7;
        elif function == "SmallHouse":
            width = 12;
            length = 10;
        else:
            #No legal buildings
            continue;

        backup = [];

        
        for xstart in xrange(minx, maxx-width):
            for zstart in xrange(minz, maxz-length):
                maxh = 0;
                minh = 256;

                bk = False;
                for x in xrange(xstart, xstart + width):
                    for z in xrange(zstart, zstart + length):
                        if level.blockAt(x,getGroundYPos(x,z),z) in [8,9]:
                            bk = True;
                            break;
                        maxh = max(maxh, getGroundYPos(x,z))
                        minh = min(minh, getGroundYPos(x,z))
                    if bk:
                        break;

                if bk:
                    continue;
                mid = (minh+maxh)/2;
                total = 0;
                for x in xrange(xstart, xstart + width):
                    for z in xrange(zstart, zstart + length):
                        total += abs(mid - getGroundYPos(x,z));
                if function != "Farm":
                    total /= 2;
                if total <= width * length:
                    if function == "SmallHouse":
                        print total;
                    backup.append((xstart,zstart,mid));


        if len(backup)==0:
            print("No!!!",function)
            return ;

        (xstart,zstart,mid) = backup[randint(0,len(backup)-1)];
        


        if function == "Farm":
            buildFarm(level,xstart,zstart,mid);
        elif function == "SmallHouse":
            buildHouse1(level,xstart,zstart,mid,(5,1));
            
def buildHouse1(level, xstart, zstart, height, material):
    width = 12;
    length = 10;

    for x in xrange(xstart, xstart+width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(height+1,he+1):
                setBlock(level,(0,0),x,y,z);
            setHeight(level,x,he,z);



    table = ((xstart+1,zstart+1),(xstart+1,zstart+length-2),(xstart+width-2,zstart+1),(xstart+width-2,zstart+length-2));
    
    for (x,z) in table:
        he = getGroundYPos(x,z)
        for y in xrange(he+1,height+1):
            setBlock(level, material, x, y, z)

    #ground        
    for x in xrange(xstart + 1, xstart + width - 1):
        for z in xrange(zstart + 1, zstart + length - 1):
            setBlock(level, material,x,height+1,z)
    #wall
    for x in xrange(xstart + 1, xstart + width - 1):
        for z in (zstart + 1, zstart + length - 2):
            for he in xrange(2,5):
                setBlock(level, material, x, height + he,z);

    for x in (xstart+1,xstart+width-2):
        for z in xrange(zstart+2,zstart+length-2):
            for he in xrange(2,5):
                setBlock(level, material, x, height + he, z);

    #roof

    for x in (xstart,xstart+width-1):
        for i in range(3):
            for z in xrange(zstart + i + 1, zstart + length - 1 - i):
                setBlock(level, (5,1), x, height + 4 + i,z)
    
    for x in xrange(xstart,xstart+width):
        setBlock(level, (134,3),x,height+4,zstart+length-1)
        setBlock(level, (134,3),x,height+5,zstart+length-2)
        setBlock(level, (134,3),x,height+6,zstart+length-3)
        setBlock(level, (134,2),x,height+5,zstart+1)
        setBlock(level, (134,2),x,height+6,zstart+2)
        setBlock(level, (134,2),x,height+4,zstart) 


    for x in xrange(xstart + 1, xstart + width - 1):
        for z in xrange(zstart + 3,zstart + length -3):
            setBlock(level,(5,1),x,height+6,z);

    #window
    x = xstart + 1;
    z = randint(zstart + 2,zstart + length - 3)

    setBlock(level, (20,0),x,height+3,z);
                        
    x = xstart + width - 2;
    z = randint(zstart + 2,zstart  + length -3)

    setBlock(level, (20,0),x,height+3,z);

    x = randint(xstart + 2,xstart + width - 3);
    z = zstart + 1;

    setBlock(level, (20,0),x,height+3,z);

    #door
    x = randint(xstart + 2,xstart + width - 3);
    z = zstart + length - 2;

                  
    setBlock(level, (64,3),x,height+2,z);
    setBlock(level, (64,9),x,height+3,z);

                
    while (level.blockAt(x,height+1,z+1)==0):
        setBlock(level, (134,3),x,height+1,z+1);
        z+=1;
        height-=1;
        if level.blockAt(x,height+1,z)==0:
            setBlock(level, (134,6),x,height+1,z);

def buildFarm(level, xstart, zstart, mid):
    width = 9;
    length = 7;
    for x in xrange(xstart, xstart + width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(he,mid):
                setBlock(level,(3,0),x,y,z);

            for y in xrange(mid+1,he+1):
                setBlock(level, (0,0),x,y,z);
            if (x == xstart) or (x == xstart + width -1) or (z == zstart) or (z == zstart + length - 1):
                setBlock(level, (17,0), x, mid+1, z);
            else:
                if (z == zstart + 3):
                    setBlock(level, (9,0),x,mid+1,z)
                else:
                    setBlock(level, (60,0), x, mid+1, z)
                    setBlock(level, (59,3), x, mid+2, z)

                
    

def flatGround(level,chunks):
    for chunk in chunks:
        for x in xrange(chunk.box.minx,chunk.box.maxx):
            for z in xrange(chunk.box.minz,chunk.box.maxz):
                he = getGroundYPos(x,z);
                for y in xrange(he+1,256):
                    setBlock(level, (0,0), x, y , z)
