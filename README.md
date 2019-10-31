# dumpy

Dumpy is a Python 3 utility used to administer CLI-based braindumps.

## a friendly introduction

Dumpy lets you take multiple-choice quizzes on the command line.

It also introduces a "dumpyfile" speficiation, for files representing multiple-choice quizzes.

### the dumpyfile spec

A "dumpyfile" is a JSON-formatted file with a .dumpy extension, in the following format:


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

## requirements and configuration

 * Dumpy requires Python 3.7.x.
 * Dumpy also requires dumpyfiles.  These need to be in the project root under `dumpyfiles/`.
 * Dumpy requires a JSON-formatted `dumpy.config` in the project root, in the following format:

```
"default_context": (string)     The name of the default .dumpy file to load on program execution.
```

The `default_context` is the name of the dumpyfile that Dumpy should import and/or execute.

## running dumpy

To run a braindump:

1. Specify a `default_context` in the dumpy.config.
2. Put a .dumpy file in `dumpyfiles/`.
3. `cd /path/to/dumpy`
4. `python3 -m unittest test.py`

## the big picture

Dumpy parses the dumpyfile and creates a local SQLite3 database under `contexts/` in the project root.  It loads the 
database contents, and from those, it issues a CLI-based braindump.