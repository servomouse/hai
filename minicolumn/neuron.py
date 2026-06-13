import math
from synapse import Synapse


class Neuron:
    def __init__(self, weights, bias):
        self.synapses = [Synapse(w, 0.2, 0.1) for w in weights]
        self.bias = bias
        self.num_inputs = len(weights)
        self.fatigue_rate = 0.2
        self.recover_rate = 0.1
        self.fatigue_val = 0
        self.learning_rate = 0.01
        self.average_output = 0
    
    def fatigue(self, output_val):
        add_fatigue = self.fatigue_rate * abs(output_val) * (1.0 - self.fatigue_val)
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
    
    def activation_func(self, value):
        return math.tanh(value)
    
    def get_output(self, values):
        self.recover()
        if len(values) > self.num_inputs:
            raise Exception(f"Error: too many input values ({len(values)}); expected {self.num_inputs}")
        if len(values) < self.num_inputs:
            raise Exception(f"Error: not enough input values ({len(values)}); expected {self.num_inputs}")
        v = 0
        for i in range(len(values)):
            v += self.synapses[i].get_value(values[i])
        v += self.bias
        v = self.activation_func(v)
        self.fatigue(v)
        self.average_output = (self.average_output + v) / 2
        return v
    
    def update_bias(self, feedback):
        """
        Updates the bias based on feedback and recent activity (fatigue).
        Feedback: -1.0 to 1.0
        """
        # if self.average_output > 0 and self.bias > 0:
        #     delta_sign = -1
        # elif self.average_output < 0 and self.bias < 0:
        #     delta_sign = -1
        # else:
        #     delta_sign = 1
        # delta_sign = 1 if self.weight >= 0 else -1

        # delta = self.learning_rate * feedback * self.fatigue_val * delta_sign
        # self.bias += delta
        multiplier = 1 - abs(self.bias)
        if feedback > self.learning_rate:
            delta = -self.learning_rate
        elif feedback < -self.learning_rate:
            delta = self.learning_rate
        else:
            delta = 0
        
        self.bias += delta * multiplier
        
        # Clip the bias to prevent "runaway" synapses 
        self.bias = max(-1.0, min(1.0, self.bias))
    
    def update_weights(self, feedback):
        self.update_bias(feedback)
        for s in self.synapses:
            s.update_weight(feedback * self.fatigue_val)

    def get_fatigue(self):
        return self.fatigue_val

    def get_weights(self):
        return [s.get_weight() for s in self.synapses] + [self.bias]


n = Neuron([0.5, -0.2], 0.1)
inputs = [0.7, 0.1]
t_output = -0.3
for i in range(1000):
    o = n.get_output(inputs)
    e = o - t_output
    print(o, e, n.get_fatigue(), '\t', n.get_weights())
    if e < n.learning_rate:
        break
    n.update_weights(e)
print(n.get_output(inputs))
# print(n.get_output([0.4, 0.3]))
# print(n.get_output([0.4, 0.3]))

