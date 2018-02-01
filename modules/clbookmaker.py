class Token:
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.ratio = []

    def add_ratio(self, ratio):
        self.ratio.extend(ratio)

    def print_token(self):
        print("Index:", self.index)
        print(self.ratio)

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

    def get_id(self):
        return self.id_bookmaker

    def print_bookmaker(self):
        print('Bookmaker: ', self.id_bookmaker)
        for key in self.ratious:
            key.print_token()

    def check_ratio_errors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher':
            return False
        else:
            return True

    def return_ratio(self, result):
        pass
