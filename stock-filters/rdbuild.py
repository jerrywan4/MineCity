import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import random
import numpy
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import Queue

import utilityFunctions
from helper import *
from ChunkAnalysis import *

import structure
import traceback

_buildLoc = {};
_used = {}
_score = {};
boundary = [];



def findRoad(level,startx,startz,minx,maxx,minz,maxz):

    bfs = [];
    bfs.append([startx,startz,-1]);
    f = 0;
    e = 1;
    _used[startx][startz]=-1;
    direct = [(-1,0),(1,0),(0,-1),(0,1)]
    ans = [];
    while (f<e):
        x = bfs[f][0];
        z = bfs[f][1];
        last = bfs[f][2];
        #print(x-minx,z-minz);
        for i in range(4):
            (x0,z0)=direct[i];
            if x0+x<minx:
                continue;
            if x0+x>=maxx:
                continue;
            if z0+z<minz:
                continue;
            if z0+z>=maxz:
                continue;
            if abs(getGroundYPos(x,z)-getGroundYPos(x0+x,z0+z))>3:
                continue;
            #print(x0+x,z0+z,_used[x0+x][z0+z],_buildLoc[x0+x][z0+z])
            
            if _used[x0+x][z0+z] in [0,2,5] and _buildLoc[x0+x][z0+z]==0:

                bfs.append([x0+x,z0+z,f]);
                _buildLoc[x0+x][z0+z] = 1;
                e+=1;
            elif _used[x0+x][z0+z]==10 and abs(getGroundYPos(x,z)-getGroundYPos(x0+x,z0+z)) <= 1:
                ans.append([x0+x,z0+z]);
                last = f;
                while (last!=-1):
                    ansx = bfs[last][0];
                    ansz = bfs[last][1];
                    last = bfs[last][2];
                    ans.append([ansx,ansz]);
                break;
            if len(ans)>0:
                break;
        if len(ans)>0:
            break;
                


        f+=1;

    for i in range(len(bfs)):
        x = bfs[i][0];
        z = bfs[i][1];
        _buildLoc[x][z] = 0;


    #if len(ans)>0:
    #    print("get");
    #else:
    #    print("no road")
    return ans;

def buildRoad(level, road, minx, maxx, minz, maxz):

    direct = [(0,1),(-1,0),(0,-1),(1,0)]
    stair = [2,1,3,0]
    
    if (len(road)==0):
        print("no road");
        return;

    for i in xrange(1,len(road)-1):
        block = road[i];
        x = block[0];
        z = block[1];
        y = getGroundYPos(x,z)
        setBlock(level,(43,5),x,y,z)

        for y0 in xrange(y+1,min(y+21,256)):
            if y0-y <= 5 or level.blockAt(x,y0,z) in [17,162]:
                setBlock(level,(0,0),x,y0,z);
        
            
        b1 = road[i-1];
        b2 = road[i+1];

        for order in range(4):
            if direct[order] == (x-b1[0],z-b1[1]):
                break;

        y1 = getGroundYPos(b1[0],b1[1]);
        y2 = getGroundYPos(b2[0],b2[1]);

    
        
        if b1[0]+b2[0] == 2*x and b1[1]+b2[1] == 2*z:
            if y < min(y1,y2):
                setBlock(level,(43,5),x,y1,z);
                y = y1;
            elif y > max(y1,y2):
                for y0 in xrange(y1,y+1):
                    setBlock(level,(0,0),x,y0,z);
                setBlock(level,(43,5),x,y1,z);
                y = y1;
            if y<y1:
                if y1-y == 1:
                    setBlock(level,(109,stair[(order+2)%4]),x,y+1,z)
                    setHeight(level,x,y,z);
                else:
                    for y0 in xrange(y+1,y1+1):
                        setBlock(level,(65,chest[order]),x,y0,z);
                    setHeight(level,x,y,z);
            elif y>y1:
                if y-y1 == 1:              
                    setBlock(level,(109,stair[order]),x,y,z);
                else:
                    for y0 in xrange(y1+1,y+1):
                        setBlock(level,(65,chest[(order+2)%4]),b1[0],y0,b1[1]);
                    setHeight(level,b1[0],y1,b2[0]);
        else:
            
            if y<y1:


                for y0 in xrange(y+1,y1+1):
                    setBlock(level,(65,chest[order]),x,y0,z);
                setHeight(level,x,y,z);
            elif y>y1:

                for y0 in xrange(y1+1,y+1):
                    setBlock(level,(65,chest[(order+2)%4]),b1[0],y0,b1[1]);
                setHeight(level,b1[0],y0,b1[1]);



            
        for x0 in xrange(x-5,x+6):
            for z0 in xrange(z-5,z+6):
                if minx<=x0<maxx:
                    if minz<=z0<maxz:
                        _score[x0][z0] += 25;


        
        _used[x][z]=10;

    block = road[len(road)-1];
    x = block[0];
    z = block[1];
    y = getGroundYPos(x,z)
    setBlock(level,(43,5),x,y,z)
    b1 = road[len(road)-2];
    y1 = getGroundYPos(b1[0],b1[1]);


    for order in range(4):
        if direct[order] == (x-b1[0],z-b1[1]):
            break;
    if y < y1:
        setBlock(level,(43,5),x,y+1,z)
    if level.blockAt(x,y,z) in stairId:
        y-=1;
    if y<y1:
        

        for y0 in xrange(y+1,y1+1):
            setBlock(level,(65,chest[order]),x,y0,z);
        setHeight(level,x,y,z);
    elif y>y1:  
        for y0 in xrange(y1+1,y+1):
            setBlock(level,(65,chest[(order+2)%4]),b1[0],y0,b1[1]);   
def HighBuild(level, chunks, maxwidth,maxlength,entrys):
    wood, stone = getMaterial(level,chunks)
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    
    init(level,minx,maxx,minz,maxz,chunks);
    
    #print(roadx,getGroundYPos(roadx,roadz),roadz)
    
    print("init")
    #for x in xrange(minx,maxx):
    #    for z in xrange(minz,maxz):
    #        print _score[x][z],
    #    print();

    loc = locate(level, minx,maxx,minz,maxz,6,6);
    snow = flatGround(level,loc)
    height = getGroundYPos(loc[0],loc[1]);
    buildWell(level,loc[0],loc[1],height,stone,wood)
    
    
    while(True):
        loc = locate(level,minx,maxx,minz,maxz,maxwidth,maxlength);
        if loc[0]==65535:
            maxwidth-=1;
            maxlength-=1;
            loc = [];
            continue;
        
        if loc[2] % 2==0:
            loc[2] -= 1;
        if loc[3] % 2==0:
            loc[3] -= 1;
        break;

    for x in xrange(loc[0],loc[0]+loc[2]):
        for z in xrange(loc[1],loc[1]+loc[3]):
            _used[x][z] = 1;

    height = getGroundYPos(loc[0],loc[1]);

    order = 0;
    length = 1000;
    toBuild = [];

    for i in range(4):
        if (i == 0):
            startx = loc[0] + loc[2]/2;
            startz = loc[1] + loc[3] - 1;
        elif (i == 1):
            startx = loc[0];
            startz = loc[1] + loc[3]/2;
        elif (i == 2):
            startx = loc[0] + loc[2]/2;
            startz = loc[1];
        elif (i == 3):
            startx = loc[0] + loc[2] - 1
            startz = loc[1] + loc[3]/2;
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        
        
        
        factor = abs(height-getGroundYPos(startx,startz));
        if factor == 0:
            factor = 1;
        
        if len(toBuild)==0:
            length = len(road)*factor+2**factor;
            order = i;
            toBuild = road;
        elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
            length = len(road)*factor+2**factor;
            order = i;
            toBuild = road;

    if (len(toBuild)>0):
        flatGround(level,loc)
    
        buildRoad(level,toBuild,minx,maxx,minz,maxz)
        
        buildBase(level,loc,"Main",wood,stone,order)

    for b in range(20):
        loc = locate(level,minx,maxx,minz,maxz,randint(9,15),randint(9,15));
        if (loc[0]==65535):
            break;
        
        if loc[2] % 2==0:
            loc[2] -= 1;
        if loc[3] % 2==0:
            loc[3] -= 1;
        for x in xrange(loc[0],loc[0]+loc[2]):
            for z in xrange(loc[1],loc[1]+loc[3]):
                _used[x][z] = 1;
        height = getGroundYPos(loc[0],loc[1]);
        order = 0;
        length = 1000;
        toBuild = [];
        
        for i in range(4):
            if (i == 0):
                startx = loc[0] + loc[2]/2;
                startz = loc[1] + loc[3] - 1;
            elif (i == 1):
                startx = loc[0];
                startz = loc[1] + loc[3]/2;
            elif (i == 2):
                startx = loc[0] + loc[2]/2;
                startz = loc[1];
            elif (i == 3):
                startx = loc[0] + loc[2] - 1
                startz = loc[1] + loc[3]/2;           
            road = findRoad(level,startx,startz,minx,maxx,minz,maxz);

            
            factor = abs(height-getGroundYPos(startx,startz));
            if factor == 0:
                factor = 1;
            if len(toBuild)==0:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
            elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
        
        #print(toBuild)
        if (len(toBuild)>0):
            flatGround(level,loc)
            buildRoad(level,toBuild,minx,maxx,minz,maxz)
                
            buildBase(level,loc,"Simple",wood,stone,order)    

    for i in xrange(0,len(entrys)):
        (startx,startz) = entrys[i];
        y = getGroundYPos(startx,startz)
        setBlock(level,(43,5),startx,y,startz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),startx,y0,startz);
        setHeight(level,startx,y,startz);
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        buildRoad(level,road,minx,maxx,minz,maxz);
    #buildBigHouse
    
    #flatGround(level,loc)
    #buildBase(level,loc,"Main",3)

           
def LowBuild(level, chunks, maxwidth,maxlength,entrys):
    wood, stone = getMaterial(level,chunks)
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    
    init(level,minx,maxx,minz,maxz,chunks);
    
    loc = locate(level, minx,maxx,minz,maxz,6,6);
    flatGround(level,loc)
    height = getGroundYPos(loc[0],loc[1]);
    buildWell(level,loc[0],loc[1],height,stone,wood)
    
    
    #for x in xrange(minx,maxx):
    #    for z in xrange(minz,maxz):
    #        print _score[x][z],
    #    print();

    for b in range(20):
        loc = locate(level,minx,maxx,minz,maxz,randint(7,11),randint(7,11));
        if (loc[0]==65535):
            break;
        
        if loc[2] % 2==0:
            loc[2] -= 1;
        if loc[3] % 2==0:
            loc[3] -= 1;
            
        for x in xrange(loc[0],loc[0]+loc[2]):
            for z in xrange(loc[1],loc[1]+loc[3]):
                _used[x][z] = 1;
        height = getGroundYPos(loc[0],loc[1]);
        order = 0;
        length = 1000;
        toBuild = [];
        
        for i in range(4):
            if (i == 0):
                startx = loc[0] + loc[2]/2;
                startz = loc[1] + loc[3]-1;
            elif (i == 1):
                startx = loc[0];
                startz = loc[1] + loc[3]/2;
            elif (i == 2):
                startx = loc[0] + loc[2]/2;
                startz = loc[1];
            elif (i == 3):
                startx = loc[0] + loc[2]-1
                startz = loc[1] + loc[3]/2;           
            road = findRoad(level,startx,startz,minx,maxx,minz,maxz);

            
            factor = abs(height-getGroundYPos(startx,startz));
            if factor == 0:
                factor = 1;
            if len(toBuild)==0:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
            elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
                
        #print(toBuild)
        if (len(toBuild)>0):
            flatGround(level,loc)
            buildRoad(level,toBuild,minx,maxx,minz,maxz)
                
            buildBase(level,loc,"Simple",wood,wood,order)    

    for i in xrange(0,len(entrys)):
        (startx,startz) = entrys[i];
        y = getGroundYPos(startx,startz)
        setBlock(level,(43,5),startx,y,startz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),startx,y0,startz);
        setHeight(level,startx,y,startz);
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        buildRoad(level,road,minx,maxx,minz,maxz);

    
    #buildBigHouse
    
    #flatGround(level,loc)
    #buildBase(level,loc,"Main",3)

def agriBuild(level, chunks, entrys):
    wood, stone = getMaterial(level,chunks)
    (roadx,roadz) = entrys[0]
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    
    init(level,minx,maxx,minz,maxz,chunks);
    _used[roadx][roadz]=10;
    #print(roadx,getGroundYPos(roadx,roadz),roadz)
    y = getGroundYPos(roadx,roadz)
    setBlock(level,(43,5),roadx,y,roadz);
    for y0 in xrange(y+1,y+6):
        setBlock(level,(0,0),roadx,y0,roadz);
    setHeight(level,roadx,y,roadz);
    
    #for x in xrange(minx,maxx):
    #    for z in xrange(minz,maxz):
    #        print _score[x][z],
    #    print();

    for b in range(40):
        loc = locate(level,minx,maxx,minz,maxz,7,9);
        if (loc[0]==65535):
            break;
        
        #if loc[2] % 2==0:
        #    loc[2] -= 1;
        #if loc[3] % 2==0:
        #    loc[3] -= 1;
        for x in xrange(loc[0],loc[0]+loc[2]):
            for z in xrange(loc[1],loc[1]+loc[3]):
                _used[x][z] = 1;
        height = getGroundYPos(loc[0],loc[1]);
        order = 0;
        length = 1000;
        toBuild = [];
        
        for i in range(4):
            if (i == 0):
                startx = loc[0] + loc[2]/2;
                startz = loc[1] + loc[3] - 1;
            elif (i == 1):
                startx = loc[0];
                startz = loc[1] + loc[3]/2;
            elif (i == 2):
                startx = loc[0] + loc[2]/2;
                startz = loc[1];
            elif (i == 3):
                startx = loc[0] + loc[2]-1
                startz = loc[1] + loc[3]/2;       
            road = findRoad(level,startx,startz,minx,maxx,minz,maxz);

            
            factor = abs(height-getGroundYPos(startx,startz));
            if factor == 0:
                factor = 1;
            if len(toBuild)==0:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
            elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
                
        #print(toBuild)
        if (len(toBuild)>0):
            flatGround(level,loc)
            buildRoad(level,toBuild,minx,maxx,minz,maxz)
                
            buildAgriBase(level,loc,"Farm",order,wood)    

    for i in xrange(1,len(entrys)):
        (startx,startz) = entrys[i];
        y = getGroundYPos(startx,startz)
        setBlock(level,(43,5),startx,y,startz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),startx,y0,startz);
        setHeight(level,startx,y,startz);
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        buildRoad(level,road,minx,maxx,minz,maxz);


    
    #buildBigHouse
    
    #flatGround(level,loc)
    #buildBase(level,loc,"Main",3)             

def idBuild(level, chunks, entrys):
    wood, stone = getMaterial(level,chunks)
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    
    init(level,minx,maxx,minz,maxz,chunks);
    
    
    loc = locate(level, minx,maxx,minz,maxz,6,6);
    if (loc[0]!=65535):
        flatGround(level,loc)
        height = getGroundYPos(loc[0],loc[1]);
        buildWell(level,loc[0],loc[1],height,stone,wood)
    else:
        (roadx,roadz) = entrys[0]
        y = getGroundYPos(roadx,roadz)
        setBlock(level,(43,5),roadx,y,roadz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),roadx,y0,roadz);
        setHeight(level,roadx,y,roadz);
        _used[roadx][roadz]=10;
    
    #for x in xrange(minx,maxx):
    #    for z in xrange(minz,maxz):
    #        print _score[x][z],
    #    print();

    houses = []
    houses.append(structure.butcherBox(stone,wood))
    houses.append(structure.smithBox(stone,wood))

    
    
    for b in range(6):
        house = houses[b % 2];
        loc1 = locate(level,minx,maxx,minz,maxz,len(house),len(house[0]));
        loc2 = locate(level,minx,maxx,minz,maxz,len(house[0]),len(house));
        if (loc1[0]==65535) and (loc2[0]==65535):
            break;
        locs = [loc1,loc2,loc1,loc2];
        toBuild = [];
        chose = -1;
        ent = [];
        for x in range(len(house)):
            for z in range(len(house[0])):
                if house[x][z][0][0] in stairId:
                    ent = [x,z];
                    break;
        if ent == []:
            ent = [len(house[0])/2,len(house)];
        for i in range(4):
            loc = locs[i];
            if loc[0] == 65535:
                continue;
            if (i==0):
                startx = loc[0]+ent[0];
                startz = loc[1]+ent[1];
            elif (i==1):
                startx = loc[0]+loc[2]-ent[1]-1;
                startz = loc[1]+ent[0];
            elif (i==2):
                startx = loc[0]+loc[2]-1-ent[0];
                startz = loc[1]+loc[3]-ent[1]-1;
            elif (i==3):
                startx = loc[0]+ent[1];
                startz = loc[1]+loc[3]-1-ent[0]

            for x in xrange(loc[0],loc[0]+loc[2]):
                for z in xrange(loc[1],loc[1]+loc[3]):
                    _used[x][z] = 1;
            road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
            for x in xrange(loc[0],loc[0]+loc[2]):
                for z in xrange(loc[1],loc[1]+loc[3]):
                    _used[x][z] = 0;

            factor = abs(height-getGroundYPos(startx,startz));
            if factor == 0:
                factor = 1;
            if len(toBuild)==0:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
            elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
        if (len(toBuild)>0):
            flatGround(level,locs[order])
            height = getGroundYPos(locs[order][0],locs[order][1]);

            buildRoad(level,toBuild,minx,maxx,minz,maxz);
            
            buildHouse(level,locs[order][0],locs[order][1],locs[order][2],locs[order][3],height,house,order);
        else:
            for x in xrange(loc1[0],loc1[0]+loc1[2]):
                for z in xrange(loc1[1],loc1[1]+loc1[3]):
                    _used[x][z] = 2;
            for x in xrange(loc2[0],loc2[0]+loc2[2]):
                for z in xrange(loc2[1],loc2[1]+loc2[3]):
                    _used[x][z] = 2;        

    for i in xrange(0,len(entrys)):
        (startx,startz) = entrys[i];
        if (_used[startx][startz] == 10):
            continue;
        y = getGroundYPos(startx,startz)
        setBlock(level,(43,5),startx,y,startz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),startx,y0,startz);
        setHeight(level,startx,y,startz);
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        buildRoad(level,road,minx,maxx,minz,maxz);

def coBuild(level, chunks, entrys):
    wood, stone = getMaterial(level,chunks)
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    
    init(level,minx,maxx,minz,maxz,chunks);
    
    
    loc = locate(level, minx,maxx,minz,maxz,6,6);
    if (loc[0]!=65535):
        flatGround(level,loc)
        height = getGroundYPos(loc[0],loc[1]);
        buildWell(level,loc[0],loc[1],height,stone,wood)
    else:
        (roadx,roadz) = entrys[0]
        y = getGroundYPos(roadx,roadz)
        setBlock(level,(43,5),roadx,y,roadz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),roadx,y0,roadz);
        setHeight(level,roadx,y,roadz);
        _used[roadx][roadz]=10;
    
    
    #for x in xrange(minx,maxx):
    #    for z in xrange(minz,maxz):
    #        print _score[x][z],
    #    print();

    houses = []
    houses.append(structure.churchBox(stone,wood))
    houses.append(structure.libraryBox(stone,wood))
    houses.append(structure.libraryBox(stone,wood))
    
    
    
    for house in houses:
        
        loc1 = locate(level,minx,maxx,minz,maxz,len(house),len(house[0]));
        loc2 = locate(level,minx,maxx,minz,maxz,len(house[0]),len(house));

        if (loc1[0]==65535) and (loc2[0]==65535):
            break;
        
        locs = [loc1,loc2,loc1,loc2];
        toBuild = [];
        chose = -1;
        ent = [];
        for x in range(len(house)):
            for z in range(len(house[0])):
                if house[x][z][0][0] in stairId:
                    ent = [x,z];
                    break;
        if ent == []:
            ent = [len(house[0])/2,len(house)];
        for i in range(4):
            loc = locs[i];
            if (loc[0] == 65535):
                continue;
            if (i==0):
                startx = loc[0]+ent[0];
                startz = loc[1]+ent[1];
            elif (i==1):
                startx = loc[0]+loc[2]-ent[1]-1;
                startz = loc[1]+ent[0];
            elif (i==2):
                startx = loc[0]+loc[2]-1-ent[0];
                startz = loc[1]+loc[3]-ent[1]-1;
            elif (i==3):
                startx = loc[0]+ent[1];
                startz = loc[1]+loc[3]-1-ent[0]

            for x in xrange(loc[0],loc[0]+loc[2]):
                for z in xrange(loc[1],loc[1]+loc[3]):
                    _used[x][z] = 1;
            road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
            for x in xrange(loc[0],loc[0]+loc[2]):
                for z in xrange(loc[1],loc[1]+loc[3]):
                    _used[x][z] = 0;

            factor = abs(height-getGroundYPos(startx,startz));
            if factor == 0:
                factor = 1;
            if len(toBuild)==0:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
            elif (len(road)*factor>0) and (len(road)*factor+2**factor)<length:
                length = len(road)*factor+2**factor;
                order = i;
                toBuild = road;
        flatGround(level,locs[order])
        height = getGroundYPos(locs[order][0],locs[order][1]);

        buildRoad(level,toBuild,minx,maxx,minz,maxz);
        
        buildHouse(level,locs[order][0],locs[order][1],locs[order][2],locs[order][3],height,house,order);
        

    for i in xrange(0,len(entrys)):
        (startx,startz) = entrys[i];
        if (_used[startx][startz] == 10):
            continue;
        y = getGroundYPos(startx,startz)
        setBlock(level,(43,5),startx,y,startz);
        for y0 in xrange(y+1,y+6):
            setBlock(level,(0,0),startx,y0,startz);
        setHeight(level,startx,y,startz);
        road = findRoad(level,startx,startz,minx,maxx,minz,maxz);
        buildRoad(level,road,minx,maxx,minz,maxz);


def init(level,minx,maxx,minz,maxz,chunks):
    random()
    boundary.append(minx);
    boundary.append(maxx);
    boundary.append(minz);
    boundary.append(maxx);
    
    for x in xrange(minx,maxx):
        _buildLoc[x]={};
        for z in xrange(minz,maxz):
            _buildLoc[x][z]= 0;
            
    for x in xrange(minx,maxx):
        _used[x]={};
        _score[x]={};
        for z in xrange(minz,maxz):
            _used[x][z]=1;
            _score[x][z] = 0.0;
            

    for chunk in chunks:
        for x in xrange(chunk.box.minx,chunk.box.maxx):
            for z in xrange(chunk.box.minz,chunk.box.maxz):
                if level.blockAt(x,getGroundYPos(x,z),z) in [8,9,10,11,79,174,212]:
                    _used[x][z]=5;
                    continue
                else:
                    _used[x][z]=0;
                    hei=0.0
                    for x0 in xrange(-2,3):
                        for z0 in xrange(-2,3):
                            if x0+x<minx:
                                hei += 1000000;
                                continue;
                            if x0+x>=maxx:
                                hei += 1000000;
                                continue;
                            if z0+z<minz:
                                hei += 1000000;
                                continue;
                            if z0+z>=maxz:
                                hei += 1000000;
                                continue;
                            hei += getGroundYPos(x+x0,z+z0);
                    hei /= 25;
                    for x0 in xrange(-2,3):
                        for z0 in xrange(-2,3):
                            if x0+x<minx:
                                he  = 1000000;
                            elif x0+x>=maxx:
                                he = 1000000;
                                continue;
                            elif z0+z<minz:
                                he = 1000000;
                                continue;
                            elif z0+z>=maxz:
                                he += 1000000;
                            else:
                                he = getGroundYPos(x+x0,z+z0)
                            _score[x][z] -= (he-hei)**2 / 25;
                                
                    
                
                

    

def flatGround(level,loc):
    xstart = loc[0];
    zstart = loc[1];
    width = loc[2];
    length = loc[3]
    snow = False;
    for x in xrange(xstart,xstart+width):
        for z in xrange(zstart,zstart+length):
            for y in xrange(255,-1,-1):
                if level.blockAt(x,y,z)==78:
                    snow = True;
                    break;
                if level.blockAt(x,y,z)!=0:
                    break;
            if snow:
                break;
        if snow:
            break;

    xmin = loc[0];
    zmin = loc[1];
    xmax = loc[2]+xmin;
    zmax = loc[3]+zmin;
    hmin = 255;
    hmax = 0;
    for x in range(xmin-4,xmax+4):
        if not (x in _used):
            continue;
        for z in range(zmin-4,zmax+4):
            if not (z in _used[x]):
                continue;
            if xmin <= x < xmax and zmin <=z < zmax:
                _used[x][z]=1;
            else:
                _used[x][z]=2;
    for x in xrange(xmin,xmax):
        for z in xrange(zmin,zmax):
            deleteTree(level,x,z);
            he = getGroundYPos(x,z);
            for y in xrange(he+1,256):
                setBlock(level, (0,0), x, y , z)
            hmin = min(hmin,he);
            hmax = max(hmax,he);
    blocksmin = 65536;
    height = -1;
    for t in xrange(hmin,hmax+1):
        total = 0;
        for x in xrange(xmin,xmax):
            for z in xrange(zmin,zmax):
                total += abs(t-getGroundYPos(x,z))
        if total < blocksmin:
            blocksmin=total
            height = t;
    if height >-1:
        for x in xrange(xmin,xmax):
            for z in xrange(zmin,zmax):
                he = getGroundYPos(x,z);
                if he<=height:
                    if level.blockAt(x,he,z)==2:
                        setBlock(level,(3,1),x,he,z)
                    for y in xrange(he+1,height+1):
                        setBlock(level,(3,1),x,y,z);
                elif he>height:
                    for y in xrange(height+1,he+1):
                        setBlock(level,(0,0),x,y,z);
                    if x in (xmin,xmax-1) or z in (zmin,zmax-1):
                        setBlock(level,(2,0),x,height,z);
    
    if snow:
        for x in xrange(xstart,xstart+width):
            for z in xrange(zstart,zstart+length):
                y = getGroundYPos(x,z)
                setBlock(level,(78,0),x,y+1,z);
                setHeight(level,x,y,z);

    
def locate(level,minx,maxx,minz,maxz,width, length):
    maxScore = 0.0;
    locx=65535;
    locz=65535;
    midx = (minx*2+width-1)/2;

    midz = (minz*2+length-1)/2;

    usedCounts=0;
    
    for x in xrange(minx,maxx-width):
        currentScore = 0.0;
        usedCounts=0;
        for tx in xrange(x,x+width):
            for tz in range(minz,minz+length-1):
                if _used[tx][tz]==0:
                    currentScore += _score[tx][tz];
                else:
                    currentScore -= 1000000*25;
                    usedCounts +=1;
                
        for z in xrange(minz,maxz-length):
            for tx in xrange(x,x+width):
                if _used[tx][z+length-1]==0:
                    currentScore += _score[tx][z+length-1];
                else:
                    currentScore -= 1000000*25;
                    usedCounts +=1;
            #print(currentScore,maxScore);
            if usedCounts==0:
                if locx == 65535:
                    maxScore = currentScore;
                    locx = x;
                    locz = z;
                elif currentScore > maxScore:
                    
                    maxScore = currentScore;
                    locx = x;
                    locz = z;
                elif currentScore == maxScore:
                    if abs(locx-midx)+abs(locz-midz) > abs((minx*2+width-1)/2-midx) + abs((minz*2+length-1)/2-midz):
                        locx = x;
                        locz = z;
            for tx in xrange(x,x+width):
                if _used[tx][z]==0:
                    currentScore -= _score[tx][z];
                else:
                    currentScore += 1000000*25;
                    usedCounts -= 1
        

    loc = [locx, locz, width, length, maxScore]
    return loc;    
                    
                            



#def buildHighBase(level, loc, houseType, order):
#    minx = loc[0];
#    minz = loc[1];
#    maxx = loc[2]+minx;
#    maxz = loc[3]+minz;
#    width = loc[2];
#    length= loc[3];
#    height = 0;


    
#    for x in xrange(minx,maxx):
#        for z in xrange(minz,maxz):
#            height = max(height,getGroundYPos(x,z))

#    buildHouse(level,minx,minz,width,length,height,(17,0),(24,0),houseType,order);


def buildBase(level, loc, houseType, material1, material2, order):
    minx = loc[0];
    minz = loc[1];
    maxx = loc[2]+minx;
    maxz = loc[3]+minz;
    width = loc[2];
    length= loc[3];
    height = 0;


    
    for x in xrange(minx,maxx):
        for z in xrange(minz,maxz):
            height = max(height,getGroundYPos(x,z))

    w1= width;
    l1 = length;

    if order % 2 == 1:
        w1 = length;
        l1 = width;

    if houseType == "Main":
            house = structure.mainHouseBox(w1,l1,material1,material2);
    else:
            house = structure.simpleHouseBox(w1,l1,material1,material2);
            

    

    buildHouse(level,minx,minz,width,length,height,house,order);

def buildAgriBase(level, loc, houseType, order, wood):
    minx = loc[0];
    minz = loc[1];
    maxx = loc[2]+minx;
    maxz = loc[3]+minz;
    width = loc[2];
    length= loc[3];
    height = 0;


    
    for x in xrange(minx,maxx):
        for z in xrange(minz,maxz):
            height = max(height,getGroundYPos(x,z))

    if houseType == "Farm":
        
        house = structure.farmBox(wood);
    
    buildHouse(level,minx,minz,width,length,height,house,0);

# we define a matrix house as building temple
# x,y,z means the location
# house[x][y][z] is an array, lenght of 2, first is id, second is value
# for id, 1,2 means two different material to enter, more number for other materials
# 333 means road, 0 means air.
# other materials will use their own id
# for value, it is used for blocks with direct (like stairs and doors)
# 20:glass
# 64:door
# 53,67,108,109,114,128,134,135,136:stairs



#Here are location for stair and doors, in order south, west, north, east
stair = [2,1,3,0]
stairId = [53,67,108,109,114,128,134,135,136,163,164]
slabId = [44];
door = [3,0,1,2]
doorId = [64,193,194,195,196,197];
road = [333]
chest = [3,4,2,5];
chestId = [54,61,62,65];
torch = [3,2,4,1]
torchId = [50]

def buildNoDirectBuilding(level, xstart, zstart, width, length,height,house,typ):
    prt(typ)
    order = 0;
        
    for x in xrange(xstart, xstart+width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(height+1,he+1):
                setBlock(level,(0,0),x,y,z);
            setHeight(level,x,he,z);

    
    
    for x in xrange(0,width):
        for z in xrange(0,length):
            for y in xrange(0,len(house[x][z])):
                if y == 0:
                    if house[x][z][y][0]==0:
                        setBlock(level,(2,0),x+xstart,height,z+zstart);
                    elif house[x][z][y][0]==333:
                        setBlock(level,(43,5),x+xstart,height,z+zstart);
                if house[x][z][y][0]==0 or house[x][z][y][0]==333:
                    continue;
                #elif house[x][z][y][0]==1:
                #    setBlock(level,house[x][z][y][0],x+xstart,height+1+y,z+zstart);
                #elif house[x][z][y][0]==2:
                #    setBlock(level,house[x][z][y][0],x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in stairId:
                    material = house[x][z][y][0];
                    data = stair[(house[x][z][y][1]+order)%4];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in doorId:
                    material = house[x][z][y][0];
                    if house[x][z][y][1]<8:
                        data = door[(house[x][z][y][1]+order)%4];
                    else:
                        data = 8;
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in chestId:
                    material = house[x][z][y][0];
                    data = chest[(house[x][z][y][1]+order)%4];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart)
                else:
                    material = house[x][z][y][0];
                    data =house[x][z][y][1];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);         

def buildHouse(level, xstart, zstart, width, length,height,house1,order):   

    snow = False;
    for x in xrange(xstart,xstart+width):
        for z in xrange(zstart,zstart+length):
            y = getGroundYPos(x,z);
            for y0 in xrange(255,y,-1):
                if level.blockAt(x,y0,z)==78:
                    snow = True;
                    break;
                if level.blockAt(x,y0,z)!=0:
                    break;
            if snow:
                break;
        if snow:
            break;
            
    if order == 0:
        house = house1
    else: 
        house = [];
        for i in range(width):
            house.append([]);
            for j in range(length):
                house[i].append([]);
        if order == 1:
            for i in range(len(house1)):
                for j in range(len(house1[0])):
                    house[width-1-j][i]=house1[i][j];
    
        elif order == 2:
            for i in range(len(house1)):
                for j in range(len(house1[0])):
                    house[width-1-i][length-1-j]=house1[i][j];
        else:
            for i in range(len(house1)):
                for j in range(len(house1[0])):
                    house[j][length-1-i]=house1[i][j];
    


    for x in xrange(xstart, xstart+width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(height+1,he+1):
                setBlock(level,(0,0),x,y,z);
            setHeight(level,x,he,z);

    
    for x in xrange(0,width):
        for z in xrange(0,length):
            for y in xrange(0,len(house[x][z])):
                if y == 0:
                    if house[x][z][y][0]==0:
                        if level.blockAt(xstart,height,z+zstart) != 0:
                            setBlock(level,(2,0),x+xstart,height,z+zstart);
                    elif house[x][z][y][0]==333:
                        setBlock(level,(43,5),x+xstart,height,z+zstart);
                if house[x][z][y][0]==0 or house[x][z][y][0]==333:
                    continue;
                #elif house[x][z][y][0]==1:
                #    setBlock(level,house[x][z][y][0],x+xstart,height+1+y,z+zstart);
                #elif house[x][z][y][0]==2:
                #    setBlock(level,house[x][z][y][0],x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in stairId:
                    material = house[x][z][y][0];
                    data = stair[(house[x][z][y][1]+order)%4];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in doorId:
                    material = house[x][z][y][0];
                    if house[x][z][y][1]<8:
                        data = door[(house[x][z][y][1]+order)%4];
                    else:
                        data = 8;
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0] in chestId:
                    material = house[x][z][y][0];
                    data = chest[(house[x][z][y][1]+order)%4];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart)
                elif house[x][z][y][0] in torchId:
                    material = house[x][z][y][0];
                    data = torch[(house[x][z][y][1]+order)%4];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart)
                else:
                    material = house[x][z][y][0];
                    if material != 20:
                        data =house[x][z][y][1];
                    else:
                        data = 0;
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);                    
                    
    if snow:
        for x in xrange(xstart,xstart+width):
            for z in xrange(zstart,zstart+length):
                for y in xrange(255,-1,-1):
                    bid = level.blockAt(x,y,z)
                    if bid!=0:
                        if house[x-xstart][z-zstart][0] == 333:
                            break;
                        if bid in [8,9,10,11]:
                            break;
                        if isGround(bid) or bid in [5,17,160,161,43,24,1,4]:
                            setBlock(level,(78,0),x,y+1,z);
                        break;

        
def buildWell(level, xstart, zstart, height,material1,material2):   
    house = structure.wellBox(material1, material2);
    width = len(house);
    length = len(house[0]);
    snow = False;
    for x in xrange(xstart,xstart+width):
        for z in xrange(zstart,zstart+length):
            y = getGroundYPos(x,z);
            for y0 in xrange(255,y,-1):
                if level.blockAt(x,y0,z)==78:
                    snow = True;
                    break;
                if level.blockAt(x,y0,z)!=0:
                    break;
            if snow:
                break;
        if snow:
            break;        
    for x in xrange(xstart, xstart+width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(height+1,he+1):
                setBlock(level,(0,0),x,y,z);
            setHeight(level,x,he,z);

    height -= 5
    for x in xrange(0,width):
        for z in xrange(0,length):
            for y in xrange(0,len(house[x][z])):
                if y == 0:
                    if house[x][z][y][0]==0:
                        if level.blockAt(xstart,height,z+zstart) != 0:
                            setBlock(level,(2,0),x+xstart,height,z+zstart);
                    elif house[x][z][y][0]==333:
                        setBlock(level,(43,5),x+xstart,height,z+zstart);
                if level.blockAt(x+xstart,height+1+y,z+zstart) == 78:
                    setBlock(level,(0,0),x+xstart,height+1+y,z+zstart);
                if house[x][z][y][0]==0 or house[x][z][y][0]==333:
                    continue;   
                else:
                    material = house[x][z][y][0];
                    data =house[x][z][y][1];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);                    
                    
    for x in xrange(0,width):
        for z in xrange(0,length):
            _used[x+xstart][z+zstart] = 10;
            
    if snow:
        for x in xrange(xstart+1,xstart+width-1):
            for z in xrange(zstart+1,zstart+length-1):
                for y in xrange(255,-1,-1):
                    bid = level.blockAt(x,y,z)
                    if bid!=0:
                        setBlock(level,(78,0),x,y+1,z);
                        break;

def getMaterial(level,chunks):
    stone = [(1,0),(4,0),(12,0),(24,0)];
    wood = [(17,0),(17,1),(17,2),(17,3),(162,0),(162,1)]
    sc = [0,0,0,0]
    wc = [0,0,0,0,0,0]
    
    for chunk in chunks:
            
        for x in xrange(chunk.box.minx,chunk.box.maxx):
            for z in xrange(chunk.box.minz,chunk.box.maxz):
                y = getGroundYPos(x,z)
                
                for y0 in xrange(y-3,y):
                    bid = level.blockAt(x,y0,z)
                    data = level.blockDataAt(x,y0,z)
                    for i in range(4):
                        if (bid,data)==stone[i]:
                            sc[i]+=1;
                    
                for y0 in xrange(y+1,256):
                    bid = level.blockAt(x,y0,z)
                    data = level.blockDataAt(x,y0,z)
                    if bid == 0:
                        break;
                    for i in range(6):
                        if (bid,data)==wood[i]:
                            wc[i]+=1;
                            
                        
    wi = -1;
    for i in range(6):
        if wi == -1:
            wi = i;
        elif wc[i]>wc[wi]:
            wi = i;

    si = -1;
    for i in range(4):
        if si == -1:
            si = i
        elif sc[i]>sc[si]:
            si = i;

    materialWood = wood[wi];

    materialStone = stone[si]

    if materialStone == (12,0):
        materialStone = (24,0);
    
    return materialWood, materialStone;
