"""
Objects parsed out from .dumpy files.
"""


class Metadata:
    def __init__(self, description, shuffle_answers=True):
        self.description = description
        self.shuffle_answers = shuffle_answers


class Question:
    def __init__(self, text, answers, postmortem=None, question_id=None):
        self.text = str(text)
        self.answers = answers
        self.question_id = int(question_id) if question_id else None
        self.postmortem = str(postmortem) if postmortem else None

    @property
    def correct_answers(self):
        return [a for a in self.answers if a.is_correct]

    @property
    def correct_answer_ids(self):
        return [a.answer_id for a in self.answers if a.is_correct]

    def assign_letters_to_answers(self):
        for i in range(len(self.answers)):
            self.answers[i].letter = chr(i + 65)


class Answer:
    def __init__(self, text, letter=None, is_correct=False, answer_id=None, question_id=None):
        self.text = str(text)
        self.letter = str(letter) if letter else None
        self.is_correct = bool(is_correct) if is_correct else False
        self.answer_id = int(answer_id) if answer_id else None
        self.question_id = int(question_id) if question_id else None
