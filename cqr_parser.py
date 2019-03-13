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
    WARNING = 3

class QuizParser(HTMLParser):
    ignoreTags = {"strong":"*", "em":"_"}
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
        if tag in QuizParser.ignoreTags and self.currentQuestion is not None:
            self.currentQuestion.text += " " + QuizParser.ignoreTags[tag]
        elif tag == "textarea" and attrs["name"] == "question_text":
            # new question
            self.end()
        elif (tag == "div" and attrs["class"] == "question_text user_content") or \
             (tag == "p" and "class" not in attrs):
            # question text incoming
            # if <p>, question text MAY be incoming (if not, will be squashed by the next <p> or question_text <div>)
            self.dataState = DataState.TEXT
            if tag == "p" and self.currentQuestion is not None:
                # the fact that we're bothering with a <p> indicates there were other tags in this question_text <div>
                # so we need to reset the question text to remove any data we erroneously read already
                self.currentQuestion.text = ""
        elif tag == "div" and attrs["class"].startswith("answer answer_for_") and attrs["class"].endswith("correct_answer"):
            # incoming option is a correct one
            self.correctOption = True
        elif tag == "div" and attrs["class"] == "answer_text":
            # answer option incoming
            self.dataState = DataState.OPTION

    def handle_data(self, data):
        if self.currentQuestion is None:
            return
        data = data.strip()
        if self.dataState == DataState.TEXT:
            self.currentQuestion.text += data
        elif self.dataState == DataState.OPTION:
            self.currentQuestion.options.append(data)
            if self.correctOption:
                self.currentQuestion.correct.add(len(self.currentQuestion.options) - 1)
                self.correctOption = False

    def handle_endtag(self, tag):
        # state resets at a </div>
        # this allows for 
        if tag == "div":
            self.dataState = DataState.NONE
        elif tag in QuizParser.ignoreTags and self.currentQuestion is not None:
            self.currentQuestion.text += QuizParser.ignoreTags[tag] + " "

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
