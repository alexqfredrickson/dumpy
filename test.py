import os
import unittest
from dumpy import Dumpy
from models import Question, Answer
from utils import DumpyfileUtils


class DumpyTests(unittest.TestCase):

    context = "cloudprac"
    dumpy = Dumpy(context)

    @unittest.skip
    def test_create_context(self):
        questions = []

        questions.extend(
            [
                Question(
                    text="What year is it?",
                    answers=[
                        Answer(text=2015),
                        Answer(text=2016),
                        Answer(text=2017),
                        Answer(text=2018),
                        Answer(text=2019, is_correct=True)
                    ],
                    postmortem="It's 2019!"
                ),
                Question(
                    text="Which of these are numbers?",
                    answers=[
                        Answer(text="A"),
                        Answer(text="B"),
                        Answer(text=1, is_correct=True),
                        Answer(text=2, is_correct=True)
                    ],
                    postmortem="'A' and 'B' are letters, but 1 and 2 are numbers."
                )
            ]
        )

        DumpyfileUtils.create(questions, self.context)

        self.dumpy.create_context()

    def test_execute(self):
        # self.dumpy.create_context()
        self.dumpy.run()
