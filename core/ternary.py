# Special functions for ternary notation operations.

BASE = 3
FIELD_WIDTH = 4
MASK_WIDTH = FIELD_WIDTH**2
POS_COUNT = BASE**MASK_WIDTH


# very very bad solution (I just want to sleep)
def set_field_width(fw):
    global FIELD_WIDTH, MASK_WIDTH, POS_COUNT
    FIELD_WIDTH = fw
    MASK_WIDTH = FIELD_WIDTH**2
    POS_COUNT = BASE**MASK_WIDTH

DIGITS_MAP = {
    '0' : ' ',
    '1' : 'X',
    '2' : 'O',
}

E_IND = 0 # linear index of empty cell
X_IND = 1 # linear index of X cell
O_IND = 2 # linear index of O cell



def change_representation(mask, to_canonical=True):
    global DIGITS_MAP

    new_mask = mask

    for csymbol in DIGITS_MAP:
        tsymbol = DIGITS_MAP[csymbol]
        a, b = (tsymbol, csymbol) if to_canonical else (csymbol, tsymbol)
        new_mask = new_mask.replace(a, b)

    return new_mask

def canonical_representation(mask):
    return change_representation(mask, to_canonical = True)

def tttoe_representation(mask):
    return change_representation(mask, to_canonical = False)    

def mask_to_decimal(mask):
    canonical_mask = canonical_representation(mask)
    return int(canonical_mask, 3)

def decimal_to_mask(decimal):
    global BASE, MASK_WIDTH, DIGITS_MAP
    symbols = "012"
    
    ternary_mask = ""
    
    while decimal != 0 :
        ternary_mask = symbols[decimal % BASE] + ternary_mask
        decimal /= BASE
    prefix = '0' * (MASK_WIDTH - len(ternary_mask))
    ternary_mask = prefix + ternary_mask
    return ternary_mask


def main():
    global DIGITS_MAP
    from random import randint
    trep_mask = ''
    for i in xrange(MASK_WIDTH):
        trep_mask += DIGITS_MAP[str(randint(0, 2))]

    print 'tic-tac-toe representation :', trep_mask
    print 'canonical representation :', canonical_representation(trep_mask)
    print 'idempotency :', tttoe_representation(canonical_representation(trep_mask)) == trep_mask

    print 'decimal from ttoe representation :', mask_to_decimal(trep_mask)
    print 'decimal from canonical representation :', mask_to_decimal(canonical_representation(trep_mask))
    print 'idempotency :', canonical_representation(trep_mask) == decimal_to_mask(mask_to_decimal(trep_mask))

if __name__=='__main__':
    main()