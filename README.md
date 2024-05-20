# dumpy

`dumpy` is a Python 3 framework that issues multiple-choice quizzes - or "braindumps" - in your terminal.

`dumpy` parses `dumpyfile`s into a local SQLite3 database. Questions are loaded  
from the database, from which CLI-based "braindumps" are administered.

## requirements
`dumpy` requires Python 3.7+.

## configuration

`dumpy` requires a `dumpy.config` in `.json` format in the project's root directory:

```
{
    # The name of the default .dumpy file to load on program execution.
    "default_braindump_filename": "foobar.dumpy"
}
```

`dumpy` also requires `dumpyfile`, located in a directory in the project's root directory, called `dumpyfiles/`.

### dumpyfiles

A `dumpyfile` is a `.json`-formatted file representing the answers of a multiple choice quiz.

It follows this format:

```
metadata: (object)            Optional metadata header.
    description: (string)     A detailed description of this .dumpy file
    shuffle_answers: (bool)   A flag indicating whether or not to shuffle the answers.
    
questions: (list of object)   A list of questions.
    text: (string)            The phrasing of the question itself.
    answers: (list)           A list of possible answers.
        text: (string)        The phrasing of one of the possible answers.
        is_correct: (bool)    Whether or not this answer is correct
    postmortem: (string)      A detailed explanation of why some answer is correct.
```

For example:

```json
{
  "metadata": {
    "description": "Fine Feathered Friends: A Bird Quiz",
    "shuffle_answers": true
  },
  "questions": [
    {
      "text": "Which of these flightless birds is native to South America?",
      "answers": [
        {
          "text": "Emu",
          "is_correct": false
        },
        {
          "text": "Cassowary",
          "is_correct": false
        },
        {
          "text": "Kiwi",
          "is_correct": false
        },
        {
          "text": "Rhea",
          "is_correct": true
        }
      ],
      "postmortem": "Although distantly related to the emu, the rhea is the only one of these flightless birds native to South America (and not Australia)."
    },
    ...
  ]
}
```

## running dumpy

To run a braindump:

1. Create a `~/dumpyfiles/` directory in the project root.
2. Create  `.dumpyfile` and put it in this directory.
3. Create a `dumpy.config` file in the project root, and specify a `default_braindump_filename`.
4. `cd /path/to/dumpy`
5. `python3 -m unittest test.py`
