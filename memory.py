

class Memory:
    def __init__(self):
        self.memories = []
        self.max_ret_items_num = 10

    def add_item(self, item):
        self.memories.append(item)
    
    def recall_items(self, tags):
        ret_items = []
        for item in self.memories:
            for tag in tags:
                if tag in item:
                    ret_items.append(item)
                break
            if len(ret_items) == self.max_ret_items_num:
                break
        return ret_items