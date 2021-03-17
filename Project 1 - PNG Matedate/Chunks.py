from lxml import etree
import io
import re

#Funkcja convert_byte - pozwala na konwertowania ciągu bitów na liczbę dziesiętną
# data - lista zawierajaca ciag bitow danych
# start - początkowy indeks bitu, który chcemy poddać konwersji
# stop - końcowy indeks bitu, który chcemy poddać konwersji
def convert_byte(data, start, end):
    return int.from_bytes(data[start:end+1],byteorder = "big", signed=False)

#Klasa CHUNK
#Atrybuty:
# length - 4 bajtowy int zawierający długość atrybutu data w bajtach
# chunk_type -  4 bajtowy typ chunku
# data - dane chunka o długości bajtowej równej length
# crc - 4 bajtowa suma kontrolna chunk_type oraz data zawiera długość atrybutu chunk_type oraz data w bajtach
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka w określony przez nas sposób)
class Chunk:
    def __init__(self, length, chunk_type, data, crc):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.crc = crc
    def __str__(self):
        info = "Chunk length: {0}\nChunk type: {1}\nChunk data: {2}\nChunk crc: {3}\n".format(self.length, self.chunk_type, self.data, self.crc)
        return info             

#Klasa IHDR - Chunk IHDR jest chunkiem obowiązkowym i musi pojawić się jako pierwszy i zawiera podstawowe informacje o obrazie
#Atrybuty:
# width  - 4 bajty zawierające informacje o długości obrazu
# length - 4 bajty zawierające informacj o wysokości obrazu
# bit_depth -  1 bajt zawierający informacje o głębi bitowej
# color_type - 1 bajt zawierający informacje o typie koloru
# compression_method - 1 bajt zawierający informacje o metodzie kompresji
# filter_method - 1 bajt zawierający informacje o metodzie filtrowania
# interlace_method - 1 bajt zawierający informacje oo metodzie z przeplotem
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka IHDR w określony przez nas sposób)
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

#Klasa PLTE - Chunk PLTE nie jest chunkiem obowiązkowym i posiada informacje o palecie kolorów
#Atrybuty:
# R - 1 bajt zawierające informacj o kolorze czerwonym (0 - czarny / 255 - czerwony)
# G - 1 bajt zawierające informacj o kolorze zielony (0 - czarny / 255 - zielony)
# B - 1 bajt zawierające informacj o kolorze niebieskim (0 - zielony / 255 - zielony)
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka PLTE w określony przez nas sposób)  
class PLTE(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
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

#Klasa IDAT - Chunk IDAT jest chunkiem obowiązkowym i zawiera obraz
#Atrybuty:
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka IDAT w określony przez nas sposób)
class IDAT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return super().__str__()

#Klasa IEND - Chunk IEND jest chunkiem obowiązkowym i musi pojawić się jako ostatni i nie zawiera informacji
#Atrybuty:
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka IEND w określony przez nas sposób)  
class IEND(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "================================================================================\n"

#Klasa tIME dziedzicząca po klasie CHUNK - zawiera datę ostatniej modyfikacji pliku
#Atrybuty:
# year - rok zapisany na 2 bajtach
# month - miesiąc zapisany na 1 bajcie
# day - dzień zapisany na 1 bajcie
# hour - godzina zapisana na 1 bajcie
# minute - minuta zapisana na 1 bajcie
# second - sekund zapisana na 1 bajcie
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka tIME w określony przez nas sposób)
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

#Klasa iTXt dziedzicząca po klasie CHUNK - zawiera informację tekstową w konkretnym języku
#Atrybuty:
# keyword - 1-79 bajtów słowo klucz określające jakie dane tekstowe otrzymujemy
# compression_flag - 1 bajt przyjmujący wartość 0 dla nieskompresowanego tekstu, a 1 dla skompresowanego tekstu
# compression_method - 1 bajt określający metodę kompresji
# language_tag - 0 lub więcej bajtów określających język przetłumaczonego słowa klucz w standarcie RFC-3066
# translated_keyword - 0 lub więcej bajtów zawierających przetłumaczone słowo klucz
# text - 0 lub więcej bajtów zawierających informację tekstową
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka iTXt w określony przez nas sposób)
class iTXt(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        all_data = self.data
        index = all_data.index(b'\x00')
        self.keyword = all_data[:index].decode('utf-8')
        self.compression_flag = all_data[index+1]
        self.itxt_compression_method = all_data[index+2]
        all_data = all_data[index+3:]
        index = all_data.index(b'\x00')
        self.language_tag = all_data[:index].decode('utf-8')
        all_data = all_data[index+1:]
        index = all_data.index(b'\x00')
        self.translated_keyword = all_data[:index].decode('utf-8')
        self.text = all_data[index+1:].decode('utf-8')
        if re.search("XML", self.keyword):
            with io.open("tmp.xml", "w", encoding="utf-8") as tmp:
                tmp.write(self.text)
                tmp.close()
            tree = etree.parse("tmp.xml")
            self.text = etree.tostring(tree, encoding="unicode", pretty_print=True)
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Keyword: {0}\nCompression flag: {1}\nCompression method: {2}\nLanguage tag: {3}\nTranslated keyword: {4}\nText: {5}\n".format(self.keyword, self.compression_flag, self.itxt_compression_method, self.language_tag, self.translated_keyword, self.text) + "================================================================================"

#Klasa tEXt dziedzicząca po klasie CHUNK - zawiera informację tekstową
#Atrybuty:
# keyword - 1-79 bajtów słowo klucz określające jakie dane tekstowe otrzymujemy
# text_string - 0 lub więcej bajtów zawierających informację tekstową
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka tEXt w określony przez nas sposób)
class tEXt(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        all_data = self.data
        index = all_data.index(b'\x00')
        self.keyword = all_data[:index].decode('utf-8')
        self.text_string = all_data[index+1:].decode('utf-8')
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Keyword: {0}\nText string: {1}\n".format(self.keyword, self.text_string) + "================================================================================"

#Klasa cHRM - Chunk cHRM jest chunkiem nieobowiązkowym 
#Atrybuty:
# white_point_x - 4 bajty zawierające informacje o współrzędnej x punktach bieli
# white_point_y - 4 bajty zawierające informacje o współrzędnej y punktach bieli
# red_x -  4 bajty zawierające informacje o współrzędnej x koloru czerwonego
# red_y - 4 bajty zawierające informacje o współrzędnej y koloru czerwonego
# green_x -  4 bajty zawierające informacje o współrzędnej x koloru zielonego
# green_y - 4 bajty zawierające informacje o współrzędnej y koloru zielonego
# blue_x -  4 bajty zawierające informacje o współrzędnej x koloru niebieskiego
# blue_y - 4 bajty zawierające informacje o współrzędnej y koloru niebieskiego
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka cHRM w określony przez nas sposób)
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

#Klasa sRGB dziedzicząca po klasie CHUNK  - zawiera informację o sposobie renderowania
#Atrybuty:
# rendering_intent - 1 bajt określający sposób renderowania za pomocą którego obraz powinien być wyświetlany
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka sRGB w określony przez nas sposób)
class sRGB(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        self.rendering_intent = self.data.decode('utf-8')
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Rendering data: {0}\n".format(self.rendering_intent) + "================================================================================\n"

#Klasa pHYs dziedzicząca po klasie CHUNK  - zawiera informację o proporcjonalności pixela
#Atrybuty:
# pixel_per_unit_x - 4 bajty unsigned int określające współczynnik x proporcjonalności pixela
# pixel_per_unit_y - 4 bajty unsigned int określające współczynnik y proporcjonalności pixela
# unit_specifier - 1 bajt określający jednostkę (0 - nie znana jednostka, 1 - metry)
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka pHYs w określony przez nas sposób)
class pHYs(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        self.pixel_per_unit_x = convert_byte(self.data, 0, 3)
        self.pixel_per_unit_y = convert_byte(self.data, 4, 7)
        self.unit_specifier = self.data[8]
    def __str__(self):
        return "================================================================================\n" + super().__str__() + "Pixel per unit, X axis: {0}\nPixel per unit, Y axis: {1}\nUnit specifier: {2}\n".format(self.pixel_per_unit_x, self.pixel_per_unit_y, self.unit_specifier) + "================================================================================\n"

#Klasa sPLT dziedzicząca po klasie CHUNK - zawiera informacje o sugerowanej palecie kolorów
#Atrybuty:
# palette_name - 1-79 bajtów określających nazwę palety
# sample_depth - 1 bajt określający głębię bitową (zawsze 8 lub 16)
# red - 1-2 bajty (w zależności od sample_depth) określające kolor czerwony
# green - 1-2 bajty (w zależności od sample_depth) określające kolor zielony
# green - 1-2 bajty (w zależności od sample_depth) określające kolor niebieski
# alpha - 1-2 bajty (w zależności od sample_depth) określające przeźroczystość
# frequency - tablica elementów 2-bajtowych zawierających częstotliwości proporcjonalne do frakcji pixeli obrazu dla których ta paleta jest najbardziej zbliżona do przestrzeni RGBA
#
#Metody:
# __init__ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# __str__ - przeciążenie wyświetlania (pozwala wyświetlić zawartość chunka sPLT w określony przez nas sposób)
class sPLT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)
        all_data = self.data
        index = all_data.index(b'\x00')
        self.palette_name = all_data[:index].decode('utf-8')
        all_data = all_data[index+1:]
        self.sample_depth = convert_byte(all_data, 0, 0)
        if self.sample_depth == 16:
            self.green = convert_byte(all_data, 1, 2)
            self.red = convert_byte(all_data, 3, 4)
            self.blue = convert_byte(all_data, 5, 6)
            self.alpha = convert_byte(all_data, 7, 8)
            index = 9
        else:
            self.green = convert_byte(all_data, 1, 1)
            self.red = convert_byte(all_data, 2, 2)
            self.blue = convert_byte(all_data, 3, 3)
            self.alpha = convert_byte(all_data, 4, 4)
            index = 5
        all_data = all_data[index:]
        self.frequency = []
        f = 0
        while f < len(all_data)/2:
            self.frequency.append(convert_byte(all_data, 2*f, 2*f+1))
            f+=1
    def __str__(self):
        return "================================================================================\n" + "Palette name: {0}\nSample_depth: {1}\nGreen: {2}\nRed: {3}\nBlue: {4}\nAplha: {5}\nFrequency: {6}\n".format(self.palette_name, self.sample_depth, self.green, self.red, self.blue, self.alpha, self.frequency) + "================================================================================\n"


