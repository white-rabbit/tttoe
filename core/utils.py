# some special functions for debugging
import sys

def die(message):
    print(message)
    sys.exit()


# Kludge for enums in Python2
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Special memoization by unque id class method depended by first argument
def memoized_by_uid(some_class_method):
    memory = {}
    def wrapped(self, *args, **kwargs):
        uid = self.unique_id(args[0])
        if uid in memory:
            return memory[uid]
        else:
            value = some_class_method(self, *args, **kwargs)
            memory[uid] = value
            return value
    return wrapped