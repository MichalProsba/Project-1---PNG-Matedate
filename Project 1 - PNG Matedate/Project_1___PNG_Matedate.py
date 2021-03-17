from ImagePng import ImagePng
import cv2
#Funkcja cls - pozwala na wyczyszczenie interpretera na każdym systemie operacyjnym
#def cls():
#    os.system('cls' if os.name=='nt' else 'clear')

#img_color = cv2.imread("mario.png", cv2.IMREAD_COLOR)
#cv2.imshow("Image color", img_color)

img = cv2.imread("dice.png", cv2.IMREAD_GRAYSCALE)
cv2.imshow("Image", img)








line = "================================================================================"
j = 1
print(line)
file_name = input("Podaj nazwę pliku:")
img = ImagePng(file_name)
print(line)
print("Wybierz Chunka, którego informacje chcesz wyświetlić:")
print(line)
print(str(j) + ". IHDR")
j += 1
print(line)
    
for i in img.chunks_typical:
    print(str(j) + ". " + str(i.chunk_type))    
    print(line)
    j += 1
print(str(j) + ". IEND")
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
        elif number == (j-1):
            print(img.chunk_iend)
        elif number == (j-2):
             img.show_picture_color()
        elif number == (j-3):
             img.show_picture_gray()
        elif number == (j-4):
             img.show_spectrum()
        elif number != j:
            print(img.chunks_typical[number-2])
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