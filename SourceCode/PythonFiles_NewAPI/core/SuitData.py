

class SuitData:
    def __init__(self, nodeData, jointData):
        self.nodeData = nodeData
        self.jointData = jointData
        self.label = None #is type in ImuDataObject
        self.segment = None