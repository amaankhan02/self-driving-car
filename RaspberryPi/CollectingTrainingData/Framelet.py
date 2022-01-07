class Framelet:
    def __init__(self, frameName, frame, cmd=None, steerDegree=None):
        """

        :param frameName:
        :param frame:
        :param cmd:
        :param steerDegree: range of +15 to -15, + = Right, - = Left, 0 = Center
        """
        self.frameName = frameName
        self.frame = frame
        self.cmd = cmd
        self.steerDegree = steerDegree;
