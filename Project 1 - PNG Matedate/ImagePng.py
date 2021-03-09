from Chunks import Chunk, IHDR, PLTE, IDAT, IEND

#Constant length of chunk
CHUNK_LENGTH = 4
#Constant typ of chunk
CHUNK_TYPE = 4
#Constant symbol CRC
CHUNK_CRC = 4

class ImagePng:
    #Const magic number
    magic_number=b'\x89PNG\r\n\x1a\n'
    #Constructor
    def __init__(self, file):
        #Open file
        self.file = open(file, "rb")

        self.chunks_idat=[]
        self.chunks_others=[]
        self.chunk_ihdr=0
        self.chunk_plte=0
        self.chunk_iend=0

        #If file is readable
        if self.file.readable():
            #If magic number is right
            if ImagePng.magic_number == self.file.read1(8):
                print("Poprawnie wczytano magiczny numer")
                self.magic_number = ImagePng.magic_number
            else:
                print("Niepoprawnie wczytano magiczny numer")
        
        chunk_type = b'noname'
        j=0
        while chunk_type != b'IEND':
            chunk_length_byte = self.file.read(CHUNK_LENGTH)
            #print(chunk_length_byte)
            chunk_length_list = list(chunk_length_byte)
            #print(chunk_length_list)
            #int.from_bytes(b'\xfc\x00', byteorder='big', signed=True)
            byte_sum = int.from_bytes(chunk_length_byte,byteorder = "big", signed=False)
            #byte_sum = sum(chunk_length_list)
            #print(byte_sum)
            chunk_type=self.file.read(CHUNK_TYPE)
            #print(chunk_type)
            chunk_data=self.file.read(byte_sum)
            #print(chunk_data)
            chunk_crc=self.file.read(CHUNK_CRC)
            #print(chunk_crc)
            #x = input()
            if chunk_type == b'IHDR':
                self.chunk_ihdr = IHDR(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
            elif chunk_type == b'PLTE':
                self.chunk_plte = PLTE(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
            elif chunk_type == b'IDAT':
                self.chunks_idat.append(IDAT(chunk_length_byte, chunk_type, chunk_data, chunk_crc))
            elif chunk_type == b'IEND':
                self.chunk_iend = IEND(chunk_length_byte, chunk_type, chunk_data, chunk_crc)     
            else:
                self.chunks_others.append(Chunk(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 






        #self.ihdr_data = int.from_bytes(self.file.read(3), byteorder="big", signed=False)
        #print(self.ihdr_data)
      

   
    def __del__(self):
        print("Closing file...")
        self.file.close()
        