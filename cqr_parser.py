from collections import defaultdict
from enum import Enum
from html.parser import HTMLParser
from question import Question
import csv
import sys

class DataState(Enum):
    NONE = 0
    TEXT = 1
    OPTION = 2

class QuizParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.currentQuestion = None
        self.dataState = DataState.NONE
        self.correctOption = False

    def end(self):
        if self.currentQuestion is not None:
            self.questions.append(self.currentQuestion)
        self.currentQuestion = Question()
    
    def handle_starttag(self, tag, attrs):
        attrs = defaultdict(str, attrs)
        if tag == "textarea" and attrs["name"] == "question_text":
            # new question
            self.end()
        elif tag == "div" and attrs["class"] == "question_text user_content":
            # question text incoming
            self.dataState = DataState.TEXT
        elif tag =="div" and attrs["class"].startswith("answer answer_for_") and attrs["class"].endswith("correct_answer"):
            # incoming option is a correct one
            self.correctOption = True
        elif tag == "div" and attrs["class"] == "answer_text":
            # answer option incoming
            self.dataState = DataState.OPTION

    def handle_data(self, data):
        data = data.strip()
        if self.dataState == DataState.TEXT:
            self.currentQuestion.text = data
        elif self.dataState == DataState.OPTION:
            self.currentQuestion.options.append(data)
            if self.correctOption:
                self.currentQuestion.correct.add(len(self.currentQuestion.options) - 1)
                self.correctOption = False
        self.dataState = DataState.NONE

if __name__ == "__main__":
    # check command line arguments
    if len(sys.argv) == 1:
        print("Usage: python cqr_parser.py htmlfile1 [htmlfile2...]\n")
        exit(0)

    # read each html file and parse it
    parser = QuizParser()
    for filename in sys.argv[1:]:
        with open(filename, "r") as htmlfile:
            parser.feed("".join(htmlfile.readlines()))
    parser.end()
    
    # for q in parser.questions:
    #     print(repr(q))

    # write csv file
    with open('quiz.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for q in parser.questions:
            csvwriter.writerow(q.toList())
