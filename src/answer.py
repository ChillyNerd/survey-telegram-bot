class Answer:
    def __init__(self, username: str, first_answer: str, second_answer: str):
        self.username = username
        self.first_answer = first_answer
        self.second_answer = second_answer

    def to_dict(self):
        return {"username": self.username, "first_answer": self.first_answer, "second_answer": self.second_answer}
