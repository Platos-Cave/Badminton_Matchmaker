from math import factorial as fact

def comb(n,r):
    return fact(n)/(fact(r)*fact(n-r))

print(comb(16,4) * comb(12,4) * comb(8 ,4))

