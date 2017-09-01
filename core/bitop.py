# Basic bitwise operations

def bit_up(number, index):
    return  number | (1 << index)

def bit_down(number, index):
    return  number & (~(1 << index))

def is_up(number, index):
    return  (number & (1 << index)) == (1 << index)
    
def main():
    from random import randint
    a = randint(0, 2**32 - 1)
    binary_a = ""
    for i in xrange(32):
        binary_a = ('1' if is_up(a, i) else '0') + binary_a


    print 'random number : ', a
    print 'binary representation : ', binary_a
    print 'idempotency : ', int(binary_a, 2) == a
    
    
if __name__=='__main__':
    main()
