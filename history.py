

class History:
    def __init__(self):
        self.history = []   # TODO: Restore from file
        self.ret_arr_len = 10

    def add_item(self, item):
        self.history.append(item)

    def find_item(self, tags=[]):
        if len(tags) == 0:
            return self.history[-self.ret_array_len:]
        ret_arr = []
        for item in self.memory:
            for tag in tags:
                if tag in item:
                    ret_arr.append(item)
                    break
            if len(ret_arr) == self.ret_arr_len:
                break
        return ret_arr