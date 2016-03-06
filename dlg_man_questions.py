from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QLabel,\
    QPushButton, QAbstractItemView, QListWidgetItem, QMessageBox,\
    QInputDialog
from dlg_man_topics import TopicManagerDlg

from db import session, Language, Topic, Question
from worker import Worker

langs = session.query(Language).all()


class QuestionManagerDlg(TopicManagerDlg):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QuestionManagerDlg, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent):
        super(QuestionManagerDlg, self).__init__(parent)

        self.btnAddL = QPushButton('Add')
        self.btnRemoveL = QPushButton('Remove')
        self.btnRemoveL.setEnabled(False)
        self.LangBox.addWidget(self.btnAddL)
        self.LangBox.addWidget(self.btnRemoveL)

        self.btnAddT = QPushButton('Add')
        self.btnRemoveT = QPushButton('Remove')
        self.btnRemoveT.setEnabled(False)
        self.topicBox.addWidget(self.btnAddT)
        self.topicBox.addWidget(self.btnRemoveT)

        lblQuestions = QLabel('Select a question.')
        self.lstQuestions = QListWidget()
        self.lstQuestions.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.btnRemoveQ = QPushButton('Remove')
        self.btnRemoveQ.setEnabled(False)

        _layout3 = QVBoxLayout()
        _layout3.addWidget(lblQuestions)
        _layout3.addWidget(self.lstQuestions)
        _layout3.addWidget(self.btnRemoveQ)

        self.layout.addLayout(_layout3)
        self.setLayout(self.layout)

        self.lstLangs.itemClicked.connect(self.selectLang)
        self.lstTopics.itemClicked.connect(self.selectTopic)
        self.lstQuestions.itemClicked.connect(self.onSelectQuestion)
        self.btnAddL.clicked.connect(self.onAddL)
        self.btnRemoveL.clicked.connect(self.onRemoveL)
        self.btnAddT.clicked.connect(self.onAddT)
        self.btnRemoveT.clicked.connect(self.onRemoveT)
        self.btnRemoveQ.clicked.connect(self.onRemoveQ)

    def selectLang(self, item):
        ''' show topics that are related with selected language.
        :param item: language
        :return: QListWidgetItem
        '''
        self.btnRemoveL.setEnabled(True)
        _lang = item.text()
        lang = session.query(Language).filter(Language.name == _lang).first()
        if not lang:
            return
        topics = lang.topics.all()
        self.lstTopics.clear()
        for topic in topics:
            item = QListWidgetItem()
            item.setText(topic.title)
            item.setStatusTip(str(topic.id))
            self.lstTopics.addItem(item)
        self.lstQuestions.clear()

    def selectTopic(self, item):
        self.btnRemoveT.setEnabled(True)
        _topic = item.text()
        topic = session.query(Topic).filter(Topic.title == _topic).first()
        questions = topic.questions.all()
        self.lstQuestions.clear()
        for q in questions:
            item = QListWidgetItem()
            item.setText(q.text)
            item.setStatusTip(str(q.id))
            self.lstQuestions.addItem(item)

    def onSelectQuestion(self, item):
        ''' Set the button 'Remove question' to enabled.
        '''
        self.btnRemoveQ.setEnabled(True)

    def onAddL(self):
        ''' Add new language.
        '''
        lang, ok = QInputDialog.getText(self, 'add language', 'Input language name')
        if ok and lang and lang.strip():
            if self.lstLangs.findItems(lang, Qt.MatchFixedString):
                QMessageBox.information(self, 'Error', '{} exists already.'.format(lang))
                return
            l = Language(name=lang)
            session.add(l)
            session.commit()
            item = QListWidgetItem()
            item.setText(l.name)
            item.setStatusTip(str(l.id))
            self.lstLangs.addItem(item)

    def onRemoveL(self):
        ''' remove selected langauge and realted topics and questions.
        '''
        answer = QMessageBox.question(self, 'Remove Language',
                                      "This operation will remove this language and it's topics.")
        if answer == QMessageBox.No:
            return
        row = self.lstLangs.currentRow()
        id = self.lstLangs.currentItem().statusTip()
        record = session.query(Language).filter(Language.id == id)
        if record:
            record.delete(synchronize_session=False)
            self.lstLangs.takeItem(row)
            self.lstTopics.clear()
            ts = session.query(Topic).filter(Topic.lang_id == id).all()
            for t in ts:
                qs = session.query(Question).filter(Question.topic_id == t.id).all()
                for q in qs:
                    session.delete(q)
                session.delete(t)
        session.commit()
        self.btnRemoveL.setEnabled(False)

    # @pyqtSlot(Topic)
    def _finishAddQuestions(self, t):
        item = QListWidgetItem()
        item.setText(t.title)
        item.setStatusTip(str(t.id))
        self.lstTopics.addItem(item)
        session.commit()
        print('finished')

    # @pyqtSlot(Question)
    def _appendQuestion(self, q):
        print('q: ', q)
        item = QListWidgetItem()
        item.setText(q.text)
        item.setStatusTip(str(q.id))
        self.lstQuestions.addItem(item)
        session.add(q)

    def onAddT(self):
        ''' Add new topic.
        '''
        lang = self.lstLangs.currentItem()
        if not lang:
            return
        lang = lang.text()
        url, ok = QInputDialog.getText(self, 'add topic', 'Input url for {}'.format(lang))
        if ok and lang and url and url.strip():
            try:
                thread = Worker(lang, url, self)
                thread.update.connect(self._appendQuestion)
                thread.finish.connect(self._finishAddQuestions)
                thread.start()
            except FileExistsError:
                QMessageBox.information(self, 'Error', 'This topic exists already.')
            except ValueError:
                QMessageBox.information(self, 'Error', 'cannot access the url.')

    def onRemoveT(self):
        answer = QMessageBox.question(self, 'Remove Topic', "This operation will remove this topic and it's questions.")
        if answer == QMessageBox.No:
            return
        row = self.lstTopics.currentRow()
        id = self.lstTopics.currentItem().statusTip()
        record = session.query(Topic).filter(Topic.id == id)
        if record:
            record.delete(synchronize_session=False)
            self.lstTopics.takeItem(row)
            self.lstQuestions.clear()
            qs = session.query(Question).filter(Question.topic_id == id).all()
            for q in qs:
                session.delete(q)
        session.commit()
        self.btnRemoveT.setEnabled(False)

    def onRemoveQ(self):
        ''' Remove a selected question from database.
        '''
        for item in self.lstQuestions.selectedItems():
            id = item.statusTip()
            self.lstQuestions.setCurrentItem(item)
            row = self.lstQuestions.currentRow()
            record = session.query(Question).filter(Question.id == id)
            if record:
                record.delete(synchronize_session=False)
                self.lstQuestions.takeItem(row)
        session.commit()
        self.btnRemoveQ.setEnabled(False)
