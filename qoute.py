class Qoute:
    def __init__(self, qoute, author):
        self.qoute = qoute
        self.author = author

    def __str__(self):
        return f'"{self.qoute}" - {self.author}'
