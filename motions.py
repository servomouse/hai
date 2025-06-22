

class Motions:
    def __init__(self, target):
        self.target = target
        self.actions = {
            0x03: self.move_manipulator_zp,
            0x02: self.move_manipulator_zm,
            0x05: self.move_manipulator_yp,
            0x04: self.move_manipulator_ym,
            0x09: self.move_manipulator_xp,
            0x08: self.move_manipulator_xm,
            0x11: self.move_self_zp,
            0x10: self.move_self_zm,
            0x21: self.move_self_yp,
            0x20: self.move_self_ym,
            0x41: self.move_self_xp,
            0x40: self.move_self_xm,
            0x81: self.rotate_self_cw,
            0x80: self.rotate_self_ccw,
        }

    def do_motion(self, action, param):
        if action in self.actions:
            self.actions[action](param)
    
    def move_manipulator_zp(self, param):
        self.target.move("manipulator", "z", "pos", param)
    
    def move_manipulator_zm(self, param):
        self.target.move("manipulator", "z", "neg", param)
    
    def move_manipulator_yp(self, param):
        self.target.move("manipulator", "y", "pos", param)
    
    def move_manipulator_ym(self, param):
        self.target.move("manipulator", "y", "neg", param)
    
    def move_manipulator_xp(self, param):
        self.target.move("manipulator", "x", "pos", param)
    
    def move_manipulator_xm(self, param):
        self.target.move("manipulator", "x", "neg", param)
    
    def move_self_zp(self, param):
        self.target.move("observer", "z", "pos", param)
    
    def move_self_zm(self, param):
        self.target.move("observer", "z", "neg", param)
    
    def move_self_yp(self, param):
        self.target.move("observer", "y", "pos", param)
    
    def move_self_ym(self, param):
        self.target.move("observer", "y", "neg", param)
    
    def move_self_xp(self, param):
        self.target.move("observer", "x", "pos", param)
    
    def move_self_xm(self, param):
        self.target.move("observer", "x", "neg", param)
    
    def rotate_self_cw(self, param):
        self.target.rotate("observer", "cw", param)
    
    def rotate_self_ccw(self, param):
        self.target.rotate("observer", "ccw", param)