import os
import json
import sqlite3
import datetime
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

    @staticmethod
    def generate_dumpyfile_json(dumpyfile_description, shuffle_answers, questions):
        """
        Parses some dumpy questions into a dumpyfile-friendly JSON object.
        """

        j = {
            "metadata": {
                "description": dumpyfile_description,
                "shuffle_answers": shuffle_answers
            },
            "questions": []
        }

        for q in questions:
            j["questions"].append(
                {
                    "text": q.text,
                    "answers": [{"text": f"{a.text}", "is_correct": f"{a.is_correct}"} for a in q.answers],
                    "postmortem": q.postmortem
                }
            )

            return j

    @staticmethod
    def generate_dumpyfile_from_database(database_path, output_path):

        questions, answers, metadata, conn = None, None, None, None

        try:
            conn = sqlite3.connect(database_path)
            c = conn.cursor()

            c.execute("SELECT * FROM metadata")
            metadata = c.fetchone()

            c.execute("SELECT * FROM questions")
            questions = c.fetchall()

            c.execute("SELECT * FROM answers")
            answers = c.fetchall()

            conn.close()

        except sqlite3.Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

        description = metadata[0]
        shuffle_answers = metadata[1]
        shuffle_questions_by_weight = metadata[2]

        dumpyfile = {
            "metadata": {
                "description": description,
                "shuffle_answers": shuffle_answers,
                "shuffle_questions_by_weight": shuffle_questions_by_weight,
                # "database_created_time": datetime.datetime.strftime(datetime.datetime.now())
            },
            "questions": []
        }

        for q in questions:
            new_question = {
                    "text": q[1],
                    "portmortem": q[2],
                    "attempted_count": q[3],
                    "correct_count": q[4],
                    "enabled": q[5],
                    "answers": []
                }

            for a in answers:
                if a[1] == q[0]:
                    new_question["answers"].append(
                        {
                            "text": a[2],
                            "is_correct": True if a[3] == 1 else False
                        }
                    )

            dumpyfile["questions"].append(new_question)

        with open(output_path, "w+") as output_file:
            output_file.write(json.dumps(dumpyfile, indent=4))
