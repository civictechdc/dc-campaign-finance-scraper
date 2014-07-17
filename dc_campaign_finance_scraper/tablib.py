import tablib


class Dataset(tablib.Dataset):

    def map(self, function):
        self.dict = list(map(function, self.dict))
        return self

    def filter(self, function):
        self.dict = list(filter(function, self.dict))
        return self
