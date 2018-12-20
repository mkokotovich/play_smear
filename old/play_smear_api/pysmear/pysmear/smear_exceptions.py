
class SmearNeedInput(Exception):
    """Raised when the engine needs user input"""
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}

class SmearUserHasSameName(Exception):
    """Raised when the user has the same name as an existing user"""
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}

