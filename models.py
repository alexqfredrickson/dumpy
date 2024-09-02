from random import shuffle

"""
Objects parsed out from .dumpy files.
"""


class Metadata:
    def __init__(self, description, shuffle_answers=False, shuffle_questions_by_weight=False):
        self.description = description
        self.shuffle_answers = shuffle_answers
        self.shuffle_questions_by_weight = shuffle_questions_by_weight


class Question:
    def __init__(self, text, answers, postmortem, attempted_count, correct_count, enabled, question_id=None):
        self.question_id = int(question_id) if question_id else None
        self.text = str(text)
        self.answers = answers
        self.postmortem = str(postmortem) if postmortem else None
        self.attempted_count = attempted_count
        self.correct_count = correct_count
        self.enabled = enabled

    @property
    def correct_answers(self):
        return [a for a in self.answers if a.is_correct]

    @property
    def correct_answer_ids(self):
        return [a.answer_id for a in self.answers if a.is_correct]

    def assign_letters_to_answers(self):
        for i in range(len(self.answers)):
            self.answers[i].letter = chr(i + 65)

    def shuffle_answers(self):
        shuffle(self.answers)


class Answer:
    def __init__(self, text, letter=None, is_correct=False, answer_id=None, question_id=None):
        self.text = str(text)
        self.letter = str(letter) if letter else None

        if is_correct is not None:
            if is_correct is True or is_correct == "True":
                self.is_correct = True
            else:
                self.is_correct = False

        self.answer_id = int(answer_id) if answer_id else None
        self.question_id = int(question_id) if question_id else None


class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
