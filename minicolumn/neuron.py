import math
from synapse import Synapse


class Neuron:
    def __init__(self, weights, bias):
        self.synapses = [Synapse(w, 0.2, 0.1) for w in weights]
        self.bias = bias
        self.num_inputs = len(weights)
        self.learning_rate = 0.01
    
    def activation_func(self, value):
        return math.tanh(value)
    
    def get_output(self, values):
        if len(values) > self.num_inputs:
            raise Exception(f"Error: too many input values ({len(values)}); expected {self.num_inputs}")
        if len(values) < self.num_inputs:
            raise Exception(f"Error: not enough input values ({len(values)}); expected {self.num_inputs}")
        v = 0
        for i in range(len(values)):
            v += self.synapses[i].get_value(values[i])
        v += self.bias
        v = self.activation_func(v)
        return v
    
    def update_bias(self, feedback):
        multiplier = 1 - abs(self.bias)
        if feedback > self.learning_rate:
            delta = -self.learning_rate
        elif feedback < -self.learning_rate:
            delta = self.learning_rate
        else:
            delta = 0
        
        self.bias += delta * multiplier

        self.bias = max(-1.0, min(1.0, self.bias))
    
    def update_weights(self, feedback):
        self.update_bias(feedback)
        for s in self.synapses:
            s.update_weight(feedback)

    def get_weights(self):
        return [s.get_weight() for s in self.synapses] + [self.bias]


n = Neuron([0.5, -0.2], 0.1)
inputs = [0.7, 0.1]
t_output = -0.3
for i in range(1000):
    o = n.get_output(inputs)
    e = o - t_output
    print(o, e, '\t', n.get_weights())
    if e < n.learning_rate:
        break
    n.update_weights(e)
print(n.get_output(inputs))
# print(n.get_output([0.4, 0.3]))
# print(n.get_output([0.4, 0.3]))

