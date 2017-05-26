import sys
import json
import requests
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, uic


class App(QtWidgets.QApplication):
    def __init__(self, list_of_str):
        super().__init__(list_of_str)
        self.ui = Ui()
        self.ui.show()
        self.ui.getButton.clicked.connect(self.on_get_button_click)

    def on_get_button_click(self):
        query = self.ui.queryInput.text()
        min_size = str(self.ui.sizeSelector.currentText()).split('x')
        self.get_by_query(query, min_size)

    # Получение и кэширование картинок по запросу
    def get_by_query(self, q, min_size):
        url = 'http://yandex.ru/images/search?text='+q+'&isize=eq&iw='+min_size[0]+'&ih='+min_size[1]
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "lxml").find(class_='serp-list')
        data_list = [i['data-bem'] for i in soup.find_all(class_='serp-item')]
        pictures = []
        for item in data_list[:10]:
            data = json.loads(item)
            pictures.append(data['serp-item']['img_href'])
        print(pictures)


# Класс графического интерфейса
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/gqttwps.ui', self)
        self.setWindowTitle('Параметры загрузки обоев')


app = App(sys.argv)
sys.exit(app.exec_())


