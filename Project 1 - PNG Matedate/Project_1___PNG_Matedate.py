from ImagePng import ImagePng

while True:
    nazwa_pliku = input("Podaj nazwę pliku:")
    img = ImagePng(nazwa_pliku)
    print(img.chunk_sPLT)
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





#try:
#    print(img.chunk_plte)
#except AttributeError:
#    print("Plik {0} nie ma chunka o nazwie PLTE".format(nazwa_pliku))


#img.show_picture_color()
#img.show_magnitude_spectrum()
#img.show_phase_spectrum()
#img.show_spectrum()


"""
#j=0
#for i in test.chunks_idat:
#    print(test.chunks_idat[j])
#    j+=1

#j=0
#for i in test.chunks_others:
#    print(test.chunks_others[j])
#    j+=1
"""