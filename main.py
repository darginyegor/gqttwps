import sys
import json
import requests
import os
from rt import RepeatedTimer
import threading
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, uic


class App(QtWidgets.QApplication):
    def __init__(self, list_of_str):
        super().__init__(list_of_str)
        self.thread_controller = ThreadController()
        self.pictures = []
        self.current_wallpaper = -1
        self.update_pictures()
        self.ui = Ui()
        self.ui.show()
        self.ui.getButton.clicked.connect(self.on_get_button_click)
        self.ui.startButton.clicked.connect(self.wp_setter_start)
        self.ui.stopButton.clicked.connect(self.wp_setter_stop)
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
        self.thread_controller.thread(self.get_by_query, 'images_getter', query, min_size, api_key, username)
        self.thread_controller['images_getter'].start()

    # Получение и кэширование картинок по запросу
    def get_by_query(self, q, min_size, api_key, username):
        url = 'http://yandex.ru/images/search/xml?user=al' + username \
              + '&key=' + api_key \
              + '&text=' + q \
              + '&isize=eq&iw=' + min_size[0] + '&ih=' + min_size[1]
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

    def update_pictures(self):
        self.pictures = [f for f in os.listdir(os.path.abspath(os.path.dirname(__file__)) + '/cached')]

    # Запуск цикла смены обоев
    def wp_setter_start(self):
        interval = self.ui.intervalSpinBox.value()
        self.thread_controller.repeat('wp_setter', interval, self.wp_setter_step)

    # Шаг ентого цикла
    def wp_setter_step(self):
        self.current_wallpaper += 1
        if not self.current_wallpaper < len(self.pictures):
            self.current_wallpaper = 0
        print('current', self.current_wallpaper)
        self.set_wallpaper(self.pictures[self.current_wallpaper])

    # Остановка цикла
    def wp_setter_stop(self):
        self.thread_controller['wp_setter'].stop()

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
        self.update_pictures()

    # Установка изображения в качетсве обоев
    # Setting picture as a wallpaper
    @staticmethod
    def set_wallpaper(image):
        path = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/cached/' + image
        os.system('gsettings set org.gnome.desktop.background picture-uri ' + path)


# Класс графического интерфейса
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/gqttwps.ui', self)
        self.setWindowTitle('Параметры загрузки обоев')


class ThreadController:
    def __init__(self):
        self.threads = {}

    def __getitem__(self, i):
        return self.threads[i]

    def thread(self, target, name, *args):
        thread = threading.Thread(target=target, name=name, args=[*args])
        self.threads[name] = thread

    def repeat(self, name,  interval, target, *args):
        rt = RepeatedTimer(interval, target, *args)
        self.threads[name] = rt


app = App(sys.argv)
sys.exit(app.exec_(),)


