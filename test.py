class PP(object):
    def __init__(self,age, name, k):
        self.age = age
        self.name = name
        self.k = k
    def data(self):
        print("Balls" + str(self.age))

p = PP(19, "buy", 2)
p.data()