from enum import Enum, unique

@unique
class Ratio(Enum):
    HIGHER = "Higher"
    LOWER = "Lower"
    EQUAL = "Equal"
    ERROR = "Error"

class Token:
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.ratio = []
        self.counted_ratio = Ratio.ERROR

    def add_ratio(self, ratio):
        self.ratio.extend(ratio)

    def count_token(self):
        self.ratio.sort(key = lambda i: i[2])
        if len(self.ratio) > 1:
            self.first = float(self.ratio[0][0])
            self.last = float(self.ratio[-1][0])
            if self.first < self.last: self.counted_ratio = Ratio.HIGHER
            elif self.first > self.last: self.counted_ratio = Ratio.LOWER
            elif self.first == self.last: self.counted_ratio = Ratio.EQUAL
            else: self.counted_ratio = Ratio.ERROR
        else:
            self.counted_ratio = Ratio.ERROR

    def print_token(self):
        print("Index:", self.index)
        print("Ratio:", self.ratio)
        print("Token:", self.token)
        print("First:", self.first, "Last:", self.last)
        print("Counted ratio:", self.counted_ratio)

class Bookmaker:
    def __init__(self, id_bookmaker, status):
        self.id_bookmaker = id_bookmaker
        self.status = status
        self.ratious = []

    def add_tokens(self, array):
        for key in array:
            index = array.index(key)
            self.ratious.append(Token(index, key))

    def add_ratio(self, token, ratio):
        for key in self.ratious:
            if key.token == token:
                key.add_ratio(ratio)

    def count_ratio(self):
        for key in self.ratious:
            key.count_token()

    def get_id(self):
        return self.id_bookmaker

    def print_bookmaker(self):
        print('Bookmaker: ', self.id_bookmaker)
        print('Status: ', self.status)
        for key in self.ratious:
            key.print_token()

    def return_ratious(self):
        return self.ratious
