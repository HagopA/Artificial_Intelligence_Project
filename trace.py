
class TraceFile:
    def __init__(self):
        self.file = open("tracemm.txt","w")

    def addLevel3(self, numOfNodes, level3):
        self.file.write(str(numOfNodes) + "\n" + "{1:1}".format(level3) + "\n" + "\n")

    def addLevel2(self, level2):
        for val in level2:
            self.file.write("{1:1}".format(val) + "\n")

        self.file.write("\n" + "\n")
