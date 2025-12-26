import queue
import os.path
import json


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
    """ The place where Global Graph is stored and the Architect works"""
    GLOBAL_GRAPH_FILE_PATH = "ltm_graph.json"
    _instance = None

    # Is a singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LongTermMemory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.LTM_queue = queue.Queue()
        if os.path.isfile(self.GLOBAL_GRAPH_FILE_PATH):
            with open(self.GLOBAL_GRAPH_FILE_PATH) as f:
                self.memory_graph = json.loads(f.read())
        else:
            self.memory_graph = {}

    def add_to_queue(self, graph):
        self.LTM_queue.put(graph)
    
    def _get_from_queue(self):
        g = self.LTM_queue.get()
        self.LTM_queue.task_done()
        return g
    
    def _update_graph(self, graph):
        pass

    def rebuild_graph(self):
        while not self.LTM_queue.empty():
            self._update_graph(self._get_from_queue())


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
