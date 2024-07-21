import os
import json
import sqlite3
import time
from random import shuffle
from models import Question, Answer


class Dumpy:
    def __init__(self, questions=None):
        self.questions = questions if questions else []

        if "DUMPY_FILEPATH" not in os.environ:
            print(f"ERROR: The environment variable `DUMPY_FILEPATH` was not set.")
            exit(1)
        else:
            self.dumpyfile_path = os.environ["DUMPY_FILEPATH"]

        if not os.path.exists(self.dumpyfile_path):
            print(f"ERROR: {self.dumpyfile_path} was not found.")
            exit(1)

        self.dumpyfile_name = os.path.basename(self.dumpyfile_path)

        self.sqlite_context_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "contexts",
            self.dumpyfile_name + ".db"
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

        self.display_opening_credits()
        self.validate_database()
        self.load_questions()
        self.begin_braindump()

    @staticmethod
    def display_opening_credits():
        print("THANK YOU FOR USING ....\n", end='', flush=True)
        print("     _                             \n", end='', flush=True)
        print("  __| |_   _ _ __ ___  _ __  _   _ \n", end='', flush=True)
        print(" / _` | | | | '_ ` _ \\| '_ \\| | | |\n", end='', flush=True)
        print("| (_| | |_| | | | | | | |_) | |_| |\n", end='', flush=True)
        print(" \\__,_|\\__,_|_| |_| |_| .__/ \\__, |\n", end='', flush=True)
        print("                      |_|    |___/\n\n", end='', flush=True)

        time.sleep(1.5)

    def validate_database(self):

        # check if database exists
        if not os.path.exists(self.sqlite_context_path):
            print(
                f"INFO: A database with the specified context ({self.sqlite_context_path}) does not yet exist."
            )

            print(f"INFO: Attempting to create one from {self.dumpyfile_path}...")

            self.create_context()

            if not os.path.exists(self.sqlite_context_path):
                print("ERROR: the dumpy database has not been created.")
                exit(1)

        try:  # check if questions table exists
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

        try:  # check to see if it actually has questions
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

            print(f"{q.text}\n")

            for a in q.answers:
                print(f"  {a.letter}. {a.text}")

            print("")

            answer = None

            while answer is None:
                answer = input()

                all_inputs_are_valid = set(list(answer.lower())).issubset(valid_answer_choices)

                if all_inputs_are_valid:
                    chosen_answer_ids = [a.answer_id for a in q.answers if a.letter.lower() in list(answer.lower())]
                    correct_answers = " and ".join(a.letter for a in q.correct_answers)
                    postmortem = f"\n{q.postmortem}\n" if q.postmortem else ""

                    if sorted(chosen_answer_ids) == sorted(q.correct_answer_ids):
                        print(f"CORRECT: {correct_answers}\n{postmortem}")
                        total_correct_count += 1

                    else:
                        if len(q.correct_answer_ids) != len(chosen_answer_ids):
                            print(f"ERROR: please provide exactly {len(chosen_answer_ids)} answer(s); eg. 'C', 'DA'.")
                            answer = None

                        else:
                            if len(q.correct_answer_ids) == 1:
                                print(f"FALSE: The correct answer is {q.correct_answers[0].letter}.\n{postmortem}")
                            else:
                                print(f"FALSE: The correct answers are {correct_answers}.\n{postmortem}")
                else:
                    print(
                        f"ERROR: the provided answer ('{answer.lower()}') is invalid.\n"
                        f"Please provide answers from the above list; eg. 'C', 'DA'."
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

            print(f"CURRENT GRADE: {grade} ({total_correct_count}/{total_displayed_count} correct)")
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

                question_id = q.question_id
                question_text = q.text.replace(f"\'", "\'\'")
                question_postmortem = q.postmortem.replace(f"\'", "\'\'") if q.postmortem else ""

                c.execute(
                    f"INSERT INTO questions VALUES ("
                    f"{question_id},"
                    f"'{question_text}',"
                    f"'{question_postmortem}'"
                    f")"
                )

                conn.commit()

                for i in range(len(q.answers)):

                    answer_question_id = q.answers[i].question_id
                    answer_text = q.answers[i].text.replace("'", "''")
                    answer_is_correct = 1 if q.answers[i].is_correct else 0

                    c.execute(
                        f"INSERT INTO answers (question_id, text, is_correct) VALUES ("
                        f"{answer_question_id}, "
                        f"'{answer_text}', "
                        f"'{answer_is_correct}'"
                        f")"
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

                    if "is_correct" not in answer:
                        pass

                    question.answers.append(
                        Answer(
                            answer_id=j + 1,
                            question_id=i + 1,
                            text=answer["text"],
                            is_correct=answer["is_correct"]
                        )
                    )

                self.questions.append(question)

            print("INFO: Dumpyfile parsing complete.")

    def delete_context(self, message):
        print(f"ERROR: {message} Deleting local database...")
        os.remove(self.sqlite_context_path)
        exit(1)

    @staticmethod
    def generate_dumpyfile_friendly_json(dumpyfile_description, shuffle_answers, questions):
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


if __name__ == "__main__":
    Dumpy().execute_braindump()
