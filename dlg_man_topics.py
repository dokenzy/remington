from PyQt5.QtWidgets import QDialog, QListWidget,\
    QHBoxLayout, QVBoxLayout, QLabel, QListWidgetItem

from db import session, Language


def langs():
    return session.query(Language).all()


class TopicManagerDlg(QDialog):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TopicManagerDlg, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent):
        super(TopicManagerDlg, self).__init__(parent)
        self.parent = parent

        self.layout = QHBoxLayout()

        self.LangBox = QVBoxLayout()
        lblLangs = QLabel('Select a language.')
        self.lstLangs = QListWidget()
        for lang in langs():
            item = QListWidgetItem()
            item.setText(lang.name)
            item.setStatusTip(str(lang.id))
            self.lstLangs.addItem(item)
        self.LangBox.addWidget(lblLangs)
        self.LangBox.addWidget(self.lstLangs)

        self.topicBox = QVBoxLayout()
        lblTopics = QLabel('Select a topic.')
        self.lstTopics = QListWidget()
        self.topicBox.addWidget(lblTopics)
        self.topicBox.addWidget(self.lstTopics)

        self.layout.addLayout(self.LangBox)
        self.layout.addLayout(self.topicBox)
        self.setLayout(self.layout)

        self.lstLangs.itemClicked.connect(self.selectLang)

    def selectLang(self, item):
        _lang = item.text()
        lang = session.query(Language).filter(Language.name == _lang).first()
        topics = lang.topics.all()
        self.lstTopics.clear()
        for topic in topics:
            item = QListWidgetItem()
            item.setText(topic.title)
            item.setStatusTip(str(topic.id))
            self.lstTopics.addItem(item)
