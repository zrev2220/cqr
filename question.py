class Question():
    nextId = 0

    def __init__(self):
        self.id = Question.nextId
        self.text = ""
        self.options = []
        self.correct = set()
        Question.nextId += 1
    
    def __repr__(self):
        s = "Question {}: {}\n".format(self.id + 1, self.text)
        for i, op in enumerate(self.options):
            s += "{} {}\n".format("+" if i in self.correct else "-", op)
        return s

    def toList(self):
        return [self.id,\
                self.text,\
                [("*" if i in self.correct else "")+o for i, o in enumerate(self.options)]]

    def fromList(lst):
        q = Question()
        Question.nextId -= 1 # undo the auto-increment
        q.id = int(lst[0])
        q.text = lst[1]
        q.options = eval(lst[2])
        for i in range(len(q.options)):
            if q.options[i][0] == "*":
                q.correct.add(i)
                q.options[i] = q.options[i][1:]

        return q
