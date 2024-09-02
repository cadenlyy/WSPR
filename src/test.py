import math

def SD(s, m, n):#sum of x^2, mean, number of values
    try:
        return math.sqrt(s/n-m**2)
    except ValueError:
        print("error")
        return "error"
    
def test(s, m , n):
    return s/n-m**2
    
x = [1473642704995, -6158, -19, 3536844986946222499181, 61778, 75]
y = 623
    
print(test(3485001982832301863885,1452042079147/605,605))