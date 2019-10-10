import csv
from operator import attrgetter


class HighScore:

    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __str__(self):
        return "[" + self.name + ": " + str(self.score) + "]"

    __repr__ = __str__


class HighScoreTable:

    def __init__(self):
        self.high_scores = []

    def load(self):
        file_name = "data/high_scores.txt"
        with open(file_name, "r") as high_scores_file:
            reader = csv.reader(high_scores_file)
            for line in reader:
                name = line[0]
                score = int(line[1])
                self.high_scores.append(HighScore(name, score))

        self.high_scores.sort(key=attrgetter('score'), reverse=True)

    def save(self):
        file_name = "data/high_scores.txt"
        with open(file_name, "w", newline='') as high_scores_file:
            writer = csv.writer(high_scores_file)
            for score in self.high_scores:
                writer.writerow([score.name, str(score.score)])

    def is_score_high(self, new_score):
        is_high = False
        lowest_score = self.high_scores[-1]
        if new_score > lowest_score.score:
            is_high = True
        return is_high

    def add_new_high_score(self, name, score):
        self.high_scores.pop()
        self.high_scores.append(HighScore(name, score))
        self.high_scores.sort(key=attrgetter('score'), reverse=True)
        self.save()
