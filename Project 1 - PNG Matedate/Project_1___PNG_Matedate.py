from ImagePng import ImagePng
img = ImagePng("dead_space.png")
#print(img.chunk_ihdr)
#img.show_picture()
#print(img.chunk_plte)
#print(img.chunk_iend)
#print(img.chunk_time)
print(img.chunk_itxt)
print(img.chunk_text)

#img.show_picture_color()
#img.show_magnitude_spectrum()
#img.show_phase_spectrum()
img.show_spectrum()


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