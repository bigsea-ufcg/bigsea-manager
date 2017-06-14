import threading

class ID_Generator:
    
    def __init__(self):
        self.id = 0
        self.id_generator_lock = threading.RLock()
        
    def get_ID(self):
        with self.id_generator_lock:
            _id = self.id
            self.id += 1
            return str(_id)