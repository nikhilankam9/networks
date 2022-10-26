import struct

class packet:
    def __init__(self, format) -> None:
        self.format = format
        self.struct = struct.Struct(format)
        
    def set_args(self, *args):
        self.args = args

    def pack(self):
        return self.struct.pack(*self.args)
    
    def unpack(self, s):
        return self.struct.unpack(s)

    def size(self):
        return self.struct.size