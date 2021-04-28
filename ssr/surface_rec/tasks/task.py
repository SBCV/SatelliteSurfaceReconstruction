import pprint


class Task:
    def __str__(self):
        return f"\n {self.__class__.__name__}: \n {pprint.pformat(self.__dict__)}  \n"

    def __repr__(self):
        return self.__str__()
