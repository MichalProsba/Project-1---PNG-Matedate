from ImagePng import ImagePng
from ParametersGeneratorRSA import ParametersGeneratorRSA
from RSA import RSA
import cv2


#Funkcja create_png - pozwala na tworzenie testowego pliku zawierającego chunk sPLT
def create_png():
        tmp2 = open("tmp2.png", 'wb')
        data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x08\x90\x00\x00\x0bh\x08\x06\x00\x00\x00\xa6C\xccs\x00\x00\x00\rsPLTha\x00\x08\x30\x10\x20\x02\x06\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        tmp2.write(data)
        tmp2.close()


#create_png();

line = "================================================================================"
while True:
    j = 1
    print(line)
    file_name = input("Podaj nazwę pliku:")
    img = ImagePng(file_name)
    print("Co chcesz zrobiź z podanym plikiem?")
    print(line +"\n1. Png Metadane")
    print(line +"\n2. Algory RSA")
    print(line +"\n3. Wyjście")
    option = int(input("Wybierz opcję:"))
    if option == 1:
        print(line)
        print("\nWybierz Chunka, którego informacje chcesz wyświetlić:")
        print(line)
        print(str(j) + ". IHDR")
        j += 1
        print(line)
        #print(img.chunks_idat[0])
    
        for i in img.chunks_typical:
            print(str(j) + ". " + str(i.chunk_type))    
            print(line)
            j += 1
        print(str(j) + ". IEND")
        print(line)
        j+=1
        print(str(j) + ". Zapisz plik (tylko z krytycznymi chunkami)")
        print(line)
        j+=1
        print(str(j) + ". Wyświetl obraz kolorowy")
        print(line)
        j+=1
        print(str(j) + ". Wyświetl obraz szary")
        print(line)
        j+=1
        print(str(j) + ". Wyświetl widmo obrazu")
        print(line)
        j+=1
        print(str(j) + ". Zakończ program")
        number = -1
        while number != j:
            print(line)
            number = int(input("Wybierz opcję:"))
            if number >= 1 and number <= j:
                if number == 1:
                    print(img.chunk_ihdr)
                elif number == (j-4):
                    img.save_only_critical()
                elif number == (j-5):
                    print(img.chunk_iend)
                elif number == (j-1):
                     img.show_spectrum()
                elif number == (j-2):
                     img.show_picture_gray()
                elif number == (j-3):
                    img.show_picture_color()
                elif number != j:
                    print(img.chunks_typical[number-2])
            else:
                print("Błąd: Nie ma takiego chunka! Spróbuj ponownie.")
    elif option == 2:
        keysize = int(input("Podaj dlugosc klucza: "))
        if keysize < 1024:
            break
        else:
            while True:
                algorithm = str(input("Podaj algorytm : "))
                if(algorithm == "ECB" or algorithm == "CBC" or algorithm == "CRYPTO"):
                    break
            img.process_idat_data()
            rsaTest = RSA(keysize)
            rsaTest.rsa(img, "encrypted.png", "decrypted.png", algorithm)
            img.show_picture_color()

            eimg = ImagePng("encrypted.png")
            eimg.show_picture_color()
            if algorithm == "ECB" or algorithm == "CBC":
                dimg = ImagePng("decrypted.png")
                dimg.show_picture_color()
    elif option == 3:
        exit()
    else:
        print("Nie ma takiej opcji. Spróbuj ponownie!")
