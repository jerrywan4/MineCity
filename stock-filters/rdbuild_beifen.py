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

_buildLoc = {};
_used = {}
_score = {};
boundary = [];
    
def findRoad(startx,startz,chunks):
    bfs = [];
    bfs.append(startx,startz,-1);
    f = 0;
    e = 1;
    _used[x][z]=-1;
    direct = [(-1,0),(1,0),(0,-1),(0,1)]
    while (f<e):
        (x,z,last) = bfs[f];
        for i in range(4):
            (x0,z0)=direct[i];
            if used[x0+x][z0+z]==0:
                bfs.append(x0+x,z0+z,f);
                used[x0+x][z0+z]=-1;
            elif used[x0+x][z0+z]==10:
                print("get");
                ans = [];
                ans.append(x0+x,z0+z);
                last = f;
                while (last!=-1):
                    (ansx,ansz,last)=bfs[last];
                    ans.append(ansx,ansz);
                return ans;
                
            e+=1;


        f+=1;
    print("no road")
    return [];
        


def randomBuild(level, chunks, maxwidth,maxlength,roadx,roadz):
    minx = 10000000;
    maxx = -10000000;
    minz = 10000000;
    maxz = -10000000;
    for chunk in chunks:
        minx = min(chunk.box.minx,minx);
        maxx = max(chunk.box.maxx,maxx);
        minz = min(chunk.box.minz,minz);
        maxz = max(chunk.box.maxz,maxz);
    
    print(minx,maxx,minz,maxz);
    
    init(level,minx,maxx,minz,maxz,chunks);
    _used[roadx][roadz]=10;
    setBlock(level,(43,5),roadx,getGroundYPos(roadx,roadz),roadz);
    print("init")
    loc = locate(level,minx,maxx,minz,maxz,maxwidth,maxlength);
    if loc[2] % 2==0:
        loc[2] -= 1;
    if loc[3] % 2==0:
        loc[3] -= 1;

    #buildBigHouse
    
    flatGround(level,loc)
    buildBase(level,loc,"Main",3)

    findRoad(loc[0],loc[1]);
                        

                            
    
def init(level,minx,maxx,minz,maxz,chunks):

    boundary.append(minx);
    boundary.append(maxx);
    boundary.append(minz);
    boundary.append(maxx);
    
    for x in xrange(minx,maxx):
        _buildLoc[x]={};
        for z in xrange(minz,maxz):
            _buildLoc[x][z]=[];
            
    for x in xrange(minx,maxx):
        _used[x]={};
        _score[x]={};
        for z in xrange(minz,maxz):
            _used[x][z]=1;
            _score[x][z] = 0.0;
            

    for chunk in chunks:
        for x in xrange(chunk.box.minx,chunk.box.maxx):
            for z in xrange(chunk.box.minz,chunk.box.maxz):
                if level.blockAt(x,getGroundYPos(x,z),z) in [8,9,10,11]:
                    _score[x][z] = -100;
                    continue
                else:
                    _used[x][z]=0;
                    for (x0,z0) in [(1,0),(-1,0),(0,1),(0,-1)]:
                        if x0+x<minx:
                            continue;
                        if x0+x>=maxx:
                            continue;
                        if z0+z<minz:
                            continue;
                        if z0+z>=minz:
                            continue;
                        _score[x][z] -= abs(getGroundYPos(x,z),getGroundYPos(x+x0,z+z0));
                    
                    

    

def flatGround(level,loc):
    xmin = loc[0];
    zmin = loc[1];
    xmax = loc[2]+xmin;
    zmax = loc[3]+zmin;
    hmin = 255;
    hmax = 0;
    for x in xrange(xmin,xmax):
        for z in xrange(zmin,zmax):
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

def locate(level,minx,maxx,minz,maxz,maxwidth,maxlength):
    currentScore = 0;
    locx = maxx;
    locz = maxz;
    locw = 0;
    locl = 0;
    count = 0;
    for x in xrange(minx,maxx):
        for z in xrange(minz,maxz):
            if level.blockAt(x,getGroundYPos(x,z),z) in [8,9,10,11]:
                continue;
            lastw = 0;
            lastl = 0;
            for width in xrange(7,maxwidth):
                if x+width>=maxx:
                    break;
                height = 0;
                minheight = 255;
                maxheight = 0;
                
                for cz in xrange(z,z+maxlength):
                    if cz >= maxz:
                        break;
                    for cx in xrange(x,x+width):
                        if level.blockAt(cx,getGroundYPos(cx,cz),cz) in [8,9,10,11]:
                            minheight = 0;
                            maxheight = 255;
                            break;
                        minheight = min(minheight,getGroundYPos(cx,cz));
                        maxheight = max(maxheight,getGroundYPos(cx,cz));
                    if maxheight-minheight>2:
                        if lastl==0 and lastw==0:
                            lastl = cz-z;
                            lastw = width;
                        elif lastl==cz-z:
                            lastw = width;
                        else:
                            if lastl>=7 and lastw>=7:
                                _buildLoc[x][z].append([lastw,lastl]);
                            lastl = cz-z;
                            lastw = width;

                        
                        break;
                    elif cz == z+maxlength-1:
                        if lastl==0 and lastw==0:
                            lastl = cz+1-z;
                            lastw = width;
                        elif lastl==cz+1-z:
                            lastw = width;
                        else:
                            if lastl>=7 and lastw>=7:
                                _buildLoc[x][z].append([lastw,lastl]);
                            lastl = cz+1-z;
                            lastw = width;
            if lastl>=7 and lastw>=7:
                _buildLoc[x][z].append([lastw,lastl]);
                
    maxa=0
    score=0.0
    midx = (minx+maxx);
    midz = (minz+maxz);
    loc = [];
    for x in xrange(minx,maxx):
        for z in xrange(minz,maxz):
            for area in _buildLoc[x][z]:
                if area[0]<10:
                    continue;
                if area[1]<10:
                    continue;
                if area[0]>area[1]*2:
                    area[0]=area[1]*2+1;
                if area[1]>area[0]*2:
                    area[1]=area[0]*2;
                if area[0]*area[1]>maxa:
                    maxa = area[0]*area[1];
                    loc = [x,z,area[0],area[1]];
                    score = abs((2*x+area[0])-midx) * abs((2*z+area[1])-midz);
                elif area[0]*area[1]==maxa:
                    s = abs((2*x+area[0])-midx) * abs((2*z+area[1])-midz)
                    if s > score:
                        score = s;
                        loc = [x,z,area[0],area[1]];
    return loc;
                        
                    
                            



def buildBase(level, loc, houseType, order):
    minx = loc[0];
    minz = loc[1];
    maxx = loc[2]+minx;
    maxz = loc[3]+minz;
    width = loc[2];
    length= loc[3];
    height = 0;

    for x in range(minx-4,maxx+4):
        if not (x in _used):
            continue;
        for z in range(minz-4,maxz+4):
            if not (z in _used[x]):
                continue;
            _used[x][z]=1;

    
    for x in xrange(minx,maxx):
        for z in xrange(minz,maxz):
            height = max(height,getGroundYPos(x,z))

    buildHouse(level,minx,minz,width,length,height,(5,1),(43,0),houseType,order);



# we define a matrix house as building temple
# x,y,z means the location
# house[x][y][z] is an array, lenght of 2, first is id, second is value
# for id, 1,2 means two different material to enter, more number for other materials
# for value, it is used for blocks with direct (like stairs and doors)
# 20:glass
# 64:door
# 53,67,108,109,114,128,134,135,136:stairs

#Here are location for stair and doors, in order south, west, north, east
stair = [2,1,3,0]
stairId = [53,67,108,109,114,128,134,135,136]
door = [3,0,1,2]
doorId = [64];
road = [333]

def mainHouseBox(width, length):
    lv = int((max(width,length)-2) / 5);

    lv = min(lv,3);
    
    house = [];
    for i in range(width):
        house.append([]);
        for j in range(length):
            house[i].append([]);
            for k in range(lv):
                
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
            house[i][j].append([0,0]);
            
    subWidth = 5;
    subLength = (length - 1)/2;

    w1 =  subWidth + 1;
    w2 =  width - subWidth - 1

    l1 =  length - subLength;

    #Ground
    for x in xrange(1, width - 1):
        for z in xrange( 1,  length - 1):
            if z > l1:
                if w1 <= x < w2:
                    continue
            house[x][z][0][0]=2;
            
    table = ((1,1),(1,length-2),(width-2,1),(width-2,length-2),
             (w1-1,length-2),(w2,length-2),(w1-1,l1),(w2,l1));


    for l in range(lv):
        #eight support
        for (x,z) in table:
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=2;

                
        #wall
        for x in xrange(2,  width - 2):
            z =  1
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=1
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20

        for x in (1,width-2):
            for z in xrange(2,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=1;
                if z % 2 == 1:
                    house[x][z][l*4+2][0]=20;
        
        for x in xrange(2, w1-1):
            z =  length - 2;
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=1;
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;

                
        for x in xrange(w2+1,  width - 2):
            z =  length - 2;
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=1;
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;
                
        for x in xrange(w1,w2):
            z = l1
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=1;
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;

        for z in xrange(l1+1, length - 2):
            for x in (w1-1,w2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=1;
                if z % 2 == 1:
                    house[x][z][l*4+2][0]=20;
            
        #floor
        for x in xrange(1, width - 1):
            for z in xrange(1, length - 1):
                if z > l1:
                    if w1 <= x < w2:
                        continue
                house[x][z][l*4+4][0]=2;

        for x in xrange(1, width-1):
            z = 0;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=0;
            z = 0 + length - 1;
            if x == w1:
                continue;
            if x == w2-1:
                continue;
            if w1 <= x < w2:
                house[x][l1+1][l*4+4][0]=109;
                house[x][l1+1][l*4+4][1]=2;
            else:
                house[x][length-1][l*4+4][0]=109;
                house[x][length-1][l*4+4][1]=2;
        for z in xrange(1,  length - 1):
            x = 0;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=3;
            x =  width - 1;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=1;

        for z in xrange(l1+1,  length - 1):
            x = w1;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=1;
            x = w2-1;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=3;
            
        
    #door
    x = (width -1)/2;
    z = l1;
    house[x][z][1][0]=64;
    house[x][z][1][1]=0;
    house[x][z][2][0]=64;
    house[x][z][2][1]=8;
    
    house[x][z+1][0][0]=109;
    house[x][z+1][0][1]=2;

    z=z+2;
    while (z<length):
        house[x][z][0][0]=333;
        z = z+1;

    return house
    
def simpleHouseBox(width,length):

    lv = int((max(width,length)-2) / 5);

    lv = min(lv,3);
    
    house = [];
    for i in range(width):
        house.append([]);
        for j in range(length):
            house[i].append([]);
            for k in range(lv):
                
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
                house[i][j].append([0,0]);
            house[i][j].append([0,0]);

    #Ground

    for x in range(1,width-1):
        for z in xrange(1,length-1):
            house[x][z][0][0] = 2;

    
    table =((1,1),(1,length-2),(width-2,1),(width-2,length-2))

    for l in range(lv):
        #four support
        for (x,z) in table:
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=2;

        #wall
        for x in xrange(2,width-2):
            for z in (1,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=1;

        for x in (1,width-2):
            for z in xrange(2,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=1;

        #window
        for x in xrange(3,width-2,2):
            z = 1;
            house[x][z][l*4+2][0]=20;
            z = length - 2;
            house[x][z][l*4+2][0]=20;

        for z in xrange(3,length-2,2):
            x = 1;
            house[x][z][l*4+2][0]=20;
            x = width - 2;
            house[x][z][l*4+2][0]=20;

        #Floor:
        for x in xrange(1, width -1):
            for z in xrange(1,length -1):
                house[x][z][l*4+4][0]=2;

        for x in xrange(1, width-1):
            z = 0;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=0;
            z = length - 1;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=2;
        for z in xrange( 1,  length - 1):
            x = 0;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=3;
            x =  width - 1;
            house[x][z][l*4+4][0]=109;
            house[x][z][l*4+4][1]=1;

    #door
    x = (width -1)/2;
    z = length-2;
    house[x][z][1][0]=64;
    house[x][z][1][1]=0;
    house[x][z][2][0]=64;
    house[x][z][2][1]=8;
    
    house[x][z+1][0][0]=109;
    house[x][z+1][0][1]=2;


    return house;
         
def buildHouse(level, xstart, zstart, width, length,height,material1,material2,typ,order):

    if order % 2 ==0:
        if typ == "Main":
            house1 = mainHouseBox(width,length);
        else:
            house1 = simpleHouseBox(width,length);
    else:
        if typ == "Main":
            house1 = mainHouseBox(length,width);
        else:
            house1 = simpleHouseBox(length,width);
            
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
                        setBlock(level,(2,0),x+xstart,height,z+zstart);
                    elif house[x][z][y][0]==333:
                        setBlock(level,(43,5),x+xstart,height,z+zstart);
                if house[x][z][y][0]==0 or house[x][z][y][0]==333:
                    continue;
                elif house[x][z][y][0]==1:
                    setBlock(level,material1,x+xstart,height+1+y,z+zstart);
                elif house[x][z][y][0]==2:
                    setBlock(level,material2,x+xstart,height+1+y,z+zstart);
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
                else:
                    material = house[x][z][y][0];
                    data =house[x][z][y][1];
                    setBlock(level,(material,data),x+xstart,height+1+y,z+zstart);                    
                    


        
def buildMainHouse(level, xstart, zstart, width, length,height,material1,material2):

    #Stype:
    #########
    #########
    #########
    ###   ###
    ###   ###
    ###   ###

    
    for x in xrange(xstart, xstart+width):
        for z in xrange(zstart, zstart + length):
            he = getGroundYPos(x,z)
            for y in xrange(height+1,he+1):
                setBlock(level,(0,0),x,y,z);
            setHeight(level,x,he,z);

    subWidth = 5;
    subLength = (length - 1)/2;

    w1 = xstart + subWidth + 1;
    w2 = xstart + width - subWidth - 1

    l1 = zstart + length - subLength;

    
    


            
    lv = int((max(width,length)-2) / 5);

    lv = min(lv,3);





    #Ground
    for x in xrange(xstart + 1, xstart + width - 1):
        for z in xrange(zstart + 1, zstart + length - 1):
            if z > l1:
                if w1 <= x < w2:
                    setBlock(level, (2,0),x,height,z)
                    continue
            
            setBlock(level, material2,x,height+1,z)

    table = ((xstart+1,zstart+1),(xstart+1,zstart+length-2),(xstart+width-2,zstart+1),(xstart+width-2,zstart+length-2),
             (w1-1,zstart+length-2),(w2,zstart+length-2),(w1-1,l1),(w2,l1));


    for l in range(lv):
        #eight support
        for (x,z) in table:
            for he in xrange(2,5):
                setBlock(level,material2,x,height+l*4+he,z);
                
        #wall
        for x in xrange(xstart + 2, xstart + width - 2):
            z = zstart + 1
            for he in xrange(2,5):
                setBlock(level, material1, x, height + l*4 + he,z);
            if (x - xstart - 2) % 2 == 1:
                setBlock(level, (20,0), x, height + l*4 + 3,z);

        for x in (xstart+1,xstart+width-2):
            for z in xrange(zstart+2,zstart+length-2):
                for he in xrange(2,5):
                    setBlock(level, material1, x, height + l*4 + he, z);
                if (z-zstart-2) % 2 == 1:
                    setBlock(level, (20,0), x, height + l*4 + 3,z);
        
        for x in xrange(xstart + 2, w1-1):
            z = zstart + length - 2;
            for he in xrange(2,5):
                setBlock(level, material1, x, height + l*4 + he,z);
            if (x - xstart - 2) % 2 == 1:
                setBlock(level, (20,0), x, height + l*4 + 3,z);

                
        for x in xrange(w2+1, xstart + width - 2):
            z = zstart + length - 2;
            for he in xrange(2,5):
                setBlock(level, material1, x, height + l*4 + he,z);
            if (x - xstart - 2) % 2 == 1:
                setBlock(level, (20,0), x, height + l*4 + 3,z);
                
        for x in xrange(w1,w2):
            z = l1
            for he in xrange(2,5):
                setBlock(level, material1, x, height + l*4 + he,z);
            if (x - xstart - 2) % 2 == 1:
                setBlock(level, (20,0), x, height + l*4 + 3,z);

        for z in xrange(l1+1,zstart + length - 2):
            for x in (w1-1,w2):
                for he in xrange(2,5):
                    setBlock(level, material1, x, height + l*4 + he,z);
                if (z-zstart-2) % 2 == 1:
                    setBlock(level, (20,0), x, height + l*4 + 3,z);

        for z in xrange(zstart + 1, zstart + length - 1):
            if z > l1:
                if w1 <= x < w2:
                    setBlock(level, (2,0),x,height,z)
                    continue
            
        #floor
        for x in xrange(xstart + 1, xstart + width - 1):
            for z in xrange(zstart + 1, zstart + length - 1):
                if z > l1:
                    if w1 <= x < w2:
                        continue
                
                setBlock(level, material2,x,height+ l*4+5,z)

        for x in xrange(xstart +1, xstart +width-1):
            z = zstart;
            setBlock(level, (109,2),x,height+l*4+5,z)
            z = zstart + length - 1;
            if x == w1:
                continue;
            if x == w2-1:
                continue;
            if w1 <= x < w2:
                setBlock(level, (109,3),x,height+l*4+5,l1+1)
            else:
                setBlock(level, (109,3),x,height+l*4+5,zstart + length - 1)
        for z in xrange(zstart + 1, zstart + length - 1):
            x = xstart;
            setBlock(level, (109,0),x,height+l*4+5,z)
            x = xstart + width - 1;
            setBlock(level, (109,1),x,height+l*4+5,z)

        for z in xrange(l1+1, zstart + length - 1):
            x = w1;
            setBlock(level, (109,1),x,height+l*4+5,z)
            x = w2-1;
            setBlock(level, (109,0),x,height+l*4+5,z)
            
        
    #door
    x = (xstart + xstart + width -1)/2;
    z = l1;
    setBlock(level,(64,3),x,height+2,z);
    setBlock(level,(64,8),x,height+3,z);

    setBlock(level, (109,3),x,height+1,z+1);    
