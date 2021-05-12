import random, sys, os
import sympy
import copy

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
 
    def greatestCommonDivisor(self, a, b): 
        if b==0: 
            return a 
        else: 
            return self.greatestCommonDivisor(b,a%b) 
        
    def extendedEuclideanAlgorithm(self, a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = self.extendedEuclideanAlgorithm(b%a,a)
        return (g, x - (b//a) * y, y)

    def modularMultiplicativeInverse(self, a, m):
        g, x, y = self.extendedEuclideanAlgorithm(a, m)
        if g != 1:
            raise Exception('No modular inverse')
        return x%m

    def __str__(self):
        str1 = "===================================================================\n"
        return str1 + "Key size: " + str(self.keySize) + "\n" + str1 + "Prime size: " + str(self.primeNumberSize)  + "\n" + str1 + "p: " + str(self.p)  + "\n" + str1 + "q: " + str(self.q)  + "\n" + str1 + "n: " + str(self.n)  + "\n" + str1 + "o: " + str(self.o) + "\n" + str1 + "e: " + str(self.e)+ "\n" + str1 + "d: " + str(self.d) + "\n" + str1 + "Public Key: " + str(self.publicKey) + "\n" + str1 + "Private Key: " + str(self.privateKey)