#Start bit to 
#End bit to convert
def convert_byte(data, start, end):
    return int.from_bytes(data[start:end+1],byteorder = "big", signed=False)

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
        self.width = convert_byte(self.data, 0, 3)
        self.height = convert_byte(self.data, 4, 7)
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
        #Paleta kolorow
        self.colors = []
        i = 0
        while i < int(convert_byte(self.length, 0, 3)):    
            R = self.data[i]
            G = self.data[i + 1]
            B = self.data[i + 2]
            self.colors.append([R, G, B])
            i+=3
    def __str__(self):
        i = 0
        plte_info = ""
        while i < int(convert_byte(self.length, 0, 3)/3):
            if not (i % 8):
                plte_info += "\n"
            plte_info += str(self.colors[i])
            i+=1
        return "================================================================================\n" + super().__str__() + str(plte_info) + "\n================================================================================\n"
       
class IDAT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()


class IEND(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "================================================================================\n"


class tIME(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        self.year = convert_byte(self.data, 0, 1)
        self.month = self.data[2]
        self.day = self.data[3]
        self.hour = self.data[4]
        self.minute = self.data[5]
        self.second = self.data[6]
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Year: {0}\nMonth: {1}\nDay: {2}\nHour: {3}\nMinute: {4}\nSecond: {5}\n".format(self.year, self.month, self.day, self.hour, self.minute, self.second) + "================================================================================"



class iTXt(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        all_data = self.data
        #all_data = b'Comment\x00\x07\x08german\x00slowoklucz\x00Created with GIMP'
        #print(all_data)
        index = all_data.index(b'\x00')
        #print(str(self.data))
        self.keyword = all_data[:index].decode('utf-8')
        #print(self.keyword)
        self.compression_flag = all_data[index+1]
        #print(self.compression_flag)
        self.itxt_compression_method = all_data[index+2]
        #print(self.itxt_compression_method)
        all_data = all_data[index+3:]
        index = all_data.index(b'\x00')
        self.language_tag = all_data[:index].decode('utf-8')
        #print(self.language_tag)
        all_data = all_data[index+1:]
        index = all_data.index(b'\x00')
        self.translated_keyword = all_data[:index].decode('utf-8')
        #print(self.translated_keyword)
        self.text = all_data[index+1:].decode('utf-8')
        #print(self.text)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Keyword: {0}\nCompression flag: {1}\nCompression method: {2}\nLanguage tag: {3}\nTranslated keyword: {4}\nText: {5}\n".format(self.keyword, self.compression_flag, self.itxt_compression_method, self.language_tag, self.translated_keyword, self.text) + "================================================================================"


class tEXt(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        all_data = self.data
        index = all_data.index(b'\x00')
        #print(str(self.data))
        self.keyword = all_data[:index].decode('utf-8')
        #print(self.keyword)
        self.text_string = all_data[index+1:].decode('utf-8')
        #print(self.text_string)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Keyword: {0}\nText string: {1}\n".format(self.keyword, self.text_string) + "================================================================================"

class cHRM(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        self.white_point_x = convert_byte(self.data, 0, 3)
        self.white_point_y = convert_byte(self.data, 4, 7)
        self.red_x = convert_byte(self.data, 8, 11)
        self.red_y = convert_byte(self.data, 12, 15)
        self.green_x = convert_byte(self.data, 16, 19)
        self.green_y = convert_byte(self.data, 20, 23)
        self.blue_x = convert_byte(self.data, 24, 27)
        self.blue_y = convert_byte(self.data, 28, 31)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "White point x: {0}\nWhite point y: {1}\nRed x: {2}\nRed y: {3}\nGreen x: {4}\nGreen y: {5}\nBlue x: {6}\nBlue y: {7}\n".format(self.white_point_x, self.white_point_y, self.red_x, self.red_y, self.green_x, self.green_y, self.blue_x, self.blue_y) + "================================================================================"



#class eXIf(Chunk):
#    def __init__(self, length, chunk_type, data, crc):
#        super().__init__(length, chunk_type, data, crc)
#    def __str__(self):
#        return "================================================================================\n" + super().__str__() + "================================================================================\n"
