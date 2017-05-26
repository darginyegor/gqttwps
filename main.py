import sys
import json
import requests
import time
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, uic


class App(QtWidgets.QApplication):
    def __init__(self, list_of_str):
        super().__init__(list_of_str)
        self.ui = Ui()
        self.ui.show()
        self.ui.getButton.clicked.connect(self.on_get_button_click)
        try:
            f = open('api.cfg')
            config = [line for line in f]
            self.ui.apiKeyInput.setText(config[0])
            self.ui.usernameInput.setText(config[1])
        except FileNotFoundError:
            pass

    # Обработчик нажатия на кнопку "Получить"
    def on_get_button_click(self):
        query = self.ui.queryInput.text()
        min_size = str(self.ui.sizeSelector.currentText()).split('x')
        api_key = self.ui.apiKeyInput.text()
        username = self.ui.usernameInput.text()
        self.get_by_query(query, min_size, api_key, username)

    # Получение и кэширование картинок по запросу
    def get_by_query(self, q, min_size, api_key, username):
        url = 'http://yandex.ru/images/search/xml?user=al'+username+'&key='+api_key+'&text='+q+'&isize=eq&iw='+min_size[0]+'&ih='+min_size[1]
        print('Получение списка URL-адресов...')
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "lxml")  # .find(class_='serp-list')
        data_list = [i['data-bem'] for i in soup.find_all(class_='serp-item')]
        pictures = []
        for item in data_list[:10]:
            data = json.loads(item)
            pictures.append(data['serp-item']['img_href'])
        print('Кэширование изображений...')
        self.cache(pictures)

    # Кэширование полученных изображений
    def cache(self, list_of_urls):
        for url in list_of_urls:
            name = str(len(url))  # str(time.time())
            ext = url[-3:]
            filename = 'cached/'+name+'.'+ext
            image = requests.get(url, verify=False).content
            f = open(filename, 'wb+')
            f.write(image)
            f.close()


# Класс графического интерфейса
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/gqttwps.ui', self)
        self.setWindowTitle('Параметры загрузки обоев')


app = App(sys.argv)
sys.exit(app.exec_())


