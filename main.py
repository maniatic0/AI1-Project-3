import sys
import copy
import subprocess


def loadNon(path: str):
    width = -1
    height = -1
    maxBlockSize = -1
    rowsRules = []
    columnsRules = []
    with open(path, "r") as f:
        # Read Header
        line = f.readline()
        lineDiv = line.split()
        if lineDiv[0].lower() == "width":
            width = int(lineDiv[1])
            print("Width: " + str(width))
            line = f.readline()
            height = int(line.split()[1])
            print("Height: " + str(height))
        else:
            height = int(lineDiv[1])
            print("Height: " + str(height))
            line = f.readline()
            width = int(line.split()[1])
            print("Width: " + str(width))

        rowsRules = [[] for i in range(height)]
        columnsRules = [[] for i in range(width)]

        # Read First Type Header (Rows or Columns)
        line = f.readline()  # Type Header

        if line.strip().lower() == "rows":
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


def saveCnfFile(name: str, numVars: int, clauses: list):
    with open(name, "w") as f:
        print("p cnf {0} {1}".format(numVars, len(clauses)), file=f)

        for clause in clauses:
            print(" ".join(map(str, clause)) + " 0", file=f)

        f.close()


def loadOuputCnf(name: str, height: int, width: int, mapFinalPosTo2D: dict):
    image = [[0 for x in range(width)] for y in range(height)]
    model = []
    with open(name, "r") as f:
        line = f.readline()
        splited = line.split(" ")
        model = [int(var) for var in splited]
        f.close()

    for var in model:
        if var == 0:
            break

        varName = abs(var)  # literal name

        if varName in mapFinalPosTo2D:
            y, x = mapFinalPosTo2D[varName]

            if var > 0:  # positive literal
                image[y][x] = 1
            else:  # negative literal
                image[y][x] = 0

    return image


def savePBM(name: str, image: list, height: int, width: int):
    with open(name, "w") as f:
        print("P1", file=f)
        print("{0} {1}".format(width, height), file=f)
        for y in range(height):
            print(" ".join(map(str, image[y])), file=f)
        f.close()


def generate2Dto1DTransform(width: int, height: int):
    return lambda y, x: x + (y * width)


def generate2DAndBlockTo1D(to1D, width: int, height: int, maxBlockSize: int):
    area = width * height
    return (
        lambda k, blockPos, y, x: to1D(y, x)
        + (blockPos * area)
        + (k * area * maxBlockSize)
    )


def exactlyOne(varList: list, getNewVariable) -> list:
    clauses = [copy.deepcopy(varList)]  # At least once
    # for now AMOS
    listSize = len(varList)
    for i in range(listSize):
        for j in range(i + 1, listSize):
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
                    for xIter in range(0, width)
                ],
                getNewVariable,
            )
        else:
            clauses += exactlyOne(
                [
                    getFinalPosition(block, blockPos, yIter, x)
                    for yIter in range(0, height)
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
        lastBlockPos = blockSizes[blockIter] - 1  # Last Block Position
        block = blocks[blockIter]
        for nextBlockIter in range(blockIter + 1, blockAmount):  # All the next blocks
            nextBlock = blocks[nextBlockIter]
            if doRowWise:
                for xIter in range(
                    lastBlockPos, width
                ):  # All the last possible positions to end a block
                    for xIter2 in range(
                        xIter + 1
                    ):  # All the previous positions where we could try to start the next block
                        clauses.append(
                            [
                                -getFinalPosition(block, lastBlockPos, y, xIter),
                                -getFinalPosition(nextBlock, 0, y, xIter2),
                            ]
                        )
            else:
                for yIter in range(
                    lastBlockPos, height
                ):  # All the last possible positions to end a block
                    for yIter2 in range(
                        yIter + 1
                    ):  # All the previous positions where we could try to start the next block
                        clauses.append(
                            [
                                -getFinalPosition(block, lastBlockPos, yIter, x),
                                -getFinalPosition(nextBlock, 0, yIter2, x),
                            ]
                        )

    return clauses


def generatePVariableAssociations(pVar: int, qVariablesAssociated: list) -> list:
    clauses = []
    clauses.append([-pVar] + qVariablesAssociated)
    for qVar in qVariablesAssociated:
        clauses.append([pVar, -qVar])
    return clauses


def main(glucosePath: str, nonPath: str, pbmPath: str):
    width, height, maxBlockSize, rowsRules, columnsRules = loadNon(nonPath + ".non")
    to1D = generate2Dto1DTransform(width, height)
    from2DandBlockTo1D = generate2DAndBlockTo1D(to1D, width, height, maxBlockSize)

    variableCount = 1 # glucose starts counting variables from 1
    map1DToPPos = {}
    map1DToFinalPos = {}  # We have many empty positions
    map1DAssociatedWithPVar = (
        {}
    )  # For Constraints of q variables associated with p variables
    mapFinalPosTo2D = {}  # For decoding
    blockCount = 0
    clauses = []
    xPos = 0
    yPos = 0

    def getNewBlock():
        nonlocal blockCount
        newBlock = blockCount
        blockCount += 1
        return newBlock

    def getNewVariable():
        nonlocal variableCount
        newVar = variableCount
        variableCount += 1
        return newVar

    def getPVariable(y, x):
        pos = to1D(y, x)
        if pos in map1DToPPos:
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
        associatedPVar = getPVariable(y, x)
        map1DAssociatedWithPVar[associatedPVar].append(finalPos)  # Add to P constraints
        return finalPos

    for rowRule in rowsRules:
        blocksInRule = []
        blockSizes = []
        for blockSize in rowRule:
            block = getNewBlock()
            blocksInRule.append(block)
            blockSizes.append(blockSize)

            clauses += generateAllExactlyOneForBlock(
                block,
                yPos,
                0,
                blockSize,
                width,
                height,
                True,
                getFinalPosition,
                getNewVariable,
            )

            clauses += generateAllBlockFull(
                block, yPos, 0, blockSize, width, height, True, getFinalPosition,
            )
        clauses += generateAllNoOverlappingBlocksOnRowOrColumn(
            blocksInRule, yPos, 0, blockSizes, width, height, True, getFinalPosition,
        )
        yPos += 1  # Move to next row

    for columnRule in columnsRules:
        blocksInRule = []
        blockSizes = []
        for blockSize in columnRule:
            block = getNewBlock()
            blocksInRule.append(block)
            blockSizes.append(blockSize)

            clauses += generateAllExactlyOneForBlock(
                block,
                0,
                xPos,
                blockSize,
                width,
                height,
                False,
                getFinalPosition,
                getNewVariable,
            )

            clauses += generateAllBlockFull(
                block, 0, xPos, blockSize, width, height, False, getFinalPosition,
            )
        clauses += generateAllNoOverlappingBlocksOnRowOrColumn(
            blocksInRule, 0, xPos, blockSizes, width, height, False, getFinalPosition,
        )
        xPos += 1  # Move to next Column

    for pVar, associatedQVars in map1DAssociatedWithPVar.items():
        clauses += generatePVariableAssociations(pVar, associatedQVars)

    inputFile = nonPath + "_input.cnf"
    saveCnfFile(
        inputFile, variableCount - 1, clauses
    )  # Variables-1 because 0 is not a valid variable
    outputFile = nonPath + "_output.cnf"
    subprocess.call(
        [glucosePath, inputFile, outputFile],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    image = loadOuputCnf(outputFile, height, width, mapFinalPosTo2D)
    savePBM(pbmPath, image, height, width)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Not Enough Arguments", file=sys.stderr)
        print("{0} glucosePath nonPath pbmPath".format(sys.argv[0]), file=sys.stderr)
        exit(-1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
