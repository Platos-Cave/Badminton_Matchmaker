from math import factorial as fact

def comb(n,r):
    return fact(n)/(fact(r)*fact(n-r))

print(comb(18,4))

