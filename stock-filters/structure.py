wallBlocks = {};
stairBlocks = {};
doorBlocks = {};
supportBlocks ={}
fenceBlocks = {}
slabBlocks = {}

def init():

    #Tree
    wallBlocks[17] = {};
    wallBlocks[17][0] = [5,0]
    wallBlocks[17][1] = [5,1]
    wallBlocks[17][2] = [5,2]
    wallBlocks[17][3] = [5,3]
    wallBlocks[162] = {};
    wallBlocks[162][0] = [5,4]
    wallBlocks[162][1] =[5,5];

    supportBlocks[17] = {};
    supportBlocks[17][0] = [17,0]
    supportBlocks[17][1] = [17,1]
    supportBlocks[17][2] = [17,2]
    supportBlocks[17][3] = [17,3]
    supportBlocks[162] = {};
    supportBlocks[162][0] = [160,0]
    supportBlocks[162][1] =[161,1];

    fenceBlocks[17] = {};
    fenceBlocks[17][0] = [85,0]
    fenceBlocks[17][1] = [188,0]
    fenceBlocks[17][2] = [189,0]
    fenceBlocks[17][3] = [190,0]
    fenceBlocks[162] = {};
    fenceBlocks[162][0] = [191,0]
    fenceBlocks[162][1] =[192,0];

    stairBlocks[17]={};
    stairBlocks[17][0] = 53
    stairBlocks[17][1] = 134
    stairBlocks[17][2] = 135
    stairBlocks[17][3] = 136
    stairBlocks[162] = {};
    stairBlocks[162][0] = 163
    stairBlocks[162][1] =164;

    doorBlocks[17] = {};
    doorBlocks[17][0] = 64
    doorBlocks[17][1] = 193
    doorBlocks[17][2] = 194
    doorBlocks[17][3] = 195
    doorBlocks[162] = {};
    doorBlocks[162][0] = 196
    doorBlocks[162][1] = 197;

    #stone
    wallBlocks[1] = {};
    wallBlocks[1][0] = [43,5]
    wallBlocks[4] = {}
    wallBlocks[4][0] = [43,3]
    wallBlocks[24] = {};
    wallBlocks[24][0] = [24,2]

    supportBlocks[1] = {};
    supportBlocks[1][0] = [1,0]
    supportBlocks[4] = {}
    supportBlocks[4][0] = [4,0]
    supportBlocks[24] = {};
    supportBlocks[24][0] = [24,1]    

    stairBlocks[1] = {};
    stairBlocks[1][0] = 109
    stairBlocks[4] = {}
    stairBlocks[4][0] = 67
    stairBlocks[24] = {};
    stairBlocks[24][0] = 128

    slabBlocks[1] = {};
    slabBlocks[1][0] = [44,0]
    slabBlocks[4] = {}
    slabBlocks[4][0] = [44,3]
    slabBlocks[24] = {};
    slabBlocks[24][0] = [44,1]

def mainHouseBox(width, length,material1,material2):

    (m1,d1)=material1;
    (m2,d2)=material2;
    wallId = wallBlocks[m1][d1][0];
    wallValue = wallBlocks[m1][d1][1];
    supportId = supportBlocks[m2][d2][0];
    supportValue = supportBlocks[m2][d2][1]
    stair = stairBlocks[m2][d2];
    door = doorBlocks[m1][d1];
    
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
            house[x][z][0][0]=supportId;
            house[x][z][0][1]=supportValue;
            
    table = ((1,1),(1,length-2),(width-2,1),(width-2,length-2),
             (w1-1,length-2),(w2,length-2),(w1-1,l1),(w2,l1));


    for l in range(lv):
        #eight support
        for (x,z) in table:
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=supportId;
                house[x][z][l*4+he][1]=supportValue;
                
        #wall
        for x in xrange(2,  width - 2):
            z =  1
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=wallId;
                house[x][z][l*4+he][1]=wallValue
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20

        for x in (1,width-2):
            for z in xrange(2,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=wallId;
                    house[x][z][l*4+he][1]=wallValue
                    if z % 2 == 1:
                        house[x][z][l*4+2][0]=20;
        
        for x in xrange(2, w1-1):
            z =  length - 2;
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=wallId;
                house[x][z][l*4+he][1]=wallValue
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;

                
        for x in xrange(w2+1,  width - 2):
            z =  length - 2;
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=wallId;
                house[x][z][l*4+he][1]=wallValue
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;
                
        for x in xrange(w1,w2):
            z = l1
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=wallId;
                house[x][z][l*4+he][1]=wallValue
            if x % 2 == 1:
                house[x][z][l*4+2][0]=20;

        for z in xrange(l1+1, length - 2):
            for x in (w1-1,w2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=wallId;
                    house[x][z][l*4+he][1]=wallValue
                    if z % 2 == 1:
                        house[x][z][l*4+2][0]=20;
            
        #floor
        for x in xrange(1, width - 1):
            for z in xrange(1, length - 1):
                if z > l1:
                    if w1 <= x < w2:
                        continue
                house[x][z][l*4+4][0]=supportId;
                house[x][z][l*4+4][1]=supportValue;

        for x in xrange(1, width-1):
            z = 0;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=0;
            z = 0 + length - 1;
            if x == w1:
                continue;
            if x == w2-1:
                continue;
            if w1 <= x < w2:
                house[x][l1+1][l*4+4][0]=stair;
                house[x][l1+1][l*4+4][1]=2;
            else:
                house[x][length-1][l*4+4][0]=stair;
                house[x][length-1][l*4+4][1]=2;
        for z in xrange(1,  length - 1):
            x = 0;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=3;
            x =  width - 1;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=1;

        for z in xrange(l1+1,  length - 1):
            x = w1;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=1;
            x = w2-1;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=3;
            
        
    #door
    x = (width -1)/2;
    z = l1;
    house[x][z][1][0]=door;
    house[x][z][1][1]=0;
    house[x][z][2][0]=door;
    house[x][z][2][1]=8;
    
    house[x][z+1][0][0]=stair;
    house[x][z+1][0][1]=2;

    z=z+2;
    while (z<length):
        house[x][z][0][0]=333;
        z = z+1;

    return house
    
def simpleHouseBox(width,length,material1,material2):

    (m1,d1)=material1;
    (m2,d2)=material2;
    wallId = wallBlocks[m1][d1][0];
    wallValue = wallBlocks[m1][d1][1];
    supportId = supportBlocks[m2][d2][0];
    supportValue = supportBlocks[m2][d2][1]
    stair = stairBlocks[m2][d2];
    door = doorBlocks[m1][d1];
    
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
            house[x][z][0][0] = supportId;
            house[x][z][0][1] = supportValue;

    table =((1,1),(1,length-2),(width-2,1),(width-2,length-2))

    for l in range(lv):
        #four support
        for (x,z) in table:
            for he in xrange(1,4):
                house[x][z][l*4+he][0]=supportId;
                house[x][z][l*4+he][1]=supportValue;

        #wall
        for x in xrange(2,width-2):
            for z in (1,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=wallId;
                    house[x][z][l*4+he][1]=wallValue;

        for x in (1,width-2):
            for z in xrange(2,length-2):
                for he in xrange(1,4):
                    house[x][z][l*4+he][0]=wallId;
                    house[x][z][l*4+he][1]=wallValue;

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
                house[x][z][l*4+4][0]=supportId;
                house[x][z][l*4+4][1]=supportValue;

        for x in xrange(1, width-1):
            z = 0;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=0;
            z = length - 1;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=2;
        for z in xrange( 1,  length - 1):
            x = 0;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=3;
            x =  width - 1;
            house[x][z][l*4+4][0]=stair;
            house[x][z][l*4+4][1]=1;

    #door
    x = (width -1)/2;
    z = length-2;
    house[x][z][1][0]=door;
    house[x][z][1][1]=0;
    house[x][z][2][0]=door;
    house[x][z][2][1]=8;
    
    house[x][z+1][0][0]=stair;
    house[x][z+1][0][1]=2;
    return house;

def farmBox(material1):
    (w1,v1)=material1;
    width = 7;
    length = 9;
    house =[];
    for x in range(width):
        house.append([]);
        for z in range(length):
            house[x].append([])
            for y in range(2):
                house[x][z].append([0,0]);
    for x in [0,width-1]:
        for z in xrange(0,length):
            house[x][z][0][0] = w1;
            house[x][z][0][1] = v1;

    for x in xrange(1,width-1):
        for z in [0,length-1]:
            house[x][z][0][0] = w1;
            house[x][z][0][1] = v1;

    for x in xrange(1,width-1):
        for z in xrange(1,length-1):
            house[x][z][0][0] = 60;
            house[x][z][0][1] = 0;

    x = (width-1) / 2;
    for z in xrange(1,length-1):
        house[x][z][0][0] = 9;

    for x in xrange(1,width-1):
        if x == (width-1)/2:
            continue;
        for z in xrange(1,length-1):
            house[x][z][1][0] = 59;
            house[x][z][1][1] = 4;

    return house;

def smithBox(material1,material2):
    (m1,d1)=material1;
    (m2,d2)=material2;
    wallId = wallBlocks[m1][d1][0];
    wallValue = wallBlocks[m1][d1][1];
    supportId = wallBlocks[m2][d2][0];
    supportValue = wallBlocks[m2][d2][1]
    stair = stairBlocks[m2][d2];
    width = 8;
    lenth = 10;
    house = []
    for x in range(width):
        house.append([]);
        for z in range(length):
            house[x].append([])
            for y in range(2):
                house[x][z].append([0,0]);
    for x in range(width):
        house.append([]);
        for z in range(length):
            house[x].append([])
            for y in range(6):
                house[x][z].append([0,0]);
    for x in range(width-1):
        for z in range(length):
            house[x][z][0][0] = wallId;
            house[x][z][0][1] = wallValue;
    house[width-1][1][0][0] = stair;
    house[width-1][1][0][1] = 0;
    house[width-1][2][0][0] = stair;
    house[width-1][2][0][1] = 0;
    house[width-1][3][0][0] = stair;
    house[width-1][3][0][1] = 0;

    for x in range(3):
        for z in range(4):
            house[x][z][1][0] = supportId;
            house[x][z][1][1] = supportValue;
            if x == 1:
                if z in [1,2]:
                    house[x][z][1][0] = 11;
                    house[x][z][1][1] = 0;
    x = 0;
    for z in xrange(4,length-1):
        
        house[x][z][1][0]=wallId;
        house[x][z][1][1]=wallValue;
    z=length-1;
    for x in xrange(1,width-1):
        house[x][z][1][0]=wallId;
        house[x][z][1][1]=wallValue;
    x = width-2;
    for z in xrange(7,length-1):
        house[x][z][1][0]=wallId;
        house[x][z][1][1]=wallValue;     

def buildFloor(floors,themap):
    height = len(floors);
    width = 0;
    length = 0;
    for y in range(height):
        length = max(length,len(floors[y]));
        for x in range(len(floors[y])):
            width = max(width,len(floors[y][x]));
            
    house = [];
    for x in range(width):
        house.append([]);
        for z in range(length):
            house[x].append([]);
            for y in range(height):
                house[x][z].append([0,0]);
    for y in range(height):
        for x in range(len(floors[y])):
            for z in range(len(floors[y][x])):
                char = floors[y][x][z];
                if char in themap:
                    house[z][x][y] = themap[char]
    return house;

def readFloors(fileName):
    file = open(fileName,'r');
    floor = [];
    now = 0;
    with open(fileName) as file:
        for line in file:
            if line[0] == '|':
                floor.append([])
            else:
                floor[-1].append(line);
                if floor[-1][-1][-1] == '\r' or floor[-1][-1][-1] == '\n':
                    floor[-1][-1] = floor[-1][-1][:-1]
    
    return floor;
    

#material1:mainpart, material2:sidepart
def smithBox(material1,material2):
    floor = readFloors("stock-filters/structures/smith.txt");
    (m1,d1)=material1;
    (m2,d2)=material2;
    mainWall = wallBlocks[m1][d1];
    mainSupport = supportBlocks[m1][d1];
    sideWall = wallBlocks[m2][d2];
    sideSupport = supportBlocks[m2][d2];
    
    mainStair = stairBlocks[m1][d1];
    sideStair = stairBlocks[m2][d2];

    fence = fenceBlocks[m2][d2]
    themap = {};
    themap['C'] = mainSupport;
    themap['O'] = [mainStair,2];
    themap['P'] = sideWall;
    themap['W'] = sideSupport;
    themap['L'] = [11,0]
    themap['S'] = [sideStair,3];
    themap['s'] = [sideStair,1];
    themap['F'] = fence;
    themap['D'] = mainWall
    themap['Q'] = [54,3]
    themap['N'] = [102,0]
    themap['n'] = [102,0]
    themap['I'] = [101,0]
    themap['B'] = [61,0]
    themap['R'] = [72,0];
    themap['$'] = slabBlocks[m1][d1]
    return buildFloor(floor,themap);

def butcherBox(material1,material2):
    floor = readFloors("stock-filters/structures/butcher.txt");
    (m1,d1)=material1;
    (m2,d2)=material2;
    
    
    mainWall = wallBlocks[m1][d1];
    mainSupport = supportBlocks[m1][d1];
    sideWall = wallBlocks[m2][d2];
    sideSupport = supportBlocks[m2][d2];
    door = doorBlocks[m2][d2]
    mainStair = stairBlocks[m1][d1];
    sideStair = stairBlocks[m2][d2];
    slab = slabBlocks[m1][d1]
    fence = fenceBlocks[m2][d2]
    themap = {};

    themap['I'] = [2,0];
    themap['C'] = mainSupport;
    themap['P'] = sideWall;
    themap['S'] = [sideStair,2];
    themap['N'] = slab
    themap['F'] = fence;
    themap['O'] = [door,0];
    themap['Y'] = [door,8];
    themap['T'] = [sideStair,2];
    themap['t'] = [sideStair,0];
    themap['D'] = mainWall
    themap['G'] = [102,0]
    themap['g'] = [102,0]
    themap['W'] = sideSupport;
    themap['L'] = [72,0]
    themap['!'] = [50,2]
    themap['h'] = [50,0]
    
    return buildFloor(floor,themap);

def churchBox(material1,material2):
    floor = readFloors("stock-filters/structures/church.txt");
    (m1,d1)=material1;
    (m2,d2)=material2;
    
    
    mainWall = wallBlocks[m1][d1];
    mainSupport = supportBlocks[m1][d1];
    sideWall = wallBlocks[m2][d2];
    sideSupport = supportBlocks[m2][d2];
    door = doorBlocks[m2][d2]
    mainStair = stairBlocks[m1][d1];
    sideStair = stairBlocks[m2][d2];
    slab = slabBlocks[m1][d1]
    fence = fenceBlocks[m2][d2]
    themap = {};

    themap['C'] = mainSupport;
    themap['S'] = [mainStair,2];
    themap['s'] = [mainStair,3];
    themap['$'] = [mainStair,0];
    themap['L'] = [65,0]
    themap['D'] = [door,0]
    themap['G'] = [102,0]
    themap['g'] = [102,0]
    themap['O'] = [door,8];
    themap['T'] = [50,2]
    themap['t'] = [50,3]
    themap['H'] = [50,0]
    themap['h'] = [50,1]

    return buildFloor(floor,themap);

def lampBox(material2):
    floor = readFloors("stock-filters/structures/lamp.txt");
    (m2,d2)=material2;
    fence = fenceBlocks[m2][d2]
    themap = {};

    themap['F'] = fence;
    themap['W'] = [m2,d2];
    themap['T'] = [50,2]
    themap['t'] = [50,3]
    themap['H'] = [50,0]
    themap['h'] = [50,1]
    

    return buildFloor(floor,themap);

def libraryBox(material1,material2):
    floor = readFloors("stock-filters/structures/library.txt");
    (m1,d1)=material1;
    (m2,d2)=material2;
    
    
    mainWall = wallBlocks[m1][d1];
    mainSupport = supportBlocks[m1][d1];
    sideWall = wallBlocks[m2][d2];
    sideSupport = supportBlocks[m2][d2];
    door = doorBlocks[m2][d2]
    mainStair = stairBlocks[m1][d1];
    sideStair = stairBlocks[m2][d2];
    slab = slabBlocks[m1][d1]
    fence = fenceBlocks[m2][d2]
    themap = {};

    themap['c'] = mainSupport;
    themap['o'] = [mainStair,2];
    themap['p'] = sideWall
    themap['s'] = [sideStair,2]
    themap['S'] = [sideStair,0]
    themap['d'] = [door,0]
    themap['a'] = [door,8]
    themap['e'] = [58,0]
    themap['f'] = fence;
    themap['g'] = [102,0]
    themap['G'] = [102,0]
    themap['r'] = [72,0]
    themap['l'] = [47,0]
    return buildFloor(floor,themap);
def wellBox(material1,material2):
    floor = readFloors("stock-filters/structures/well.txt");
    (m1,d1)=material1;
    (m2,d2)=material2;
    
    
    mainWall = wallBlocks[m1][d1];
    mainSupport = supportBlocks[m1][d1];
    sideWall = wallBlocks[m2][d2];
    sideSupport = supportBlocks[m2][d2];
    door = doorBlocks[m2][d2]
    mainStair = stairBlocks[m1][d1];
    sideStair = stairBlocks[m2][d2];
    slab = slabBlocks[m1][d1]
    fence = fenceBlocks[m2][d2]
    themap = {};

    themap['C'] = mainSupport;
    themap['W'] = [8,0]
    themap['F'] = fence
    return buildFloor(floor,themap);

