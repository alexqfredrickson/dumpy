import os
import json
import sqlite3
import textwrap
from random import shuffle
from models import Question, Answer


class Dumpy:
    def __init__(self, context, questions=None):
        self.context = context
        self.questions = questions if questions else []

        self.dumpyfile_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dumpyfiles",
            self.context.lower() + ".dumpy"
        )

        self.sqlite_context_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "contexts",
            self.context.lower() + ".db"
        )

        self.shuffle_answers = True

    def load_questions(self):
        """
        Validates the existence of the local dumpy database and loads all questions/answers from it.
        """

        self.questions = []

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

        answers = [
            Answer(
                answer_id=a[0],
                question_id=a[1],
                text=a[2],
                is_correct=True if a[3] == 1 else False
            )
            for a in answers
        ]

        self.questions.extend(
            [
                Question(
                    question_id=q[0],
                    text=q[1],
                    postmortem=q[2],
                    answers=[a for a in answers if int(a.question_id) == q[0]]
                )
                for q in questions
            ]
        )

        if self.shuffle_answers:
            shuffle(self.questions)

        for q in self.questions:
            q.assign_letters_to_answers()

    def execute_braindump(self):
        """
        Validates the local database, loads questions it, and begins the braindump.
        """

        self.validate_database()
        self.load_questions()
        self.begin_braindump()

    def validate_database(self):

        # check if database exists
        if not os.path.exists(self.sqlite_context_path):
            print(
                "INFO: A database with the specified context ({}) does not yet exist.".format(self.sqlite_context_path)
            )

            print("INFO: Attempting to create one from {}...".format(self.dumpyfile_path))

            self.create_context()

            if not os.path.exists(self.sqlite_context_path):
                print("ERROR: the dumpy database has not been created.")
                exit(1)

        # check if questions table exists
        questions_table_exists = False

        try:
            conn = sqlite3.connect(self.sqlite_context_path)
            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE name='questions'")
            questions_table_exists = c.fetchall()

            conn.close()

        except Exception as e:
            print(e)
            exit(1)

        if not questions_table_exists:
            print("ERROR: No questions table was found. Deleting local database...")

        # check to see if it actually has questions
        question_count = 0

        try:
            conn = sqlite3.connect(self.sqlite_context_path)
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM questions")
            question_count = c.fetchall()

            conn.close()

        except Exception as e:
            print(e)
            exit(1)

        if len(question_count) == 0:
            self.delete_context("No questions were found.")

    def begin_braindump(self):
        """
        Starts the test.
        """

        total_correct_count = 0
        total_displayed_count = 0

        for q in self.questions:
            os.system('cls' if os.name == 'nt' else 'clear')

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
                        if len(q.correct_answer_ids) != len(chosen_answer_ids):

                            print(
                                "ERROR: the provided answer ('{}') is invalid.\n"
                                "Please provide the correct amount of answer(s); eg. 'C', 'DA'.".format(answer.lower())
                            )

                            answer = None
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
                    print(
                        "ERROR: the provided answer ('{}') is invalid.\n"
                        "Please provide answers from the above list; eg. 'C', 'DA'.".format(answer.lower())
                    )
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
            print("Press the enter key to continue.")
            input()

    def create_context(self):
        """
        If the .dumpy file is valid, creates a local Dumpy database and inserts questions/answers into it.
        """

        self.validate_dumpyfile()
        self.create_database_context()
        self.import_dumpyfile()

    def validate_dumpyfile(self):
        """
        Ensures the .dumpy file is properly formatted.
        """

        try:
            self.parse_dumpyfile(self.dumpyfile_path)
        except json.decoder.JSONDecodeError as e:
            print("ERROR: the .dumpy file has an invalid format.")
            print(e)
            exit(1)

        return True

    def create_database_context(self):
        """
        Creates a local, empty Dumpy database under '[project root]/contexts/'.
        """

        if not os.path.exists(os.path.dirname(self.sqlite_context_path)):
            os.mkdir(os.path.dirname(self.sqlite_context_path))

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

    def import_dumpyfile(self):
        """
        Parses a .dumpy file and inserts this data into the local Dumpy database.
        """

        conn = None

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
                        "INSERT INTO answers (question_id, text, is_correct) VALUES ({},'{}',{})".format(
                            q.answers[i].question_id,
                            q.answers[i].text.replace("'", "''"),
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
        """
        Proves the existence of the local .dumpy file and inserts it into the local dumpy database.
        """

        if not os.path.exists(dumpyfile_path):
            print(
                "ERROR: the dumpyfile ({}) was not found. "
                "Its default location is '[project root]/dumpyfiles/'.".format(dumpyfile_path)
            )
            exit(1)

        with open(dumpyfile_path, 'r') as dumpyfile:
            contents = json.loads(dumpyfile.read())

            question_count = len(contents["questions"])

            for i in range(question_count):

                question = None

                this_question = contents["questions"][i]

                try:
                    question = Question(
                        question_id=i + 1,
                        text=this_question["text"],
                        postmortem=this_question["postmortem"] if "postmortem" in this_question else None,
                        answers=[]
                    )
                except Exception as e:
                    print(e)

                answer_count = len(this_question["answers"])

                for j in range(answer_count):
                    answer = this_question["answers"][j]

                    question.answers.append(
                        Answer(
                            answer_id=j + 1,
                            question_id=i + 1,
                            text=answer["text"],
                            is_correct=answer["is_correct"] if "is_correct" in answer else None
                        )
                    )

                self.questions.append(question)

    def delete_context(self, message):
        print("ERROR: {} Deleting local database...".format(message))
        os.remove(self.sqlite_context_path)
        exit(1)

    def list_contexts(self):
        pass
