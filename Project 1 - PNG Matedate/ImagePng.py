from Chunks import Chunk, IHDR, PLTE, IDAT, IEND, tIME, iTXt, tEXt, cHRM, sRGB, pHYs, sPLT
import cv2
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

#Funkcja create_png - pozwala na tworzenie testowego pliku zawierającego chunk sPLT
def create_png():
        tmp2 = open('tmp2.png', 'wb')
        data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x08\x90\x00\x00\x0bh\x08\x06\x00\x00\x00\xa6C\xccs\x00\x00\x00\rsPLTha\x00\x08\x30\x10\x20\x02\x06\x00\x06\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        tmp2.write(data)
        tmp2.close()


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
        if self.file.readable():
            if b'\x89PNG\r\n\x1a\n' == self.file.read1(8):
                self.magic_number = b'\x89PNG\r\n\x1a\n'
            else:
                print("Niepoprawnie wczytano magiczny numer")
        chunk_type = "noname"
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
                #self.chunk_plte = PLTE(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
                self.chunks_typical.append(PLTE(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "IDAT":
                self.chunks_idat.append(IDAT(chunk_length_byte, chunk_type, chunk_data, chunk_crc))
            elif chunk_type == "IEND":
                self.chunk_iend = IEND(chunk_length_byte, chunk_type, chunk_data, chunk_crc)    
            elif chunk_type == "tIME":
                #self.chunk_time = tIME(chunk_length_byte, chunk_type, chunk_data, chunk_crc) 
                self.chunks_typical.append(tIME(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "iTXt":
                #self.chunk_itxt = iTXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc) 
                self.chunks_typical.append(iTXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc))
            elif chunk_type == "tEXt":
                #self.chunk_text = tEXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc) 
                self.chunks_typical.append(tEXt(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "cHRM":
                #self.chunk_chrm = cHRM(chunk_length_byte, chunk_type, chunk_data, chunk_crc) 
                self.chunks_typical.append(cHRM(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "sRGB":
                #self.chunk_srgb = sRGB(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
                self.chunks_typical.append(sRGB(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "pHYs":
                #self.chunk_phys = pHYs(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
                self.chunks_typical.append(pHYs(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            elif chunk_type == "sPLT":
                #self.chunk_splt = sPLT(chunk_length_byte, chunk_type, chunk_data, chunk_crc)
                self.chunks_typical.append(sPLT(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
            else:
                self.chunks_others.append(Chunk(chunk_length_byte, chunk_type, chunk_data, chunk_crc)) 
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