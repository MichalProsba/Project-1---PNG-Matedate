#Start bit to 
#End bit to convert
def convert_byte(data, start, end):
    return int.from_bytes(data[start-1:end],byteorder = "big", signed=False)

class Chunk:
    def __init__(self, length, chunk_type, data, crc):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.crc = crc
    def __str__(self):
        info = "Chunk length: {0}\nChunk type: {1}\nChunk data: {2}\nChunk crc: {3}\n".format(self.length, self.chunk_type, self.data, self.crc)
        return info
            
    #def __del__(self):
        #print("Deleting chunk...")


class IHDR(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        self.width = convert_byte(self.data, 1, 4)
        self.height = convert_byte(self.data, 5, 8)
        self.bit_depth = self.data[8]
        self.color_type = self.data[9]
        self.compression_method = self.data[10]
        self.filter_method = self.data[11]
        self.interlace_method = self.data[12]
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Width: {0}\nHeight: {1}\nBit Depth: {2}\nColor type: {3}\nCompression method: {4}\nFilter method: {5}\nInterlace method: {6}\n".format(self.width, self.height, self.bit_depth, self.color_type, self.compression_method, self.filter_method, self.interlace_method) + "================================================================================"
        
class PLTE(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()

class IDAT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()


class IEND(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()

