from question import Question
import csv
import enum
import os
import random
import sys

class Color(enum.Enum):
    RESET = enum.auto()
    RED = enum.auto()
    GREEN = enum.auto()
    CYAN = enum.auto()
    YELLOW = enum.auto()

COLORS = dict(zip([*Color], ["\033[1;00;40m",
                             "\033[1;31;40m",
                             "\033[1;32;40m",
                             "\033[1;36;40m",
                             "\033[1;33;40m"]))
useColor = False

def colorText(s, color):
    if useColor: print(COLORS[color] + s + COLORS[Color.RESET])
    else: print(s)

def results(total, correct):
    colorText("\n\n-----------------------------", Color.YELLOW)
    print("You answered {} questions and got {} correct.".format(total, correct))
    percent = 0 if total == 0 else correct*100/total
    colorText("{}/{}  {:.2f}%".format(correct, total, percent), Color.CYAN)

if __name__ == "__main__":
    useColor = sys.platform == "linux" or "--color" in sys.argv
    shuffle = "--shuffle" in sys.argv

    # load questions from .csv
    questions = []
    with open("quiz.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            questions.append(Question.fromList(row))

    # quiz!
    if shuffle:
        # shuffle questions
        random.shuffle(questions)
        # reassign IDs to count in order
        i = 0
        for q in questions:
            q.id = i
            i += 1

    total, correct = 0, 0
    try:
        for q in questions:
            print("Question #{}: {}".format(q.id + 1, q.text))
            ops = list(enumerate(q.options))
            random.shuffle(ops)
            for i, op in enumerate(thing[1] for thing in ops):
                print("{}. {}".format(i + 1, op))

            ans = ""
            while True:
                try:
                    ans = int(input("Enter answer: "))
                    if ans < 1 or ans > len(q.options):
                        print("That's not in the range!")
                    else:
                        break
                except ValueError:
                    print("That's not a number!")
            if ops[ans-1][0] in q.correct:
                colorText("Correct!", Color.GREEN)
                correct += 1
            else:
                localCorrect = set([i+1 for i, stuff in enumerate(ops) if stuff[0] in q.correct])
                colorText("Wrong. It's {}".format(", ".join(map(str, localCorrect))), Color.RED)
            total += 1
            input("Press enter to continue . . . ")
            print()
    except KeyboardInterrupt:
        pass
    results(total, correct)
