from neuron import Neuron
import random

class Layer:
    def __init__(self, num_neurons=0, weights=None, num_inputs=0):
        """
        weights example: [
            [[0.1, 0.2, 0.3], 0.4],
            [[0.1, 0.2, 0.3], 0.4],
        ]
        where: 01...03 are weights, 0.4 is bias
        """
        if weights is not None:
            self.neurons = [Neuron(w, b) for w, b in weights]
        elif num_inputs > 0:
            self.neurons = [Neuron([random.uniform(-0.5, 0.5) for _ in range(num_inputs)], random.uniform(-0.5, 0.5)) for n in range(num_neurons)]
        else:
            raise Exception("Error: Need to provide either num_inputs or weights!")
    
    def get_output(self, inputs):
        return [n.get_output(inputs) for n in self.neurons]
    
    def apply_feedback(self, feedback):
        # Apply feedback neuronwise
        for i in range(len(self.neurons)):
            self.neurons[i].update_weights(feedback[i])


inputs = [0.1, 0.2, 0.3, 0.4]
target_outputs = [0.5, -0.1, 0.7, -0.4]

l = Layer(num_neurons=4, num_inputs=4)
for _ in range(200):
    o = l.get_output(inputs)
    print(o)
    e = [o[i]-target_outputs[i] for i in range(len(target_outputs))]
    l.apply_feedback(e)
