# dumpy

`dumpy` is a Python 3.7+ framework that issues multiple-choice quizzes - or "braindumps" - in your terminal.

`dumpy` parses `dumpyfile`s into a local SQLite3 database. Questions are loaded  
from the database, from which CLI-based "braindumps" are administered.

## configuration

`dumpy` requires an environment variable called `DUMPY_FILEPATH`, which tells `dumpy` which 
`dumpyfile` to load. 

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
    "description": "Fine-Feathered Friends: A Quiz About Birds",
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

1. Set the `DUMPY_FILEPATH` environmental variable to point to a valid `dumpyfile`.`.
2. `cd /path/to/dumpy`
3. `python3 -m unittest test.py`
