import os
import json
import sqlite3
import textwrap
import string
from random import shuffle
from models import Question, Answer


class Dumpy:
    def __init__(self, context, questions=None):
        self.context = context
        self.questions = questions if questions else []

        self.sqlite_context_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "contexts",
            self.context.lower() + ".db"
        )

    def create_context(self, dumpyfile_path):
        """
        Creates a local Dumpy database and imports questions/answers from the specified Dumpyfile path.

        :param dumpyfile_path: The path to the Dumpyfile (this project has a default repository located at /dumpy/dumpyfiles/).
        :type dumpyfile_path: str
        """

        self.create_database_context()
        self.import_dumpyfile(dumpyfile_path)

    def load(self):
        """

        """

        questions, answers, conn = None, None, None

        try:
            conn = sqlite3.connect(self.sqlite_context_path)
            c = conn.cursor()

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

        self.questions.extend(
            [
                Question(
                    question_id=q[0],
                    text=q[1],
                    postmortem=q[2]
                )
                for q in questions
            ]
        )

        answers = [
            Answer(
                answer_id=a[0],
                question_id=a[1],
                text=a[2],
                letter=a[3],
                is_correct=True if a[4] == 1 else False
            )
            for a in answers
        ]

        for q in self.questions:
            for a in answers:
                if a.question_id != q.question_id:
                    continue

                q.answers.append(a)

    def execute_braindump(self):
        shuffle(self.questions)

        print("")

        total_correct_count = 0
        total_displayed_count = 0

        for q in self.questions:
            total_displayed_count += 1
            valid_answer_choices = [a.letter.lower() for a in q.answers]

            print(
                "{}\n".format(
                    textwrap.fill(q.text, 100)
                )
            )

            for a in q.answers:
                print("  {}. {}".format(a.letter, textwrap.fill(a.text, 80)))

            print("")

            answer = None

            while answer is None:
                answer = input()

                all_inputs_are_valid = set(list(answer.lower())).issubset(valid_answer_choices)

                if all_inputs_are_valid:
                    chosen_answer_ids = [a.answer_id for a in q.answers if a.letter.lower() in list(answer.lower())]

                    if sorted(chosen_answer_ids) == sorted(q.correct_answer_ids):
                        print(
                            "CORRECT: {}\n{}".format(
                                " and ".join(a.letter for a in q.correct_answers),
                                "\n{}\n".format(q.postmortem) if q.postmortem else ""
                            )
                        )
                        total_correct_count += 1
                    else:
                        if len(q.correct_answer_ids) == 1:
                            print(
                                "FALSE: The correct answer is {}.\n{}".format(
                                    q.correct_answers[0].letter,
                                    "\n{}\n".format(q.postmortem) if q.postmortem else ""
                                )
                            )
                        else:
                            print(
                                "FALSE: The correct answers are {}.\n\n{}\n".format(
                                    " and ".join(a.letter for a in q.correct_answers),
                                    textwrap.fill(q.postmortem, 100) if q.postmortem else ""
                                )
                            )
                else:
                    print("ERROR: please provide a letter (eg. 'C').".format(answer))
                    answer = None

            percent = (total_correct_count / total_displayed_count) * 100

            grade = "F"

            if percent >= 90:
                grade = "A"
            elif percent >= 80:
                grade = "B"
            elif percent >= 70:
                grade = "C"
            elif percent >= 60:
                grade = "D"

            print("CURRENT GRADE: " + grade + " ({}/{} correct)".format(total_correct_count, total_displayed_count))
            print("Press any key to continue.")
            input()
            os.system('cls' if os.name == 'nt' else 'clear')

    def delete_context(self):
        pass

    def list_contexts(self):
        pass

    def run(self):

        self.load()
        self.execute_braindump()

    def create_database_context(self):
        """
        Creates the basic schema

        """

        conn = None

        try:
            conn = sqlite3.connect(self.sqlite_context_path)
            c = conn.cursor()

            c.execute(
                "CREATE TABLE questions ("
                "`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
                "`text`	TEXT NOT NULL,"
                "`postmortem` TEXT"
                ")"
            )

            c.execute(
                "CREATE TABLE answers ("
                " `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
                " `question_id`	INTEGER NOT NULL,"
                " `text`	TEXT NOT NULL,"
                " `letter`	TEXT NOT NULL,"
                " `is_correct`	INTEGER NOT NULL DEFAULT 0"
                ")"
            )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

    def import_dumpyfile(self, dumpyfile_path):
        """

        :param dumpyfile_path:
        :return:
        """

        self.parse_dumpyfile(dumpyfile_path)

        conn = None

        alphabet_dictionary = dict(enumerate(string.ascii_lowercase, 1))

        try:
            conn = sqlite3.connect(self.sqlite_context_path)
            c = conn.cursor()

            for q in self.questions:
                c.execute(
                    "INSERT INTO questions VALUES ({},'{}'{})".format(
                        q.question_id,
                        q.text.replace("'", "''"),
                        ",'{}'".format(q.postmortem.replace("'", "''")) if q.postmortem else ""
                    )
                )

                conn.commit()

                for i in range(len(q.answers)):
                    c.execute(
                        "INSERT INTO answers (question_id, text, letter, is_correct) VALUES ({},'{}','{}',{})".format(
                            q.answers[i].question_id,
                            q.answers[i].text.replace("'", "''"),
                            alphabet_dictionary[i+1].upper(),
                            1 if q.answers[i].is_correct else 0
                        )
                    )

                    conn.commit()

            conn.close()

        except sqlite3.Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

    def parse_dumpyfile(self, dumpyfile_path):

        with open(dumpyfile_path, 'r') as dumpyfile:
            contents = json.loads(dumpyfile.read())

            question_count = len(contents)

            for i in range(question_count):

                question = Question(
                    question_id=i + 1,
                    text=contents[i]["text"],
                    postmortem=contents[i]["postmortem"] if "postmortem" in contents[i] else None,
                    answers=[]
                )

                answer_count = len(contents[i]["answers"])

                for j in range(answer_count):
                    answer = contents[i]["answers"][j]

                    question.answers.append(
                        Answer(
                            answer_id=j + 1,
                            question_id=i + 1,
                            text=answer["text"],
                            is_correct=answer["is_correct"] if "is_correct" in answer else None
                        )
                    )

                self.questions.append(question)

