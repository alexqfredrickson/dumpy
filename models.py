class Question:
    def __init__(self, text, postmortem=None, question_id=None, answers=None):
        self.text = str(text)
        self.question_id = int(question_id) if question_id else None
        self.postmortem = str(postmortem) if postmortem else None
        self.answers = answers if answers else []

    @property
    def correct_answers(self):
        return [a for a in self.answers if a.is_correct]

    @property
    def correct_answer_ids(self):
        return [a.answer_id for a in self.answers if a.is_correct]


class Answer:
    def __init__(self, text, letter=None, is_correct=False, answer_id=None, question_id=None):
        self.text = str(text)
        self.letter = str(letter) if letter else None
        self.is_correct = bool(is_correct) if is_correct else False
        self.answer_id = int(answer_id) if answer_id else None
        self.question_id = int(question_id) if question_id else None