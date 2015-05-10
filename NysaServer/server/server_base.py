
class ScriptBase(type):

    def __init__(cls, name, bases, attrs): 
        if cls is None:
            return

        if not hasattr(cls, "plugins"):
            cls.plugins = []

        else:
            cls.plugins.append(cls)


class ServerBase:
    __metaclass__ = ScriptBase

    def __init__(self):
        super(ServerBase, self).__init__()

    def setup(self, nysa):
        self.n = nysa
    
