from enum import Enum;

class Commands(Enum):
    #TODO: Right sql script to change all cmds with len 7 to len 4, must find an efficient way to change these
    NO_CMD = [0,0,0,0]
    LEFT = [1,0,0,0] #left forward
    RIGHT = [0,1,0,0] #right forward
    FORWARD = [0,0,1,0] #Only forward straight
    BACK = [0,0,0,1]
    STOP_ALL_MOTORS = [0,0,0,0,1,0,0]
    # BACK_MOTOR_STOP = [0,0,0,0,0,1,0] #dont think i should use this
    # RESET_STEER = [0,0,0,0,0,0,1]

    # def get_oneHotEncoded(self, command):

    @staticmethod
    def parseCommand(cmd):
        if cmd == Commands.NO_CMD or cmd == Commands.NO_CMD.value:
            return "NO_CMD"
        elif cmd == Commands.LEFT or cmd == Commands.LEFT.value:
            return "LEFT"
        elif cmd == Commands.RIGHT or cmd == Commands.RIGHT.value:
            return 'RIGHT'
        elif cmd == Commands.FORWARD or cmd == Commands.FORWARD.value:
            return 'FORWARD'
        elif cmd == Commands.BACK or cmd == Commands.BACK.value:
            return 'BACK'
        # elif cmd == Commands.STOP_ALL_MOTORS or cmd == Commands.STOP_ALL_MOTORS.value:
        #     return 'STOP ALL MOTORS'
        # elif cmd == Commands.BACK_MOTOR_STOP:
        #     return 'BACK_MOTOR_STOP'
        # elif cmd == Commands.RESET_STEER:
        #     return 'RESET_STEER'
        else:
            return None