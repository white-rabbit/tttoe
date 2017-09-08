#
class BinaryFilterException(Exception):
    def __init__(self, message):
        super(BinaryFilterException, self).__init__(message)

class BinaryFilter(object):
    def __init__(self, initilizer):
        if isinstance(initilizer, BinaryFilter):
            self.values_count = initilizer.values_count
            self.bitmask = initilizer.bitmask
        elif isinstance(initilizer, str):
            self.values_count = len(initilizer)
            self.bitmask = int(initilizer, 2)
        elif isinstance(initilizer, int):
            self.values_count = initilizer
            self.bitmask = 2 ** self.values_count - 1
        else:
            BinaryFilterException('Unknown initializer type: %s' % type(initilizer))

    @staticmethod
    def bit_up(number, index):
        return  number | (1 << index)
    @staticmethod
    def bit_down(number, index):
        return  number & (~(1 << index))
    @staticmethod
    def __is_up(number, index):
        return  (number & (1 << index)) == (1 << index)

    def drop_index(self, index):
        """
        Drop some value from the list by index.

        Parameters
        ----------
        index  (int):   drop index
        
        """
        self.bitmask = BinaryFilter.bit_down(self.bitmask, index)

    def return_index(self, index):
        """
        Return some index to the list by index.

        Parameters
        ----------
        index  (int):   index for returning
        
        """
        self.bitmask = BinaryFilter.bit_up(self.bitmask, index)


    def indicies(self):
        """
        Returns
        ----------
        (list):   the list of the allowed indicies
        
        """
        is_allowed = lambda i : BinaryFilter.__is_up(self.bitmask, i)
        return filter(is_allowed, range(self.values_count))

    def empty(self):
        return self.bitmask == 0


        
def main():
    bf = BinaryFilter(10)
    print bf.indicies()
    bf.drop_index(2)
    print bf.indicies()

    
    
if __name__=='__main__':
    main()
