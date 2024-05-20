# dumpy

`dumpy` is a Python 3 framework that issues multiple-choice quizzes - or "braindumps" - in your terminal.

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
metadata: (object)              Optional metadata header.
    description: (string)       A detailed description of this .dumpy file
    shuffle_answers: (bool)     A flag indicating whether or not to shuffle the answers.
    
questions: (list)               A list of questions.
    question: (object)          A question.
        text: (string)          The phrasing of the question itself.
        answers: (list)         A list of possible answers.
            text: (string)      The phrasing of one of the possible answers.
            is_correct: (bool)  Whether or not this answer is correct
        postmortem: (string)    A detailed explanation of why some answer is correct.

```



## running dumpy

To run a braindump:

1. Specify a `default_braindump_filename` in the dumpy.config.
2. Put a .dumpy file in `dumpyfiles/`.
3. `cd /path/to/dumpy`
4. `python3 -m unittest test.py`

## the big picture

Dumpy parses the dumpyfile and creates a local SQLite3 database under `contexts/` in the project root.  It loads the 
database contents, and from those, it issues a CLI-based braindump.