import os
import json
from models import Question


class DumpyfileUtils:
    def __init__(self):
        pass

    @staticmethod
    def create(metadata, questions, context):
        """
        Creates a .dumpy file in the local ~/dumpy/dumpyfiles/ directory based on the provided Questions.

        :param questions: A list of questions with accompanying answers.
        :type questions: list of Question
        :param metadata: The metadata of the .dumpy file.
        :type metadata: Metadata
        :param context: The name of the resulting dumpyfile (e.g. if context=test --> test.dumpy will be created).
        :type context: str
        """

        dumpyfile_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dumpyfiles",
            context.lower() + ".dumpy"
        )

        # serialize questions object to json
        def obj_dict(obj):
            return obj.__dict__

        for q in questions:
            del q.question_id

            for a in q.answers:
                del a.answer_id
                del a.letter
                del a.question_id

        json_contents = {
            "metadata": metadata,
            "questions": questions
        }

        json_string = json.dumps(json_contents, default=obj_dict, indent=4)

        with open(dumpyfile_path, 'w') as dumpyfile:
            dumpyfile.write(json_string)

