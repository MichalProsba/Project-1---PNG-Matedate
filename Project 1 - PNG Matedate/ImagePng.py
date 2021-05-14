from Chunks import Chunk, IHDR, PLTE, IDAT, IEND, tIME, iTXt, tEXt, cHRM, sRGB, pHYs, sPLT
import cv2
import zlib
import numpy as np
from PIL import Image, PngImagePlugin
import PIL.Image
import sys

#Ilość bitów przeznaczona na informacje o długości w chunku
CHUNK_LENGTH = 4
#Ilość bitów przeznaczona na informacje o typie chunku w chunku
CHUNK_TYPE = 4
#Ilość bitów przeznaczona na informacje o sumie kontrolnej w chunku
CHUNK_CRC = 4

#Klasa ImagePng
#Atrybuty:
# file_name - nazwa pliku png
# file - uchwyt do pliku png
# img_color - obiekt przechowujący obraz w kolorze
# img_gray - obiekt przechowujący obraz w odcieniach szarości
# chunks_idat - lista zawierająca chunki idat
# chunks_other - lista zawierająca pozostałe, które nie są obligatoryjne
#Metody:
# _init_ - konstruktor parametryczny do którego wysyłamy ścieżkę do pliku
# show_picture_color - wyświetla obraz w kolorze
# show_picture_gray - wyświetla obraz w odcieniach szarości
# show_spectrum - wyświetla transformate Fouriera obrazu 
class ImagePng:
    def __init__(self, file):
        self.file_name = file
        self.file = open(self.file_name, "rb")
        self.chunks_idat=[]
        self.chunks_typical=[]
        self.chunks_others=[]
        self.plte = -1
        self.bytesPerPixel = 0
        self.reconstructed_idat_data=[]
        self.after_iend_data = bytes()
        if self.file.readable():
            if b'\x89PNG\r\n\x1a\n' == self.file.read(8):
                self.magic_number = b'\x89PNG\r\n\x1a\n'
            else:
                print("Niepoprawnie wczytano magiczny numer")
        chunk_type = "name"
        j=0
        while chunk_type != "IEND":
            chunk_length_byte = self.file.read(CHUNK_LENGTH)
            byte_sum = int.from_bytes(chunk_length_byte,byteorder = "big", signed=False)
            chunk_type=self.file.read(CHUNK_TYPE).decode('utf-8')
            chunk_data=self.file.read(byte_sum)
            chunk_crc=self.file.read(CHUNK_CRC)
            if chunk_type == "IHDR":
                self.chunk_ihdr = IHDR(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
            elif chunk_type == "PLTE":
                self.chunks_typical.append(PLTE(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
                self.plte = len(self.chunks_typical)
            elif chunk_type == "IDAT":
                self.chunks_idat.append(IDAT(chunk_length_byte, chunk_type, chunk_data, chunk_crc))
            elif chunk_type == "IEND":
                self.chunk_iend = IEND(chunk_length_byte, chunk_type, chunk_data, chunk_crc)    
            elif chunk_type == "tIME":
                self.chunks_typical.append(tIME(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "iTXt":
                self.chunks_typical.append(iTXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc))
            elif chunk_type == "tEXt":
                self.chunks_typical.append(tEXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "cHRM":
                self.chunks_typical.append(cHRM(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "sRGB":
                self.chunks_typical.append(sRGB(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "pHYs":
                self.chunks_typical.append(pHYs(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "sPLT":
                self.chunks_typical.append(sPLT(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            else:
                self.chunks_others.append(Chunk(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 

        #Wczytanie nadmiarowych danych, znajdujących się za chunkiem IEND
        while True:
            bytes_read = self.file.read(2)
            if not bytes_read:
                break
            self.after_iend_data += bytes_read
        self.file.close();

    def show_picture_color(self):
        img = cv2.imread(self.file_name, cv2.IMREAD_COLOR)
        cv2.imshow("Image color", img)
        self.file.close()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def show_picture_gray(self):
        img = cv2.imread(self.file_name, cv2.IMREAD_GRAYSCALE)
        cv2.imshow("Image gray", img)
        self.file.close()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def show_spectrum(self):
        img = cv2.imread(self.file_name, cv2.IMREAD_GRAYSCALE)
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20*np.log(np.sqrt(np.real(fshift[::]) ** 2 + np.imag(fshift[::]) ** 2))
        phase_spectrum = np.arctan(np.imag(fshift[::])/np.real(fshift[::]))
        magnitude_spectrum = np.asarray(magnitude_spectrum, dtype=np.uint8)
        phase_spectrum = np.asarray(phase_spectrum, dtype=np.uint8)
        cv2.imshow("Image Furrier Magnitude", magnitude_spectrum)
        cv2.imshow("Image Furrier Angle", phase_spectrum)
        cv2.imshow("Image", img)
        self.file.close()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def save_only_critical(self):
        critical_file = open("critical.png", 'wb')
        data = self.magic_number
        data += self.chunk_ihdr.length
        data += self.chunk_ihdr.chunk_type.encode('utf-8')
        data += self.chunk_ihdr.data
        data += self.chunk_ihdr.crc
        if self.plte != -1:
            data += self.chunks_typical[self.plte-1].length
            data += self.chunks_typical[self.plte-1].chunk_type.encode('utf-8')
            data += self.chunks_typical[self.plte-1].data
            data += self.chunks_typical[self.plte-1].crc
        for i in range(len(self.chunks_idat)):
            data += self.chunks_idat[i].length
            data += self.chunks_idat[i].chunk_type.encode('utf-8')
            data += self.chunks_idat[i].data
            data += self.chunks_idat[i].crc
        data += self.chunk_iend.length
        data += self.chunk_iend.chunk_type.encode('utf-8')
        data += self.chunk_iend.data
        data += self.chunk_iend.crc
        critical_file.write(data)
        critical_file.close()


    def getDecompressedIdat(self):
        IDAT_data = b''.join(chunk.data for chunk in self.chunks_idat)
        return zlib.decompress(IDAT_data)

    # Funkcja wykonująca dekompresję i defiltrację danych pliku PNG
    def process_idat_data(self):
        # https://pyokagan.name/blog/2019-10-14-png/
    
        # Określa ile bytów przypada na jeden pixel w zależności od typu koloru
        colorTypeToBytesPerPixel = {
            0: 1,
            2: 3,
            3: 1,
            4: 2,
            6: 4
        }

        # Dekompresowanie danych
        IDAT_data = self.getDecompressedIdat()

        # Wyznaczenie ile bytów przypada na jeden pixel
        self.bytesPerPixel = colorTypeToBytesPerPixel.get(self.chunk_ihdr.color_type)

        # Wyznaczenie spodziewanej długości chunków IDAT
        width = self.chunk_ihdr.width
        height = self.chunk_ihdr.height
        expected_IDAT_data_len = height * (1 + width * self.bytesPerPixel)

        assert expected_IDAT_data_len == len(IDAT_data), "Nie poprawna ilość danych po dekompresji."
        stride = width * self.bytesPerPixel

        # Funkcja wykorzystana do defiltracji typu 4
        def paeth_predictor(a, b, c):
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                Pr = a
            elif pb <= pc:
                Pr = b
            else:
                Pr = c
            return Pr

        # Funkcja wykorzystana do defiltracji do typów: 1,3,4
        def recon_a(r, c):
            return self.reconstructed_idat_data[r * stride + c - self.bytesPerPixel] if c >= self.bytesPerPixel else 0

        # Funkcja wykorzystana do defiltracji do typów: 2,3,4
        def recon_b(r, c):
            return self.reconstructed_idat_data[(r-1) * stride + c] if r > 0 else 0

        # Funkcja wykorzystana do defiltracji typu 4
        def recon_c(r, c):
            return self.reconstructed_idat_data[(r-1) * stride + c - self.bytesPerPixel] if r > 0 and c >= self.bytesPerPixel else 0

        # Defiltrowanie 
        i = 0
        for r in range(height): # dla kazdej linii skanowania
            filter_type = IDAT_data[i] # pierwszy bajt w linii skanowania
            i += 1
            for c in range(stride): # dla kazdego bajtu w lini skanowania
                filt_x = IDAT_data[i]
                i += 1
                if filter_type == 0: # Brak
                    recon_x = filt_x
                elif filter_type == 1: # typ_1 filtru
                    recon_x = filt_x + recon_a(r, c)
                elif filter_type == 2: # typ_2 filtru
                    recon_x = filt_x + recon_b(r, c)
                elif filter_type == 3: # typ_3 filtru
                    recon_x = filt_x + (recon_a(r, c) + recon_b(r, c)) // 2
                elif filter_type == 4: # typ_4 filtru
                    recon_x = filt_x + paeth_predictor(recon_a(r, c), recon_b(r, c), recon_c(r, c))
                else:
                    raise Exception('unknown filter type: ' + str(filter_type))
                self.reconstructed_idat_data.append(recon_x & 0xff) # usunięcie bajtu