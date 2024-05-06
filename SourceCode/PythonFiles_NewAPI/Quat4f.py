from pyquaternion import Quaternion
class Quat4f:
    if __name__ == "__main__": 
        self.vectorBins = {
            "up" : np.array([0, 1, 0]),
            "down" : np.array([0, -1, 0]),

            "front" : np.array([0, 0, -1]),
            "front_up" : np.array([0, 1, -1]),
            "front_down" : np.array([0, -1, -1]),

            "front_left" : np.array([1, 0, -1]),
            "front_left_up" : np.array([1, 1, -1]),
            "front_left_down" : np.array([1, -1, -1]),

            "front_right" : np.array([-1, 0, -1]),
            "front_right_up" : np.array([-1, 1, -1]),
            "front_right_down" : np.array([-1, -1, -1]),

            "left" : np.array([1, 0, 0]),
            "left_up" : np.array([1, 1, 0]),
            "left_down" : np.array([1, -1, 0]),

            "back_left" : np.array([1, 0, 1]),
            "back_left_up" : np.array([1, 1, 1]),
            "back_left_down" : np.array([1, -1, 1]),

            "back" : np.array([0, 0, 1]),
            "back_up" : np.array([0, 1, 1]),
            "back_down" : np.array([0, -1, 1]),

            "back_right" : np.array([-1, 0, 1]),
            "back_right_up" : np.array([-1, 1, 1]),
            "back_right_down" : np.array([-1, -1, 1]),

            "right" : np.array([-1, 0, 0]),
            "right_up" : np.array([-1, 1, 0]),
            "right_down" : np.array([-1, -1, 0]),
        }

    def __init__(self, data):
        self.w = data[0]
        self.x = data[1]
        self.y = data[2]
        self.z = data[3]

#source:https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
def euler_from_quaternion():
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (self.w * self.x + self.y * self.z)
        t1 = +1.0 - 2.0 * (self.x * self.x + self.y * self.y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (self.w * self.y - self.z * self.x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (self.w * self.z + self.x * self.y)
        t4 = +1.0 - 2.0 * (self.y * self.y + self.z * self.z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

def get_direction(roll_x, pitch_y, yaw_z):
    direction = ""
    if roll_x != 0:
        if roll_x > 0:
            direction = direction + "Back"
        else: 
            direction = direction + "Front"
    if pitch_y != 0:
        if pitch_y > 0:
            direction = direction + "Left"
        else: 
            direction = direction + "Right"
    if yaw_z != 0:
        if yaw_z > 0:
            direction = direction + "Left"
        else: 
            direction = direction + "Right"