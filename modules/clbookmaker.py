class Bookmaker:
    def __init__(self, name_bookmaker, ratio_1, ratio_2):
        self.id_bookmaker = id_bookmaker
        self.ratio_1 = ratio_1
        self.ratio_2 = ratio_2

    def print_bookmaker(self):
        print('Bookmaker: ', self.name_bookmaker)
        print('1: ', self.ratio_1)
        print('2: ', self.ratio_2)

    def check_ratio_errors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher':
            return False
        else:
            return True

    def return_ratio(self, result):
        if result == '1':
            if self.check_ratio_errors() and (self.ratio_1 == 'Higher' or self.ratio_1 == 'Lower'):
                return self.ratio_1
            else:
                return
        elif result == '2':
            if self.check_ratio_errors() and (self.ratio_2 == 'Higher' or self.ratio_2 == 'Lower'):
                return self.ratio_2
            else:
                return
        else:
            print('Error with result!')
