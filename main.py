import sys


def loadNon(path : str):
    width = -1
    height = -1
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
        line = f.readline() # Type Header

        if (line.strip() == "rows"):
            # Read Rows first
            print("First Row Header: " + line.strip())
            for i in range(height):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    rowsRules[i].append(int(rule))

            # Read Columns
            line = f.readline() # Column Header
            print("Second Column Header: " + line.strip())
            for i in range(width):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    columnsRules[i].append(int(rule))
        else:
            # Read Columns first
            print("First Column Header: " + line.strip())
            for i in range(width):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    columnsRules[i].append(int(rule))

            # Read Rows
            line = f.readline() # Rows Header
            print("Second Row Header: " + line.strip())
            for i in range(height):
                line = f.readline()
                lineDiv = line.split(",")
                for rule in lineDiv:
                    rowsRules[i].append(int(rule))

        f.close()
    return width, height, rowsRules, columnsRules


def generate2Dto1DTransform(width, height):
    return (lambda y, x: x + y * width), 1, width

def main(glucosePath: str, nonPath: str, bmpPath: str):
    width, height, rowsRules, columnsRules = loadNon(nonPath + ".non")
    to1D, colStep, rowStep = generate2Dto1DTransform(width, height)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Not Enough Arguments", file=sys.stderr)
        print("{0} glucosePath nonPath bmpPath".format(sys.argv[0]), file=sys.stderr)
        exit(-1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
