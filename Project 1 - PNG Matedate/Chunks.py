class Chunk:
    def __init__(self, length, chunk_type, data, crc):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.crc = crc
    def __str__(self):
        info = "Chunk length: {0}, Chunk type: {1},  Chunk data: {2}, Chunk crc: {3}".format(self.length, self.chunk_type, self.data, self.crc)
        return info
            
    def __del__(self):
        print("Deleting chunk...")


class IHDR(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()

class PLTE(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    #def __str__(self):
        #super().__str__()

class IDAT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    #def __str__(self):
        #super().__str__()


class IEND(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    #def __str__(self):
        #super().__str__()

