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
# doubleByteChunkPart - dlugosc chunka jako dwa bajty
# singleByteEncryptedChunkPart - rozmiar chunków zaszyfrowanych jako pojedynczy bajt
# doubleByteEncryptedChunkPart - rozmiar chunków zaszyfrowanych jako podwojny bajt
# primaryDataLength - pierwotna dlugosc danych
# initializationVector - wektor inicjalizujący dla trybu CBC
# 
# 
#Metody:
# _init_ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# _str_ - przeciążenie wyświetlania (pozwala wyświetlić zawartość obiektu typu RSA w określony przez nas sposób)
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
        self.doubleByteChunkPart = keySize // 16 - self.chunkBytesReduction
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
            #Odczytaj paczke danych o długości bajtów mniejszej niż klucz
            chunkToEncryptHex = bytes(data[i: i + self.singleByteChunkPart])
            #Zaszyfruj paczke danych używając klucza publicznego
            encryptedInt = pow(int.from_bytes(chunkToEncryptHex, 'big'), self.publicKey[0], self.publicKey[1])
            #Zapisz paczke danych w postaci hexadecymalnej zamieniamy na ilość bajtów o długości klucza,
            #aby zapewnić że klucz zawsze będzie większy co do wartości
            encryptedHex = encryptedInt.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            #Zapisanie do danych 
            #Aby zapewnić poprawne wyświatlanie danych, sztucznie dodany byte odcinamy i wrzucamy do osobnej tablicy,
            #Dane te zostana dodane na koniec pliku za chunkiem iend
            for i in range(self.singleByteChunkPart):
                #Dodanie tyle danych jaka jest dlugosc bloku tekstu jawnego
                encryptedData.append(encryptedHex[i])
            # Odcięcie ostatniego elementu i dodanie go do osobnej tablicy
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        #Dodanie do odszyfrowanych danych ostatniego bajta odpowiedzialnego za koniec czytania
        encryptedData.append(lastElementInEncryptedDataBlock.pop())
        # encryptedData - element zwraca ilosc bajtow rowna dlugosci bloku jawnego 
        # lastElementInEncryptedDataBlock - zwraca nadmiarowa ilosc bajtow, ktora trafi poza blok
        return encryptedData, lastElementInEncryptedDataBlock

    # Deszyfrowanie danych
    def decryptECB(self, data, dataAfterIend):
        # Sklejenie danych zawartych w chunkach IDAT i tych umieszczonych za chunkiem IEND
        dataToDecrypt = self.concatenateData(data, deque(dataAfterIend))
        decryptedData = []
        # Pętla iterująca po danych zaszyfrowanych
        for i in range(0, len(dataToDecrypt), self.singleByteEncryptedChunkPart):
            # Zamienia na byty potrzbne do deszyfrowania dane
            chunkToDescryptHex = bytes(dataToDecrypt[i: i + self.singleByteEncryptedChunkPart])
            # Deszyfruje paczkę przygotowanych danych
            descryptedInt = pow(int.from_bytes(chunkToDescryptHex, 'big'), self.privateKey[0], self.privateKey[1])
            # Weryfikacja z jakim chunkiem mamy do czynienia (ostatni, krótki, jest traktowany inaczej)
            if len(decryptedData) + self.singleByteChunkPart > self.primaryDataLength:
                # Ostatni chunk do odczytania (krótszy)
                decryptedHexLen = self.primaryDataLength - len(decryptedData)
            else:
                # Standardowo do odszyfrowania stosujemy dlugosc taka sama jak do szyfrowania danych
                decryptedHexLen = self.singleByteChunkPart
            # Zamiana deszyfrowanych danych na byty
            decryptedHex = descryptedInt.to_bytes(decryptedHexLen, 'big')
            # Łączenie wszystkich bytów po deszyfracji w jedną tablicę
            for byte in decryptedHex:
                decryptedData.append(byte)
        return decryptedData

    #Zapisanie zaszyfrowanego obrazu w postaci blokow o dlugosci tekstu jawnego oraz danych znajdujacych sie za chunkiem IEND o dlugosci bloku nadmiarowych danych
    def createEncryptedPng(self, encryptedData, bytesPerPixel, width, height, encryptedPngPath, lastElementInEncryptedDataBlock):
        #Podzielenie danych na bloki danych rownych tekstowi jawnego oraz nadmiarowych danych znajdujacych sie po chunku IEND
        idatData, dataAfterIend = self.splitData(encryptedData)
        #Przygotowanie instancji pngWriter
        pngWriter = self.createPngWriter(width, height, bytesPerPixel)
        #Szerokość obrazu w pixelach
        pixelWidth = width * bytesPerPixel
        #Wszystkie wiersze obrazu
        pixelRows = [idatData[i: i + pixelWidth] for i in range(0, len(idatData), pixelWidth)]
        #Otwarcie pliku w trybie write binary i zapis danych
        f = open(encryptedPngPath, 'wb')
        #Zapisanie do pliku
        pngWriter.write(f, pixelRows)
        f.write(bytes(lastElementInEncryptedDataBlock))
        f.write(bytes(dataAfterIend))
        #Zamknięcie pliku
        f.close()

    #Zapisanie odszyfrowanego obrazu 
    def createDescryptedPng(self, decryptedData, bytesPerPixel, width, height, decryptedPngPath):
        # Przygotowanie instancji pngWriter, który umożliwia hermetyzację danych dotyczących pliku PNG
        pngWriter = self.createPngWriter(width, height, bytesPerPixel)
        # Szerokośc obrazu w pixelach
        pixelWidth = width * bytesPerPixel
        # Wszystkie wiersze obrazu
        pixelRows = [decryptedData[i: i + pixelWidth] for i in range(0, len(decryptedData), pixelWidth)]
        # Otwarcie pliku w trybie write binary i zapis danych
        f = open(decryptedPngPath, 'wb')
        #Zapisanie do pliku
        pngWriter.write(f, pixelRows)
        #Zamknięcie pliku
        f.close()

    # Funkcja tworząca instację pngWriter w zależności od bytów na pixel (typu obrazu)
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

    # Dzieli zaszyfrowane dane na te, które mieszczą się w chunkach IDAT oraz te, które umieścimy za chunkiem IEND
    def splitData(self, encryptedData):
        encryptedData = deque(encryptedData)
        idatData = []
        dataAfterIend = []
        for i in range(self.primaryDataLength):
            idatData.append(encryptedData.popleft())
        for i in range(len(encryptedData)):
            dataAfterIend.append(encryptedData.popleft())
        return idatData, dataAfterIend

    #Sklejenie blokow danych nadmiarowych znajdujacych sie za iendem oraz blokow danych o dlugosci tekstu jawnego w jeden blok danych
    def concatenateData(self, data, dataAfterIend: deque):
        dataToDecrypt = []
        for i in range(0, len(data), self.singleByteChunkPart):
            dataToDecrypt.extend(data[i:i + self.singleByteChunkPart])
            dataToDecrypt.append(dataAfterIend.popleft())
        dataToDecrypt.extend(dataAfterIend)
        return dataToDecrypt

    #Sklejenie blokow danych nadmiarowych znajdujacych sie za iendem oraz blokow danych o dlugosci tekstu jawnego w jeden blok danych
    def concatenateDoubleData(self, data, dataAfterIend: deque):
        dataToDecrypt = []
        for i in range(0, len(data), self.singleByteChunkPart):
            dataToDecrypt.extend(data[i:i + self.singleByteChunkPart])
            dataToDecrypt.append(dataAfterIend.popleft())
            dataToDecrypt.append(dataAfterIend.popleft())
        dataToDecrypt.extend(dataAfterIend)
        return dataToDecrypt

    #Szyfrowanie chunkow
    def encryptCBC(self, data):
        # tablica zaszyfrowanych danych
        encryptedData = []
        # tablica sztucznie dodanych bytów
        lastElementInEncryptedDataBlock = []
        # długość pierwotnych danych
        self.primaryDataLength = len(data)
        # wektor inicjalizujący, potrzebny przy szyfrowaniu pierwszej paczki danych
        self.initializationVector= random.getrandbits(self.keySize)
        prev = self.initializationVector

        # pętla w której iterujemy po danych do zaszyfrowania
        for i in range(0, len(data), self.singleByteChunkPart):
            # paczka danych do zaszyfrowania zapisana w bytach
            chunkToEncryptHex = bytes(data[i: i + self.singleByteChunkPart])
            # poprzednia paczka zaszyfrowanych danych w postaci bytów
            prev = prev.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            # poprzednia paczka zaszyfrowanych danych w postaci inta
            prev = int.from_bytes(prev[:len(chunkToEncryptHex)], 'big')
            # operacja xor poprzednich zaszyfrowanych danych oraz danych tekstu jawnego ktore chcemy zaszyfrowac
            xor = int.from_bytes(chunkToEncryptHex, 'big') ^ prev
            # szyfrowania danych
            encryptedInt = pow(xor, self.publicKey[0], self.publicKey[1])
            # przygotowanie poprzednika dla następnej iteracji pętli
            prev = encryptedInt
            # konwersja zaszyfrowanych danych do postaci bytów
            encryptedHex = encryptedInt.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            #Zapisanie do danych 
            #Aby zapewnić poprawne wyświatlanie danych, sztucznie dodany byte odcinamy i wrzucamy do osobnej tablicy,
            #Dane te zostana dodane na koniec pliku za chunkiem iend
            for i in range(self.singleByteChunkPart):
                #Dodanie tyle danych jaka jest dlugosc bloku tekstu jawnego
                encryptedData.append(encryptedHex[i])
            # Odcięcie ostatniego elementu i dodanie go do osobnej tablicy
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        #Dodanie do odszyfrowanych danych ostatniego bajta odpowiedzialnego za koniec czytania
        encryptedData.append(lastElementInEncryptedDataBlock.pop())
        # encryptedData - element zwraca ilosc bajtow rowna dlugosci bloku jawnego 
        # lastElementInEncryptedDataBlock - zwraca nadmiarowa ilosc bajtow, ktora trafi poza blok
        return encryptedData, lastElementInEncryptedDataBlock

    #Deszyfrowanie chunkow
    def decryptCBC(self, data, dataAfterIend):
        # dane do deszyfracji
        dataToDecrypt = self.concatenateData(data, deque(dataAfterIend))
        # dane po deszyfrowaniu
        decryptedData = []
        # pobranie pierwotnego wektora inicjalizującego
        prev = self.initializationVector
        # pętla w której iterujemy po danych do deszyfracji
        for i in range(0, len(dataToDecrypt), self.singleByteEncryptedChunkPart):
            # paczka danych do deszyfracji w postaci bytów
            chunkToDecryptHex = bytes(dataToDecrypt[i: i + self.singleByteEncryptedChunkPart])
            # deszyfrowana paczka danych
            decryptedInt = pow(int.from_bytes(chunkToDecryptHex, 'big'), self.privateKey[0], self.privateKey[1])
            # Weryfikacja z jakim chunkiem mamy do czynienia (ostatni, krótki, jest traktowany inaczej)
            if len(decryptedData) + self.singleByteChunkPart > self.primaryDataLength:
                # Ostatni chunk do odczytania (krótszy)
                decryptedHexLen = self.primaryDataLength - len(decryptedData)
            else:
                # Standardowo do odszyfrowania stosujemy dlugosc taka sama jak do szyfrowania danych
                decryptedHexLen = self.singleByteChunkPart
            # zamiana poprzednika na byty
            prev = prev.to_bytes(self.singleByteEncryptedChunkPart, 'big')
            # zamiana poprzednika na inta
            prev = int.from_bytes(prev[:decryptedHexLen], 'big')
            # operacja xor poprzednich zaszyfrowanych danych oraz danych, które chcemy odszyfrować
            xor = prev ^ decryptedInt
            # przypisanie zaszyfrowanych danych do poprzednich
            prev = int.from_bytes(chunkToDecryptHex, 'big')
            # zamiana rozszyfrowanych danych w postaci inta na postac hexadecymalna
            decryptedHex = xor.to_bytes(decryptedHexLen, 'big')
            # Łączenie wszystkich bytów po deszyfracji w jedną tablicę
            for byte in decryptedHex:
                decryptedData.append(byte)
        return decryptedData

    # Szyfrowanie danych za pomocą algorytmu RSA z gotowej bilbioteki
    def encryptCrypto(self, data):
        # zaszyfrowane dane
        encryptedData = []
        # ostatni (sztucznie wygenrowany byte) paczki danych
        lastElementInEncryptedDataBlock = []
        # długość pierwotnych danych
        self.primaryDataLength = len(data)
        # inicjalizacja klucza
        key = RSALibrary.construct((self.publicKey[1] , self.publicKey[0]))
        # asymetryczny szyfr oparty na algorytmie RSA
        cipher = PKCS1_OAEP.new(key)  
        # pętla iterująca po danych do zaszyfrowania
        for i in range(0, len(data), self.doubleByteChunkPart):
            # paczka danych do zaszyfrowania w postaci bytów
            chunkToEncryptHex = bytes(data[i: i + self.doubleByteChunkPart])
            # paczka zaszyfrowanych danych
            encryptedHex = cipher.encrypt(chunkToEncryptHex)
            #Zapisanie do danych 
            #Aby zapewnić poprawne wyświatlanie danych, sztucznie dodany byte odcinamy i wrzucamy do osobnej tablicy,
            #Dane te zostana dodane na koniec pliku za chunkiem iend
            for i in range(self.doubleByteChunkPart):
                #Dodanie tyle danych jaka jest dlugosc bloku tekstu jawnego
                encryptedData.append(encryptedHex[i])
            # Odcięcie ostatniego elementu i dodanie go do osobnej tablicy
            lastElementInEncryptedDataBlock.append(encryptedHex[-2])
            lastElementInEncryptedDataBlock.append(encryptedHex[-1])
        # Dodanie do odszyfrowanych danych ostatniego bajta odpowiedzialnego za koniec czytania
        encryptedData.append(lastElementInEncryptedDataBlock.pop())
        # encryptedData - element zwraca ilosc bajtow rowna dlugosci bloku jawnego 
        # lastElementInEncryptedDataBlock - zwraca nadmiarowa ilosc bajtow, ktora trafi poza blok
        return encryptedData, lastElementInEncryptedDataBlock

    #def decryptCrypto(self, data, dataAfterIend):
    #    # dane do deszyfracji
    #    dataToDecrypt = self.concatenateDoubleData(data, deque(dataAfterIend))
    #    # dane po deszyfrowaniu
    #    decryptedData = []
    #    # inicjalizacja klucza
    #    key = RSALibrary.construct((self.privateKey[1] , self.privateKey[0]))
    #    # asymetryczny szyfr oparty na algorytmie RSA
    #    cipher = PKCS1_OAEP.new(key)  
    #    # pętla iterująca po danych do zaszyfrowania
    #    for i in range(0, len(dataToDecrypt), self.doubleByteEncryptedChunkPart):
    #        # paczka danych do zaszyfrowania w postaci bytów
    #        chunkToDecryptHex = bytes(data[i: i + self.doubleByteChunkPart])
    #        # paczka zaszyfrowanych danych
    #        encryptedHex = cipher.decrypt(chunkToDecryptHex)
    #        if len(decryptedData) + self.doubleByteChunkPart > self.primaryDataLength:
    #            # Ostatni chunk do odczytania (krótszy)
    #            decryptedHexLen = self.primaryDataLength - len(decryptedData)
    #        else:
    #            # Standardowo do odszyfrowania stosujemy dlugosc taka sama jak do szyfrowania danych
    #            decryptedHexLen = self.doubleByteChunkPart
    #        # Zamiana deszyfrowanych danych na byty
    #        decryptedHex = descryptedInt.to_bytes(decryptedHexLen, 'big')
    #        # Łączenie wszystkich bytów po deszyfracji w jedną tablicę
    #        for byte in decryptedHex:
    #            decryptedData.append(byte)
    #    return decryptedData

    # Funkcja wywołująca algorytm RSA z podaną jako argument metodą
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
            #decrypted_data = self.decryptCrypto(new_png.reconstructed_idat_data, new_png.after_iend_data)
            self.createDescryptedPng(decrypted_data, new_png.bytesPerPixel, new_png.chunk_ihdr.width,new_png.chunk_ihdr.height, decrypted_file_path)
