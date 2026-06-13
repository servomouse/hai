

class Synapse:
    def __init__(self, weight, fatigue_rate, recover_rate):
        self.weight = weight
        self.fatigue_rate = fatigue_rate
        self.recover_rate = recover_rate
        self.fatigue_val = 0
        self.learning_rate = 0.05
        self.average_input = 0
    
    def fatigue(self, input_val):
        add_fatigue = self.fatigue_rate * abs(input_val) * (1.0 - self.fatigue_val)
        self.fatigue_val += add_fatigue
        if self.fatigue_val < 0:
            self.fatigue_val = 0
        elif self.fatigue_val > 1.0:
            self.fatigue_val = 1.0
    
    def recover(self):
        recovered = self.recover_rate * self.fatigue_val
        self.fatigue_val -= recovered
        if self.fatigue_val < 0:
            self.fatigue_val = 0
    
    def get_value(self, input_val):
        self.recover()
        effective_weight = self.weight * (1.0 - self.fatigue_val)
        val = input_val * effective_weight
        self.fatigue(input_val)
        self.average_input = (self.average_input + input_val) / 2
        return val
    
    def update_weight(self, feedback):
        """
        Updates the weight based on feedback and recent activity (fatigue).
        Feedback: -1.0 to 1.0
        """
        if self.average_input > 0 and self.weight > 0:
            delta_sign = -1
        elif self.average_input < 0 and self.weight < 0:
            delta_sign = -1
        else:
            delta_sign = 1
        # delta_sign = 1 if self.weight >= 0 else -1

        # delta = self.learning_rate * feedback * self.fatigue_val * delta_sign
        # self.weight += delta
        # if feedback > self.learning_rate:
        #     self.weight -= self.learning_rate * delta_sign
        # elif feedback < -self.learning_rate:
        #     self.weight += self.learning_rate * delta_sign
        multiplier = 1 - abs(self.weight)
        if feedback > self.learning_rate:
            delta = -self.learning_rate * delta_sign
        elif feedback < -self.learning_rate:
            delta = self.learning_rate * delta_sign
        else:
            delta = 0
        
        self.weight += delta * multiplier
        
        # Clip the weight to prevent "runaway" synapses 
        self.weight = max(-1.0, min(1.0, self.weight))

    def get_fatigue(self):
        return self.fatigue_val

    def get_weight(self):
        return self.weight


# s = Synapse(-0.5, 0.5, 0.3)
# for i in range(10):
#     v = 0.4
#     print(f"{v}: {s.get_value(v)}, fatigue: {s.get_fatigue()}")
