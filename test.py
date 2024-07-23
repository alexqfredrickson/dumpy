import unittest
from models import *
from dumpy import Dumpy
from utils import DumpyfileUtils


class DumpyTests(unittest.TestCase):

    @staticmethod
    @unittest.skip
    def test_example():

        dumpy = Dumpy()

        metadata = Metadata(
            description="An example .dumpy file.",
            shuffle_answers=True
        )

        questions = [
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

        DumpyfileUtils.create(metadata, questions, dumpy.dumpyfile_path)  # todo: test this

        dumpy.execute_braindump()
