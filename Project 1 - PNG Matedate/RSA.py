from ParametersGeneratorRSA import ParametersGeneratorRSA
from ImagePng import ImagePng
from collections import deque
import logging
import random
import png
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome import Random
from Cryptodome.PublicKey import RSA as RSALibrary
import Cryptodome as crypto

#Klasa RSA
#Atrybuty:
# parametersRSA
# publicKey - klucz publiczny
# privateKey - klucz prywatny
# keySize - rozmiar klucza
# chunkBytesReduction - określa o ile bajtow w stosunku do dlugosci klucza ma byc mniejsza porcja danych
# singleByteChunkPart - dlugosc chunka jako pojedynczy bajt
# doubleByteChunkPart - dlugosc chunka jako podwojny bajt
# singleByteEncryptedChunkPart - rozmiar chunków zaszyfrowanych jako pojedynczy bajt
# doubleByteEncryptedChunkPart - rozmiar chunków zaszyfrowanych jako podwojny bajt
# primaryDataLength - pierwotna dlugosc danych
# initializationVector - wektor inicjalizujący dla trybu CBC
# 
# 
#Metody:
# _init_ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# _str_ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka w określony przez nas sposób)
# encryptECB - metoda szyfrujaca dane metoda ECB
# decryptECB - metoda deszydrujaca dane metoda ECB
# createEncryptedPng - metoda zapisuje zaszyfrowany obraz jako png
# createDescryptedPng - metoda zapisuje zdeszydrowany obraz jako png
# createPngWriter - metoda wybierajaca zapis obrazu w zaleznosci od ilosci bytow przypadajaca na jeden piksel
# splitData - dzieli dane na dwie grupy (jedna wczytywana do chunków IDAT, druga umieszczana na końcu pliku, po chunku IEND)
# concatenateData - łączy dane zawarte w chunkach IDAT z tymi, które znajdują się na końcu pliku, po chunku IEND
# encryptCBC - metoda szyfrujaca dane metoda CBC
# decryptCBC - metoda deszydrujaca dane metoda CBC
# encryptCrypto - szyfrowanie algorytmem RSA z wykorzystaniem gotowych bilbiotek
# rsa - wykonuje kryptograficzny algorytm RSA
class RSA:
    def __init__(self, keySize):
        self.parametersRSA = ParametersGeneratorRSA(keySize)
        # Klucz publiczny
        self.publicKey = self.parametersRSA.publicKey
        # Klucz prywatny
        self.privateKey = self.parametersRSA.privateKey
        # Dlugosc klucza
        self.keySize = keySize
        # Chunki, które idą do zaszyfrowania powinny mieć mniejszą długość niż klucz 
        self.chunkBytesReduction = 1
        # Dlugosc chunka jako pojedynczy bajt
        self.singleByteChunkPart = keySize // 8 - self.chunkBytesReduction
        # Dlugosc chunka jako podwojny bajt
        self.doubleByteChunkPart = keySize // 16 
        # Rozmiar chunków zaszyfrowanych jako pojedynczy bajt
        self.singleByteEncryptedChunkPart = keySize // 8
        # Rozmiar chunków zaszyfrowanych jako podwojny bajt
        self.doubleByteEncryptedChunkPart = keySize // 16
    #Szyfrowanie chunkow
    def encryptECB(self, data):
        #Zaszyfrowane dane
        encryptedData = []
        lastElementInEncryptedDataBlock = []
        self.primaryDataLength = len(data)
        #Podziel dane na długość jaka może być zaszyfrowana RSA (Odczytanie n bajtów)
        for i in range(0, len(data), self.singleByteChunkPart):
            #Odczytaj paczke danych i długości chunka jako pojedynczy bajt
            chunkToEncryptHex = bytes(data[i: i + self.singleByteChunkPart])
            #Zaszyfruj paczke danych używając klucza publicznego
            encryptedInt = pow(int.from_bytes(chunkToEncryptHex, 'big'), self.publicKey[0], self.publicKey[1])
            #Zapisz paczke danych w postaci hexadecymalnej
            encryptedHex = encryptedInt.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            #Zapisanie do danych 
            for i in range(self.singleByteChunkPart):
                encryptedData.append(encryptedHex[i])
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        encryptedData.append(lastElementInEncryptedDataBlock.pop())
        return encryptedData, lastElementInEncryptedDataBlock

    def decryptECB(self, data, dataAfterIend):
        dataToDecrypt = self.concatenateData(data, deque(dataAfterIend))
        decryptedData = []
        for i in range(0, len(dataToDecrypt), self.singleByteEncryptedChunkPart):
            chunkToDescryptHex = bytes(dataToDecrypt[i: i + self.singleByteEncryptedChunkPart])
            descryptedInt = pow(int.from_bytes(chunkToDescryptHex, 'big'), self.privateKey[0], self.privateKey[1])
            # Weryfikacja z jakim chunkiem mamy do czynienia (ostatni, krótki, jest traktowany inaczej)
            if len(decryptedData) + self.singleByteChunkPart > self.primaryDataLength:
                # ostatni chunk do odczytania (krótszy)
                decryptedHexLen = self.primaryDataLength - len(decryptedData)
            else:
                # standardowo do odszyfrowania stosujemy dlugosc taka sama jak do szyfrowania danych
                decryptedHexLen = self.singleByteChunkPart
            decryptedHex = descryptedInt.to_bytes(decryptedHexLen, 'big')
            for byte in decryptedHex:
                decryptedData.append(byte)
        return decryptedData

    def createDescryptedPng(self, decryptedData, bytesPerPixel, width, height, decryptedPngPath):
        pngWriter = self.createPngWriter(width, height, bytesPerPixel)
        pixelWidth = width * bytesPerPixel
        pixelRows = [decryptedData[i: i + pixelWidth] for i in range(0, len(decryptedData), pixelWidth)]

        f = open(decryptedPngPath, 'wb')
        pngWriter.write(f, pixelRows)
        f.close()

    def createEncryptedPng(self, encryptedData, bytesPerPixel, width, height, encryptedPngPath, lastElementInEncryptedDataBlock):
        idatData, dataAfterIend = self.splitData(encryptedData)
        pngWriter = self.createPngWriter(width, height, bytesPerPixel)
        pixelWidth = width * bytesPerPixel
        pixelRows = [idatData[i: i + pixelWidth] for i in range(0, len(idatData), pixelWidth)]

        f = open(encryptedPngPath, 'wb')
        pngWriter.write(f, pixelRows)
        f.write(bytes(lastElementInEncryptedDataBlock))
        f.write(bytes(dataAfterIend))
        f.close()

    def createPngWriter(self, width, height, bytesPerPixel):
        if bytesPerPixel == 1:
            pngWriter = png.Writer(width, height, greyscale=True)
        elif bytesPerPixel == 2:
            pngWriter = png.Writer(width, height, greyscale=True, alpha=True)
        elif bytesPerPixel == 3:
            pngWriter = png.Writer(width, height, greyscale=False)
        elif bytesPerPixel == 4:
            pngWriter = png.Writer(width, height, greyscale=False, alpha=True)
        return pngWriter

    def splitData(self, encryptedData):
        """
        The side effect of using the ECB mode with RSA is that IDAT length gets bigger.
        In order to NOT CHANGE THE METADATA, we are using hack.
        The hack is to put new pixels after IEND chunk, so image can be displayed properly AND
        further deciphering operation can be successfull.
        """
        encryptedData = deque(encryptedData)
        idatData = []
        dataAfterIend = []
        for i in range(self.primaryDataLength):
            idatData.append(encryptedData.popleft())
        for i in range(len(encryptedData)):
            dataAfterIend.append(encryptedData.popleft())
        return idatData, dataAfterIend

    def concatenateData(self, data, dataAfterIend: deque):
        dataToDecrypt = []
        for i in range(0, len(data), self.singleByteChunkPart):
            dataToDecrypt.extend(data[i:i + self.singleByteChunkPart])
            dataToDecrypt.append(dataAfterIend.popleft())
        dataToDecrypt.extend(dataAfterIend)
        return dataToDecrypt

    def encryptCBC(self, data):
        encryptedData = []
        decryptedData = []
        lastElementInEncryptedDataBlock = []
        self.primaryDataLength = len(data)
        self.initializationVector= random.getrandbits(self.keySize)
        prev = self.initializationVector

        for i in range(0, len(data), self.singleByteChunkPart):
            chunkToEncryptHex = bytes(data[i: i + self.singleByteChunkPart])

            prev = prev.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            prev = int.from_bytes(prev[:len(chunkToEncryptHex)], 'big')
            xor = int.from_bytes(chunkToEncryptHex, 'big') ^ prev

            encryptedInt = pow(xor, self.publicKey[0], self.publicKey[1])
            prev = encryptedInt

            encryptedHex = encryptedInt.to_bytes(self.singleByteEncryptedChunkPart, 'big')

            for i in range(self.singleByteChunkPart):
                encryptedData.append(encryptedHex[i])
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        encryptedData.append(lastElementInEncryptedDataBlock.pop())

        return encryptedData, lastElementInEncryptedDataBlock

    def decryptCBC(self, data, dataAfterIend):
        dataToDecrypt = self.concatenateData(data, deque(dataAfterIend))
        decryptedData = []
        prev = self.initializationVector

        for i in range(0, len(dataToDecrypt), self.singleByteEncryptedChunkPart):
            chunkToDecryptHex = bytes(dataToDecrypt[i: i + self.singleByteEncryptedChunkPart])

            decryptedInt = pow(int.from_bytes(chunkToDecryptHex, 'big'), self.privateKey[0], self.privateKey[1])

            # We don't know how long was the last original chunk (no matter what, chunks after encryption have fixd key-length size, so extra bytes could have been added),
            # so below, before creating decrpyted_hex of fixed size we check if adding it to decrpted_data wouldn't exceed the original_data_len
            # If it does, we know that the length of last chunk was smaller and we can retrieve it's length
            if len(decryptedData) + self.singleByteChunkPart > self.primaryDataLength:
                # last original chunk
                decryptedHexLen = self.primaryDataLength - len(decryptedData)
            else:
                # standard encryption_RSA_chunk length
                decryptedHexLen = self.singleByteChunkPart
            prev = prev.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            prev = int.from_bytes(prev[:decryptedHexLen], 'big')
            xor = prev ^ decryptedInt
            prev = int.from_bytes(chunkToDecryptHex, 'big')
            decryptedHex = xor.to_bytes(decryptedHexLen, 'big')
            for byte in decryptedHex:
                decryptedData.append(byte)

        return decryptedData

    def encryptCrypto(self, data):
        encryptedData = []
        lastElementInEncryptedDataBlock = []
        self.primaryDataLength = len(data)
        key = RSALibrary.construct((self.publicKey[1] , self.publicKey[0]))
        cipher = PKCS1_OAEP.new(key)    
        for i in range(0, len(data), self.doubleByteChunkPart):
            chunkToEncryptHex = bytes(data[i: i + self.doubleByteChunkPart])
            encryptedHex = cipher.encrypt(chunkToEncryptHex)
            for i in range(self.doubleByteChunkPart):
                encryptedData.append(encryptedHex[i])
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        encryptedData.append(lastElementInEncryptedDataBlock.pop())
        return encryptedData, lastElementInEncryptedDataBlock

    def rsa(self, img,  encrypted_file_path="encrypted.png", decrypted_file_path="decrypted.png", mode="ECB"):
        if mode == "ECB":
            cipher, after_iend_data_embedded = self.encryptECB(img.reconstructed_idat_data)
        elif mode == "CBC":
            cipher, after_iend_data_embedded = self.encryptCBC(img.reconstructed_idat_data)
        elif mode == "CRYPTO":
            cipher, after_iend_data_embedded = self.encryptCrypto(img.reconstructed_idat_data)
        self.createEncryptedPng(cipher, img.bytesPerPixel, img.chunk_ihdr.width,img.chunk_ihdr.height, encrypted_file_path, after_iend_data_embedded)

        new_png = ImagePng(encrypted_file_path)
        new_png.process_idat_data()

        if mode == "ECB":   
            decrypted_data = self.decryptECB(new_png.reconstructed_idat_data, new_png.after_iend_data)
        elif mode == "CBC":
            decrypted_data = self.decryptCBC(new_png.reconstructed_idat_data, new_png.after_iend_data)
        if mode != "CRYPTO":  
            self.createDescryptedPng(decrypted_data, new_png.bytesPerPixel, new_png.chunk_ihdr.width,new_png.chunk_ihdr.height, decrypted_file_path)