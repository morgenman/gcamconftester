# Подготовка
1) Скачиваем и устанавливаем питона
https://www.python.org/downloads/
2) Скачиваем весь репозиторий, распаковываем, заходим в папку, открываем консоль в папке через шифт+пкм
3) В консоль пишем "***pip install -r requirements.txt***" (без кавычек)
4) Включаем на телефоне отладку по адб, подключаем по ПРОВОДУ, на телефоне даём разрешение на отладку если спросит
5) Пишем в консоль "***.\adb\adb.exe tcpip 5555***" и отключаем телефон
6) Опять пишем в консоль "***.\adb\adb.exe connect IP_АДРЕС_ТЕЛЕФОНА:5555***" (IP адрес телефона можно узнать в настройках вайфая на телефоне или посмотреть в веб-интерфейсе роутера)
7) Включаем гкам на телефоне и ставим телефон на штатив или опираем на тапок
# Запуск
В ту же консоль пишем "***python gcamconftester.py имя_конфига название_ключа_для_теста***"

Название ключа для теста можно узнать в camera_preferences.xml поискав по названию параметра в либпатчере и скопировать то что указано в android:key=

Желательно чтобы в имени конфига не было всяких всратых символов типа эмоджи, кавычек, пробелов и т.д

Пример: 
***python gcamconftester.py "8.2riv.xml" "lib_sharpness_key"***

Так же можно тестить кастомные адреса и их значения

***python gcamconftester.py имя_конфига -custom номер_кастомного_значения адрес значения_через_запятую***

Пример:
***python gcamconftester.py "8.2riv.xml" --custom 2 0DE3694 24008052,04008052,44008052***

Это запишет в User Defined Value 2 адрес 0DE3694 и переберет значения 24008052,04008052,44008052

