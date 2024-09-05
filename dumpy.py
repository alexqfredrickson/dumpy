import os
import json
import sqlite3
import datetime
import time
import random
from random import shuffle
from models import Question, Answer, TerminalColors


class Dumpy:
    def __init__(self):

        print("\n", end='', flush=True)
        print("THANK YOU FOR USING ....\n", end='', flush=True)
        print("     _                             \n", end='', flush=True)
        print("  __| |_   _ _ __ ___  _ __  _   _ \n", end='', flush=True)
        print(" / _` | | | | '_ ` _ \\| '_ \\| | | |\n", end='', flush=True)
        print("| (_| | |_| | | | | | | |_) | |_| |\n", end='', flush=True)
        print(" \\__,_|\\__,_|_| |_| |_| .__/ \\__, |\n", end='', flush=True)
        print("                      |_|    |___/\n\n", end='', flush=True)

        time.sleep(1)

        self.questions = []

        self.description = None
        self.shuffle_answers = None
        self.shuffle_questions_by_weight = None

        self.dumpyfile_path = os.environ["DUMPY_FILEPATH"] if "DUMPY_FILEPATH" in os.environ else None
        self.dumpy_path = os.path.dirname(os.path.abspath(__file__))
        self.databases_directory = os.path.join(self.dumpy_path, "databases")
        self.dumpyfiles_directory = os.path.join(self.dumpy_path, "dumpyfiles")

        for d in [self.databases_directory, self.dumpyfiles_directory]:
            if not os.path.exists(d):
                os.mkdir(d)

        self.available_databases = os.listdir(self.databases_directory)

        # this is just a convenience.  by convention, a single dumpyfile is specified in the environment
        self.available_dumpyfiles = os.listdir(self.dumpyfiles_directory)

        if len(self.available_databases) == 0:

            # ensure dumpyfile was specified and exists
            if not self.dumpyfile_path:
                print(f"ERROR: The environment variable `DUMPY_FILEPATH` was not set.")
                exit(1)

            if not os.path.exists(self.dumpyfile_path):
                print(f"ERROR: {self.dumpyfile_path} was not found.")
                exit(1)

            self.selected_database = os.path.join(
                self.databases_directory,
                os.path.basename(self.dumpyfile_path.replace(".dumpy", "")) + ".db"
            )

            self.selected_dumpyfile = os.path.join(self.dumpyfiles_directory, os.path.basename(self.dumpyfile_path))
            self.import_dumpyfile()

        else:
            print("Please select an option (e.g. '1'):\n")

            options = []

            for ad in self.available_databases:
                options.append(("LOAD", f"Load {ad}", ad.replace(".db", "")))

            if self.dumpyfile_path:
                options.append(("IMPORT", f"Import {self.dumpyfile_path}", self.dumpyfile_path))

            for i in range(1, len(options) + 1):
                print(f"    {i}. {options[i - 1][1]}")

            print("")

            selected_option = int(input())
            selection = options[selected_option - 1]
            selection_type = selection[0]

            if selection_type == "LOAD":
                selected_database_name = selection[2]
                self.selected_database = os.path.join(self.databases_directory, selected_database_name + ".db")
                self.selected_dumpyfile = os.path.join(self.dumpyfiles_directory, selected_database_name + ".dumpy")

            elif selection_type == "IMPORT":

                if self.dumpyfile_path:
                    self.selected_database = os.path.join(
                        self.databases_directory,
                        os.path.basename(self.dumpyfile_path.replace(".dumpy", "")) + ".db"
                    )

                    self.selected_dumpyfile = os.path.join(
                        self.dumpyfiles_directory, os.path.basename(self.dumpyfile_path)
                    )

                else:
                    selected_database_name = self.available_databases[selected_option - 1].replace(".db", "")
                    self.selected_database = os.path.join(self.databases_directory, selected_database_name + ".db")
                    self.selected_dumpyfile = os.path.join(self.dumpyfiles_directory, selected_database_name + ".dumpy")

                self.import_dumpyfile()

        self.load_questions_from_database()
        self.begin_braindump()

    def load_questions_from_database(self):
        """
        Validates the existence of the local dumpy database and loads all questions/answers from it.
        """

        questions, answers, metadata, conn = None, None, None, None

        try:
            conn = sqlite3.connect(self.selected_database)
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

        if len(questions) == 0 or len(answers) == 0:
            print("ERROR: the database is empty and will need to be deleted and re-imported.")
            exit(1)

        self.description = metadata[0]
        self.shuffle_answers = metadata[1]
        self.shuffle_questions_by_weight = metadata[2]

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
                    answers=[a for a in answers if int(a.question_id) == q[0]],
                    attempted_count=q[3],
                    correct_count=q[4],
                    enabled=q[5]
                )
                for q in questions
            ]
        )

        if self.shuffle_answers:
            [q.shuffle_answers() for q in self.questions]

        # idea here is to perform a simple weighted shuffle based on how often questions have been answered correctly.
        # weights with '0' are ignored by the lambda, so do an initial shuffle prior to the weighted one.
        if self.shuffle_questions_by_weight:
            shuffle(self.questions)

            self.questions.sort(
                key=lambda q: (random.random() * (q.correct_count / q.attempted_count)) if q.attempted_count > 0 else 0
            )

        for q in self.questions:
            q.assign_letters_to_answers()

        self.questions = [q for q in self.questions if q.enabled == 1]

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
                        print(f"{TerminalColors.OKGREEN}CORRECT{TerminalColors.ENDC}: {correct_answers}\n{postmortem}")

                        self.execute_sqlite([
                            f"UPDATE questions SET attempted_count = attempted_count + 1 WHERE id = {q.question_id}",
                            f"UPDATE questions SET correct_count = correct_count + 1 WHERE id = {q.question_id}",
                        ])

                        total_correct_count += 1

                    else:
                        if len(q.correct_answer_ids) != len(chosen_answer_ids):

                            print(
                                f"ERROR: please provide exactly {len(q.correct_answer_ids)} answer(s); eg. 'C', 'DA'."
                            )

                            answer = None

                        else:
                            if len(q.correct_answer_ids) == 1:
                                print(f"{TerminalColors.WARNING}FALSE{TerminalColors.ENDC}: The correct answer "
                                      f"is {q.correct_answers[0].letter}.\n{postmortem}")
                            else:
                                print(f"{TerminalColors.WARNING}FALSE{TerminalColors.ENDC}: The correct answers "
                                      f"are {correct_answers}.\n{postmortem}")

                            self.execute_sqlite([
                                f"UPDATE questions SET attempted_count = attempted_count + 1 WHERE id = {q.question_id}"
                            ])
                else:
                    print(
                        f"ERROR: the provided answer ('{answer.lower()}') is invalid.\n"
                        f"Please provide answers from the above list; eg. 'C', 'DA'."
                    )
                    answer = None

            percent = (total_correct_count / total_displayed_count) * 100

            grade = f"{TerminalColors.WARNING}F{TerminalColors.ENDC}"

            if percent >= 90:
                grade = f"{TerminalColors.OKGREEN}A{TerminalColors.ENDC}"
            elif percent >= 80:
                grade = f"{TerminalColors.OKGREEN}B{TerminalColors.ENDC}"
            elif percent >= 70:
                grade = f"{TerminalColors.OKGREEN}C{TerminalColors.ENDC}"
            elif percent >= 60:
                grade = f"{TerminalColors.WARNING}D{TerminalColors.ENDC}"

            print(f"CURRENT GRADE: {grade} ({total_correct_count}/{total_displayed_count} correct)")
            print("Press the enter key to continue.")
            input()

    def import_dumpyfile(self):
        """
        Creates a local database from a .dumpy file.
        """

        sql_statements = []

        # recreate the database if it exists
        if os.path.exists(self.selected_database):
            os.remove(self.selected_database)

        # create the database; any self.execute_sqlite() operation will create it if it doesn't already exist
        if not os.path.exists(self.selected_database):
            print(f"INFO: Importing {self.dumpyfile_path} into {self.selected_database} ...")

            self.execute_sqlite([
                "CREATE TABLE metadata ("
                "`description` TEXT,"
                "`shuffle_answers` INTEGER DEFAULT 0,"
                "`shuffle_questions_by_weight` INTEGER DEFAULT 1,"
                "`database_created_time` TEXT"
                ");",

                "CREATE TABLE questions ("
                "`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
                "`text`	TEXT NOT NULL,"
                "`postmortem` TEXT,"
                "`attempted_count` INTEGER DEFAULT 0,"
                "`correct_count` INTEGER DEFAULT 0,"
                "`enabled` INTEGER DEFAULT 1"
                ");",

                "CREATE TABLE answers ("
                " `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
                " `question_id`	INTEGER NOT NULL,"
                " `text`	TEXT NOT NULL,"
                " `is_correct`	INTEGER NOT NULL DEFAULT 0"
                ");"
            ])

            print(f"INFO: {self.selected_database} has been successfully created.\n")

        with open(self.selected_dumpyfile, 'r') as dumpyfile:
            dumpyfile_contents = json.loads(dumpyfile.read())

        self.description = dumpyfile_contents["metadata"]["description"]
        self.shuffle_answers = dumpyfile_contents["metadata"]["shuffle_answers"]
        self.shuffle_questions_by_weight = dumpyfile_contents["metadata"]["shuffle_questions_by_weight"]

        sql_statements.append(
            f"INSERT INTO metadata VALUES ("
            f"\"{dumpyfile_contents["metadata"]["description"]}\", "
            f"\"{1 if dumpyfile_contents["metadata"]["shuffle_answers"] else 0}\", "
            f"\"{1 if dumpyfile_contents["metadata"]["shuffle_questions_by_weight"] else 0}\", "
            f"\"{datetime.datetime.now()}\""
            f")"
        )

        for i in range(len(dumpyfile_contents["questions"])):

            question = None
            this_question = dumpyfile_contents["questions"][i]

            try:
                question = Question(
                    question_id=i + 1,
                    text=this_question["text"],
                    postmortem=this_question["postmortem"] if "postmortem" in this_question else None,
                    answers=[],
                    attempted_count=0,
                    correct_count=0,
                    enabled=True
                )

            except Exception as e:
                print(e)

            for j in range(len(this_question["answers"])):
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

        for q in self.questions:

            question_id = q.question_id
            question_text = q.text.replace(f"\'", "\'\'")
            question_postmortem = q.postmortem.replace(f"\'", "\'\'") if q.postmortem else ""

            sql_statements.append(
                f"INSERT INTO questions VALUES ("
                f"{question_id},"
                f"'{question_text}',"
                f"'{question_postmortem}',"
                f"'0',"  # attempted_count
                f"'0',"  # correct_count
                f"'1'"  # enabled
                f")"
            )

            for i in range(len(q.answers)):
                answer_question_id = q.answers[i].question_id
                answer_text = q.answers[i].text.replace("'", "''")
                answer_is_correct = 1 if q.answers[i].is_correct else 0

                sql_statements.append(
                    f"INSERT INTO answers (question_id, text, is_correct) VALUES ("
                    f"{answer_question_id}, "
                    f"'{answer_text}', "
                    f"'{answer_is_correct}'"
                    f")"
                )

        self.execute_sqlite(sql_statements)

    def execute_sqlite(self, sql_statements):
        """
        Executes some SQL.
        """

        s, conn = "", None

        try:
            conn = sqlite3.connect(self.selected_database)
            c = conn.cursor()

            for s in sql_statements:
                c.execute(s)

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(e, s)

        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    Dumpy()
