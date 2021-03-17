from ImagePng import ImagePng

def create_png():
        tmp2 = open('tmp2.png', 'wb')
        data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x08\x90\x00\x00\x0bh\x08\x06\x00\x00\x00\xa6C\xccs\x00\x00\x00\rsPLTha\x00\x08\x30\x10\x20\x02\x06\x00\x06\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        tmp2.write(data)
        tmp2.close()

create_png()

while True:
    nazwa_pliku = input("Podaj nazwę pliku:")
    img = ImagePng(nazwa_pliku)
    print(img.chunk_splt)
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