def add(a:int,b:int)->int:
    return a+b

def sub(a:int,b:int)->int:
    return a-b      

def mul(a:int,b:int)->int:
    return a*b  

def div(a:int,b:int)->float:
    if b==0:
        raise ValueError("Division by zero is not allowed.")
    return a/b

def mod(a:int,b:int)->int:
    return a%b

def power(a:int,b:int)->int:
    return a**b

def floor_div(a:int,b:int)->int:
    if b==0:
        raise ValueError("Division by zero is not allowed.")
    return a//b

def sqrt(a:int)->float:
    if a<0:
        raise ValueError("Square root of negative number is not allowed.")
    return a**0.5

def cube(a:int)->int:
    return a**3 

def factorial(n:int)->int:
    if n<0:
        raise ValueError("Factorial of negative number is not defined.")
    if n==0 or n==1:
        return 1
    result=1
    for i in range(2,n+1):
        result*=i
    return result

def gcd(a:int,b:int)->int:
    while b:
        a,b=b,a%b
    return a

def lcm(a:int,b:int)->int:
    if a==0 or b==0:
        return 0
    return abs(a*b)//gcd(a,b)

def is_prime(n:int)->bool:
    if n<=1:
        return False
    for i in range(2,int(n**0.5)+1):
        if n%i==0:
            return False
    return True