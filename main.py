import sys
import copy


def loadNon(path: str):
    width = -1
    height = -1
    maxBlockSize = -1
    rowsRules = []
    columnsRules = []
    with open(path, "r") as f:
        # Read Header
        line = f.readline()
        width = int(line.split()[1])
        print("Width: " + str(width))
        line = f.readline()
        height = int(line.split()[1])
        print("Width: " + str(height))

        rowsRules = [[] for i in range(height)]
        columnsRules = [[] for i in range(width)]

        # Read First Type Header (Rows or Columns)
        line = f.readline()  # Type Header

        if line.strip() == "rows":
            # Read Rows first
            print("First Row Header: " + line.strip())
            for i in range(height):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    blockSize = int(rule)
                    maxBlockSize = max(maxBlockSize, blockSize)
                    rowsRules[i].append(blockSize)

            # Read Columns
            line = f.readline()  # Column Header
            print("Second Column Header: " + line.strip())
            for i in range(width):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    blockSize = int(rule)
                    maxBlockSize = max(maxBlockSize, blockSize)
                    columnsRules[i].append(blockSize)
        else:
            # Read Columns first
            print("First Column Header: " + line.strip())
            for i in range(width):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    blockSize = int(rule)
                    maxBlockSize = max(maxBlockSize, blockSize)
                    columnsRules[i].append(blockSize)

            # Read Rows
            line = f.readline()  # Rows Header
            print("Second Row Header: " + line.strip())
            for i in range(height):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    blockSize = int(rule)
                    maxBlockSize = max(maxBlockSize, blockSize)
                    rowsRules[i].append(blockSize)

        f.close()
    return width, height, maxBlockSize, rowsRules, columnsRules


def generate2Dto1DTransform(width: int, height: int):
    return lambda y, x: x + y * width


def generate2DAndBlockTo1D(to1D, width: int, height: int, maxBlockSize: int):
    area = width * height
    return (
        lambda k, blockPos, y, x: to1D(y, x) + blockPos * area + k * area * maxBlockSize
    )


def exactlyOne(varList: list, getNewVariable) -> list:
    clauses = [copy.deepcopy(varList)]  # At least once
    # for now AMOS
    listSize = len(varList)
    for i in range(listSize):
        for j in range(listSize):
            clauses.append([-varList[i], -varList[j]])
    return clauses


def generateAllExactlyOneForBlock(
    block: int,
    y: int,
    x: int,
    blockSize: int,
    width: int,
    height: int,
    doRowWise: bool,
    getFinalPosition,
    getNewVariable,
) -> list:
    clauses = []
    for blockPos in range(blockSize):
        if doRowWise:
            clauses += exactlyOne(
                [
                    getFinalPosition(block, blockPos, y, xIter)
                    for xIter in range(blockPos, width - (blockSize - blockPos - 1))
                ],
                getNewVariable,
            )
        else:
            clauses += exactlyOne(
                [
                    getFinalPosition(block, blockPos, yIter, x)
                    for yIter in range(blockPos, height - (blockSize - blockPos - 1))
                ],
                getNewVariable,
            )
    return clauses


def generateAllBlockFull(
    block: int,
    y: int,
    x: int,
    blockSize: int,
    width: int,
    height: int,
    doRowWise: bool,
    getFinalPosition,
) -> list:
    clauses = []

    if doRowWise:
        for xIter in range(width - (blockSize - 1)):  # all starting positions
            for blockPosIter in range(1, blockSize):  # all the next positions
                clauses.append(
                    [
                        -getFinalPosition(block, 0, y, xIter),
                        getFinalPosition(block, blockPosIter, y, xIter + blockPosIter),
                    ]
                )
    else:
        for yIter in range(height - (blockSize - 1)):  # all starting positions
            for blockPosIter in range(1, blockSize):  # all the next positions
                clauses.append(
                    [
                        -getFinalPosition(block, 0, yIter, x),
                        getFinalPosition(block, blockPosIter, yIter + blockPosIter, x),
                    ]
                )

    return clauses


def generateAllNoOverlappingBlocksOnRowOrColumn(
    blocks: list,
    y: int,
    x: int,
    blockSizes: list,
    width: int,
    height: int,
    doRowWise: bool,
    getFinalPosition,
) -> list:
    blockAmount = len(blocks)
    clauses = []
    for blockIter in range(blockAmount - 1):  # All the blocks except the last one
        lastBlockPos = blockSizes[blockIter] - 1
        for nextBlockIter in range(blockIter+1, blockAmount):  # All the next blocks
            if doRowWise:
                for xIter in range(
                    lastBlockPos, width
                ):  # All the last possible positions to end a block
                    for xIter2 in range(
                        xIter + 1
                    ):  # All the previous positions where we could try to start the next block
                        clauses += [
                            -getFinalPosition(
                                blocks[blockIter], lastBlockPos, y, xIter
                            ),
                            -getFinalPosition(blocks[nextBlockIter], 0, y, xIter2),
                        ]
            else:
                for yIter in range(
                    lastBlockPos, height
                ):  # All the last possible positions to end a block
                    for yIter2 in range(
                        yIter + 1
                    ):  # All the previous positions where we could try to start the next block
                        clauses += [
                            -getFinalPosition(
                                blocks[blockIter], lastBlockPos, yIter, x
                            ),
                            -getFinalPosition(blocks[nextBlockIter], 0, yIter2, x),
                        ]

    return clauses


def main(glucosePath: str, nonPath: str, bmpPath: str):
    width, height, maxBlockSize, rowsRules, columnsRules = loadNon(nonPath + ".non")
    to1D = generate2Dto1DTransform(width, height)
    from2DandBlockTo1D = generate2DAndBlockTo1D(to1D, width, height, maxBlockSize)

    variableCount = 0
    map1DToPPos = {}
    map1DToFinalPos = {}  # We have many empty positions
    map1DAssociatedWithPVar = (
        {}
    )  # For Constraints of q variables associated with p variables
    mapFinalPosTo2D = {}  # For decoding

    def getNewVariable():
        nonlocal variableCount
        newVar = variableCount
        variableCount += 1
        return newVar

    def getPVariable(y, x):
        pos = to1D(y, x)
        if pos in mapFinalPosTo2D:
            return map1DToPPos[pos]

        # register it
        finalPos = getNewVariable()
        map1DToPPos[pos] = finalPos  # real name used
        mapFinalPosTo2D[finalPos] = (y, x)  # for decoding
        map1DAssociatedWithPVar[finalPos] = []  # for q variables
        return finalPos

    def getFinalPosition(k, blockPos, y, x):
        pos = from2DandBlockTo1D(k, blockPos, y, x)

        # if we have seen it before
        if pos in map1DToFinalPos:
            return map1DToFinalPos[pos]

        # register it
        finalPos = getNewVariable()  # get free variable name
        map1DToFinalPos[pos] = finalPos  # set the translation table for future querys
        map1DAssociatedWithPVar[getPVariable(y, x)].append(
            finalPos
        )  # Add to P constraints
        return finalPos


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Not Enough Arguments", file=sys.stderr)
        print("{0} glucosePath nonPath bmpPath".format(sys.argv[0]), file=sys.stderr)
        exit(-1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
