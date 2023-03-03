
def generator_test():
    yield 1
    yield 2
    yield 3

myGen = generator_test()

print("generator_test: " + str(next(myGen)))
print("generator_test: " + str(next(myGen)))
print("generator_test: " + str(next(myGen)))
#print("generator_test: " + str(next(myGen)))