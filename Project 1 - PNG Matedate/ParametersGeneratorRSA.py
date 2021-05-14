import random, sys, os
import sympy
import copy

#Klasa ParametersGeneratorRSA
#Atrybuty:
# keySize - rozmiar klucza w bitach
# primeNumberSize - rozmiar liczby pierwszej
# p - pierwsza liczba pierwsza
# q - druga liczba 
# o - iloczyn (p-1)(q-1)
# n - iloczyn pq (część klucza publicznego i prywatnego)
# e - liczba wzglednie pierwsza do liczby o (część klucza publicznego)
# d - liczba obliczona jako e^(-1)(mod(o)) (część klucza prywatnego)
# publicKey - klucz publiczny
# privateKey - klucz prywatny

#Metody:
# _init_ - konstruktor parametryczny do którego wysyłamy dane do powyższych atrybutów
# _str_ - przeciążenie wyświetlania (pozwala wyświetlić zawartość obiektu typu ParametersGeneratorRSA w określony przez nas sposób)
# generateLargePrimeNumber - generuje dużą liczbę pierwszą
# generateAll - generuje klucze potrezbne do szyfrowania algorytmem RSA
# greatestCommonDivisor - generuje największy wspólny dzielnik dwóch podanych liczb
# extendedEuclideanAlgorithm - generuje największy wspólny dzielnik dwóch podanych liczb oraz dwie liczby spełniające tożsamość Bézouta
# modularMultiplicativeInverse - funkcja obliczająca odwrotność modulo dla podanej pary liczb

class ParametersGeneratorRSA:
    def __init__(self, keySize):
        self.keySize=keySize
        self.primeNumberSize = keySize/2
        self.p=0
        self.q=0
        self.o=0
        self.n=0
        self.e=0
        self.d=0
        self.publicKey=0
        self.privateKey=0
        self.generateAll()
        
    def generateLargePrimeNumber(self):
        while True:
            number = random.randrange(2**(self.primeNumberSize-1), 2**(self.primeNumberSize))
            if sympy.isprime(number):
                return number

    def generateAll(self):
        self.p = self.generateLargePrimeNumber()
        self.q = self.generateLargePrimeNumber()
        while self.p == self.q or ((self.p-1)*(self.q-1)).bit_length() != self.keySize:
            self.p = self.generateLargePrimeNumber()
            self.q = self.generateLargePrimeNumber()
        self.n = self.p * self.q;    
        self.o = (self.p-1)*(self.q-1)

        while True:
            self.e = random.randrange(2 ** (self.keySize - 1), 2 ** (self.keySize))
            if self.greatestCommonDivisor(self.e, self.o) == 1 and self.e < self.o:
                break

        self.d = self.modularMultiplicativeInverse(self.e, self.o)

        self.publicKey=(self.e, self.n)
        self.privateKey=(self.d, self.n)

        if self.e.bit_length() == self.keySize and self.d.bit_length() == self.keySize:
           return (copy.deepcopy(self.publicKey), copy.deepcopy(self.privateKey))
 
    def greatestCommonDivisor(self, t, s): 
        if s==0: 
            return t 
        else: 
            return self.greatestCommonDivisor(s,t%s) 
        
    def extendedEuclideanAlgorithm(self, t, s):
        if t == 0:
            return (s, 0, 1)
        g, y, x = self.extendedEuclideanAlgorithm(s%t,t)
        return (g, x - (s//t) * y, y)

    def modularMultiplicativeInverse(self, a, m):
        g, x, y = self.extendedEuclideanAlgorithm(a, m)
        if g != 1:
            raise Exception('No modular inverse')
        return x%m

    def __str__(self):
        str1 = "===================================================================\n"
        return str1 + "Key size: " + str(self.keySize) + "\n" + str1 + "Prime size: " + str(self.primeNumberSize)  + "\n" + str1 + "p: " + str(self.p)  + "\n" + str1 + "q: " + str(self.q)  + "\n" + str1 + "n: " + str(self.n)  + "\n" + str1 + "o: " + str(self.o) + "\n" + str1 + "e: " + str(self.e)+ "\n" + str1 + "d: " + str(self.d) + "\n" + str1 + "Public Key: " + str(self.publicKey) + "\n" + str1 + "Private Key: " + str(self.privateKey)