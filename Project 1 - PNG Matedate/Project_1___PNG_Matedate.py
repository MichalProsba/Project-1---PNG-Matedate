from ImagePng import ImagePng
import os

#Funkcja cls - pozwala na wyczyszczenie interpretera na każdym systemie operacyjnym
def cls():
    os.system('cls' if os.name=='nt' else 'clear')


line = "================================================================="


while True:
    j = 1
    print(line)
    file_name = input("Podaj nazwę pliku:")
    img = ImagePng(file_name)
    print(line)
    print("Wybierz Chunka, którego informacje chcesz wyświetlić:")
    print(line)
    print("1. IHDR")
    j += 1
    print(line)
    
    for i in img.chunks_typical:
        print(str(j) + ". " + str(i.chunk_type))    
        print(line)
        j += 1
    print(str(j) + ". IEND")
    j+=1
    print(str(j) + ". Zakończ program")
    j+=1
    number = -1
    while number != j:
        print(line)
        number = int(input("Wybierz opcję:"))
        cls()
        if number >= 1 and number <= j:
            if number == 1:
                print(img.chunk_ihdr)
            elif number == j:
                print(img.chunk_iend)
            elif number != j:
                print(img.chunks_typical[number-1])
        else:
            print("Błąd: Nie ma takiego chunka! Spróbuj ponownie.")
    
        





    

#print(img.chunk_splt)
#print(img.chunk_ihdr)
#print(img.chunk_plte)
#print(img.chunk_iend)
#print(img.chunk_time)
#print(img.chunk_itxt)
#print(img.chunk_text)
#print(img.chunk_chrm)
#print(img.chunk_srgb)
#print(img.chunk_phys)
#print(img.chunk_exif)