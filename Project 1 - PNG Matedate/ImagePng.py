from Chunks import Chunk, IHDR, PLTE, IDAT, IEND

#Constant length of chunk
CHUNK_LENGTH = 4
#Constant typ of chunk
CHUNK_TYPE = 4
#Constant symbol CRC
CHUNK_CRC = 4
aaaaaaaaaaaaaaaaaaa\''
class ImagePng:
    #Const magic number
    magic_number=b'\x89PNG\r\n\x1a\n'
    #Constructor
    def __init__(self, file):
        #Open file
        self.file = open(file, "rb")
        #If file is readable
        if self.file.readable():
            #If magic number is right
            if ImagePng.magic_number == self.file.read1(8):
                print("Poprawnie wczytano magiczny numer")
                self.magic_number = ImagePng.magic_number
            else:
                print("Niepoprawnie wczytano magiczny numer")
        
        chunk_length_byte = self.file.read(CHUNK_LENGTH)
        print(chunk_length_byte)
        chunk_length_list = list(chunk_length_byte)
        print(chunk_length_list)
        byte_sum = chunk_length_list[0] + chunk_length_list[1] + chunk_length_list[2]
        self.ihdr = IHDR(chunk_length_byte, self.file.read(CHUNK_TYPE), self.file.read(byte_sum), self.file.read(CHUNK_CRC))  

        #self.ihdr_data = int.from_bytes(self.file.read(3), byteorder="big", signed=False)
        #print(self.ihdr_data)
      

   
    def __del__(self):
        print("Closing file...")
        self.file.close()
        