from urllib import request

from bs4 import BeautifulSoup
from PyQt5.QtCore import QThread, pyqtSignal

from db import session, Language, Topic, Question
import time


class Worker(QThread):
    update = pyqtSignal(Question)
    finish = pyqtSignal(Topic)

    def __init__(self, lang, url, parent=None):
        super(Worker, self).__init__(parent)
        self.lang = session.query(Language).filter(Language.name == lang).first()
        self.url = url
        self.ps = self.get()
        self.remain_line = ''

    def __del__(self):
        self.wait()

    def get(self):
        ''' add questions from python library document.
        '''
        with request.urlopen(self.url) as resp:
            source = resp.read()
            soup = BeautifulSoup(source, 'html.parser')
            body = soup.find('div', attrs={'role': 'main'})
            h1 = body.find('h1').text.split(' —')[0]
            _topic = session.query(Topic).filter(Topic.title == h1).first()
            if _topic:
                raise FileExistsError
            self.topic = Topic(title=h1, lang_id=self.lang.id)
            session.add(self.topic)
            session.commit()
            ps = body.find_all('p')
            return ps

    def run(self):
        for p in self.ps:
            text = self.replace(p.text)
            line = '' + self.remain_line
            self.remain_line = ''
            tmp_word = None
            q = None
            for word in text.split(' '):
                word = ' ' + word
                if tmp_word:
                    word = tmp_word + word
                    tmp_word = None
                tmp_line = line + word
                len_tmp_line = len(tmp_line)
                if len_tmp_line >= 70 and len_tmp_line <= 80:
                    q = Question(
                        text=tmp_line.lstrip(),
                        topic_id=self.topic.id
                    )
                    line = ''
                elif len_tmp_line > 80:
                    q = Question(
                        text=line.lstrip(),
                        topic_id=self.topic.id
                    )
                    line = ''
                    tmp_word = word
                elif len_tmp_line < 70:
                    line += word
            if line:
                self.remain_line = line
            if q:
                self.update.emit(q)
            time.sleep(0.1)
        else:
            self.finish.emit(self.topic)

    def replace(self, text):
        text = text.replace('\r', ' ').replace('\n', ' ').replace('  ', ' ')\
            .replace('¶', '').replace('’', "'").replace('–', '--').replace('“', '"').replace('”', '"')
        return text
