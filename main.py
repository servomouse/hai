#---------------------------------------
# Basic elements
#---------------------------------------
class Node:
    def __init__(self, vector, network, LTM):
        self.vector = vector
        self.network = network
        self.LTM = LTM
        self.input_links = []
        self.output_links = []
    
    def add_input_link(self, new_link):
        if new_link not in self.input_links:
            self.input_links.append(new_link)
    
    def remove_input_link(self, link):
        if link in self.input_links:
            # May contain only one entry of the link
            self.input_links.remove(link)

    def add_new_output_link(self, new_link):
        if new_link not in self.output_links:
            self.output_links.append(new_link)

    def remove_new_output_link(self, link):
        if link in self.output_links:
            # May contain only one entry of the link
            self.output_links.remove(link)


class GraphBuilder:
    def __init__(self):
        self.graph = None

    def create_new_graph(self):
        pass

    def add_node(self):
        pass

    def move_graph_to_STM(self):
        pass

    def get_graph_to_STM(self):
        pass

    def move_graph_to_LTM(self):
        pass


class Architect:
    def __init__(self):
        pass


#---------------------------------------
# Basic locations
#---------------------------------------


class LongTermMemory:
    _instance = None

    # Is a singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LongTermMemory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass


class ShortTermMemory:
    _instance = None

    # Is a singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ShortTermMemory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass


class ThinkingCore:
    _instance = None

    # Is a singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThinkingCore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass
