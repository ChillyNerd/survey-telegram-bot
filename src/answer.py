from typing import List


class Answer:
    def __init__(self, username: str, *args):
        self.username = username
        self.answers: List[str] = list(args)

    def to_dict(self):
        return {"username": self.username, **{str(index + 1): answer for index, answer in enumerate(self.answers)}}

    def to_json(self):
        return {"username": self.username, 'answers': self.answers}
