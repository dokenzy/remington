# -*- coding: utf-8 -*-

import sys
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton

from layout import Ui_MainWindow
from dlg_man_questions import TopicManagerDlg, QuestionManagerDlg
from utils import colorize
from db import session, Topic


class Quickstart(QMainWindow):
    def __init__(self, parent=None):
        super(Quickstart, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.started = False
        self.start_time = 0
        self.end_time = 0

    def endAnswer(self):
        answer = self.ui.lineAnswer.text()
        len_answer = len(answer)
        if len_answer == 0:
            return
        self.end_time = datetime.now()
        take_time = self.end_time - self.start_time
        self.started = False
        self.start_time = 0
        question = self.ui.lblQuestion.text()
        len_question = len(question)
        result = ''
        wrong = 0
        for index, char in enumerate(question):
            try:
                if char == answer[index]:
                    result += colorize(char, True)
                else:
                    result += colorize('-', False)
                    wrong += 1
            except IndexError:
                result += colorize('+', False)
                wrong += 1
        if len_answer > len_question:
            result += colorize(answer[len_question:], False)
        self.ui.lineAnswer.setText('')
        self.ui.lblAnswer.setText(result)
        cpm = (len_question - wrong) / take_time.total_seconds() * 60
        self.ui.lblTime.setText('{:.0f} CPM'.format(cpm))
        acc_rate = (len_question - wrong) / len_question * 100
        self.ui.lblAccuracy.setText('{0:.2f}%'.format(acc_rate))
        self.ui.lblAnswer.setText('')
        try:
            self.ui.lblQuestion.setText(next(self.qs).text)
        except StopIteration:
            self.ui.lblQuestion.setText('Finish')
            self.ui.lineAnswer.setEnabled(False)

    def changeAnswer(self):
        if not self.started and len(self.ui.lineAnswer.text()):
            self.started = True
            self.start_time = datetime.now()
        question = self.ui.lblQuestion.text()
        answer = self.ui.lineAnswer.text()
        result = ''
        for q, a in zip(question, answer):
            if q == a:
                result += colorize(a, True)
            else:
                result += colorize(a, False)
        self.ui.lblAnswer.setText(result)
        self.ui.lblAnswer.setEnabled(True)

    def start(self):
        self.game_dlg = TopicManagerDlg(self)
        layout = QVBoxLayout()
        btnStart = QPushButton('Start')
        layout.addWidget(btnStart)
        self.game_dlg.layout.addLayout(layout)
        btnStart.clicked.connect(self.start_game)
        self.game_dlg.exec_()

    def start_game(self):
        _topic = self.game_dlg.lstTopics.currentItem().text()
        topic = session.query(Topic).filter(Topic.title == _topic).first()
        qs = topic.questions.all()
        self.game_dlg.close()
        self.qs = iter(qs)
        self.ui.lineAnswer.setEnabled(True)
        self.ui.lineAnswer.setFocus()
        self.ui.lblQuestion.setText(next(self.qs).text)

    def openManQuestionDlg(self):
        dlg = QuestionManagerDlg(self)
        dlg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qs = Quickstart()
    qs.show()
    sys.exit(app.exec_())
