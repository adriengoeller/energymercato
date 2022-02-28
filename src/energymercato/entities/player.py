

class Player():
    def __init__(self):
        self.plant_list = []
        score = [0]

    def get_prod(self):
        if self.plant_list:
            print("please fill plant_list")
        else:
            return sum(c.p for c in self.plant_list)

    


