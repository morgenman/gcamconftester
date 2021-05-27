# Подготовка
1) Скачиваем и устанавливаем питона
https://www.python.org/downloads/
2) Скачиваем весь репозиторий, распаковываем, заходим в папку, открываем консоль в папке через шифт+пкм
3) В консоль пишем "***pip install -r requirements.txt***" (без кавычек)
4) Включаем на телефоне отладку по адб, подключаем по ПРОВОДУ, на телефоне даём разрешение на отладку если спросит
5) Пишем в консоль "***.\adb\adb.exe tcpip 5555***" и после этого провод можно вытаскивать
6) Опять пишем в консоль "***.\adb\adb.exe connect IP_АДРЕС_ТЕЛЕФОНА:5555***" (IP адрес телефона можно узнать в настройках вайфая на телефоне или посмотреть в веб-интерфейсе роутера)
7) Сохраняем на телефоне свой конфиг НА НУЖНОМ МОДУЛЕ и кидаем его в папку со скриптом 
8) Ставим на телефоне время выключения экрана на подольше, запускаем гкам и ставим телефон на штатив или опираем на тапок
# Запуск
Для запуска в ту же консоль пишем

"***python gcamconftester.py имя_конфига название_ключа_для_теста [количество_значений_для_теста]***"

![изображение](https://user-images.githubusercontent.com/2606215/119790955-0d974780-bedd-11eb-881c-6b54ff523741.png)

Если количество значений для теста не указано, то будут дефолтные 5

Название ключа для теста можно узнать в camera_preferences.xml поискав по названию параметра в либпатчере и скопировать то что указано в android:key=

Желательно чтобы в имени конфига не было всяких всратых символов типа эмоджи, кавычек, пробелов и т.д

Пример: 
***python gcamconftester.py "8.2riv.xml" "lib_sharpness_key"***

В результате работы рядом со скриптом появится папка с названием ключа. В этой папке будут лежать фото (имя = значение) которые удобно смотреть и сравнивать через FastStone Image Viewer
![изображение](https://user-images.githubusercontent.com/2606215/119796119-c3fd2b80-bee1-11eb-82c2-89048871156e.png)

Так же можно тестить кастомные адреса и их значения

***python gcamconftester.py имя_конфига -custom номер_кастомного_значения адрес значения_через_двоеточие***

Пример:
***python gcamconftester.py "8.2riv.xml" --custom 2 0DE3694 24008052:04008052:44008052***

![изображение](https://user-images.githubusercontent.com/2606215/119791814-d7a69300-bedd-11eb-9036-e01444d66414.png)


Это запишет в User Defined Value 2 адрес 0DE3694 и переберет значения 24008052,04008052,44008052
# Баги / особенности
1) ~~Для нормальной работы в конфиге уже должен существовать необходимый ключ и в патчере для него должно быть выставлено любое значение~~ Должен быть включен соответствующий раздел патчера
2) ~~Точно так же и с кастомными значениями - оно должно быть включено и там должны быть введены какие-нибудь значения до запуска~~
3) ~~Автоматическое нажатие кнопок может не работать на телефонах у которых разрешение НЕ 1080р~~ вроде работает
4) Количество итоговых фото всегда будет количество_значений_для_теста+1
