
class TraceFile:
    def __init__(self):
        self.file = open("tracemm.txt","w")

    def addLevel3(self, numOfNodes, level3):
        self.file.write(str(numOfNodes) + "\n" + "{0:1}".format(level3) + "\n" + "\n")

    def addLevel2(self, level2):
        for val in level2:
            self.file.write("{0:1}".format(val[0]) + "\n")

        self.file.write("\n" + "\n")
        self.file.close()
        self.file = open("tracemm.txt", "a")
