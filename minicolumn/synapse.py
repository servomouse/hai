

class Synapse:
    def __init__(self, weight, fatigue_rate, recover_rate):
        self.weight = weight
        self.learning_rate = 0.05
        self.average_input = 0

    def get_value(self, input_val):
        val = input_val * self.weight
        self.average_input = (self.average_input + input_val) / 2
        return val

    def update_weight(self, feedback):
        """
        Feedback: -1.0 to 1.0
        """
        if self.average_input > 0 and self.weight > 0:
            delta_sign = -1
        elif self.average_input < 0 and self.weight < 0:
            delta_sign = -1
        else:
            delta_sign = 1
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

    def get_weight(self):
        return self.weight


# s = Synapse(-0.5, 0.5, 0.3)
# for i in range(10):
#     v = 0.4
#     print(f"{v}: {s.get_value(v)}, fatigue: {s.get_fatigue()}")
