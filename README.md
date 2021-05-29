# Подготовка
1) Скачиваем и устанавливаем питона
https://www.python.org/downloads/
2) Скачиваем весь репозиторий, распаковываем, заходим в папку, открываем консоль в папке через шифт+пкм
3) В консоль пишем "***pip install -r requirements.txt***" (без кавычек)
4) Включаем на телефоне отладку по адб, подключаем по ПРОВОДУ, на телефоне даём разрешение на отладку если спросит
5) Пишем в консоль "***.\adb\adb.exe tcpip 5555***" и после этого провод можно вытаскивать
6) Опять пишем в консоль "***.\adb\adb.exe connect IP_АДРЕС_ТЕЛЕФОНА:5555***" (IP адрес телефона можно узнать в настройках вайфая на телефоне или посмотреть в веб-интерфейсе роутера)
7) Сохраняем на телефоне свой конфиг и кидаем его в папку со скриптом 
8) Ставим на телефоне время выключения экрана на подольше, запускаем гкам и ставим телефон на штатив или опираем на тапок
# Использование
```
Использование:
    python gcamconftester.py [-h] -c конфиг.xml [-k какой ключ перебирать] [-n количество значений для теста]
    python gcamconftester.py [-h] -c конфиг.xml [-custom номер кастомного адреса] [-a адрес] [-v значения через двоеточие]
    python gcamconftester.py [-h] -c конфиг.xml [-p название параметра в конфиге] [-l название модуля камеры] [-n количество значений для теста]

Пример:
    python gcamconftester.py -c "8.2riv.xml" -k lib_sharpness_key -n 3
    python gcamconftester.py -c "8.2riv.xml" --custom 2 -a 0de3694 -v 04008052:24008052:44008052
    python gcamconftester.py -c "8.2riv.xml" -p "Sharp Depth 2" -l "LDR"


Список аргументов:
  -h, --help            Показать информацию для помощи
  -c CONFIG, --config CONFIG
                        Имя конфига
  -k KEY, --key KEY     Название ключа для перебора настроек (Например: "lib_sharpness_key")
  -l LENS, --lens LENS  Имя модуля камеры на котором тестировать патчер (Например: "LDR") (по умолчанию: 1х)
  -p PARAMETER, --parameter PARAMETER
                        Название параметра в патчере для которого проводить тесты (Например: "Sharp Depth 2")
  -n NUM, --num NUM     Количество значений для перебора (по умолчанию: 5)
  -custom CUSTOM, --custom CUSTOM
                        Номер кастомного значения в патчере (от 1 до 12) в который вносить данные
  -a ADDRESS, --address ADDRESS
                        Адрес кастомного значения
  -v VALUES, --values VALUES
                        Кастомные значения через двоеточие
```
# Пример 1
```python gcamconftester.py -c "8.2riv.xml" -p "Sharp Depth 2" -l "LDR" -n 10```

(может не работать с некоторыми параметрами патчера. в этом случае воспользуйтесь вторым способом через ключ)

Имя модуля для -l должно полностью совпадать с именем на кнопке. Если не указано то выбирается 1х

![изображение](https://user-images.githubusercontent.com/2606215/120077450-26f1ec80-c0b3-11eb-9476-f6202dc5b552.png)

Название параметра для -p должно полностью совпадать с названием в патчере
![изображение](https://user-images.githubusercontent.com/2606215/120077439-1e99b180-c0b3-11eb-840d-b5368bcf7cac.png)

# Пример 2
```python gcamconftester.py -c "8.2riv.xml" -k lib_sharpness_key -n 3```

![изображение](https://user-images.githubusercontent.com/2606215/119966049-97194900-bfb3-11eb-87cd-f7c2a418f705.png)

Название ключа для теста можно узнать в camera_preferences.xml поискав по названию параметра в либпатчере и скопировать то что указано в android:key=

Желательно чтобы в имени конфига не было всяких всратых символов типа эмоджи, кавычек, пробелов и т.д

В результате работы рядом со скриптом появится папка с названием ключа. В этой папке будут лежать фото (имя = значение) которые удобно смотреть и сравнивать через FastStone Image Viewer
![изображение](https://user-images.githubusercontent.com/2606215/119796119-c3fd2b80-bee1-11eb-82c2-89048871156e.png)
# Пример 3
Так же можно тестить кастомные адреса и их значения

```python gcamconftester.py -c имя_конфига --custom номер -a адрес -v значения_через_двоеточие```

Пример:
```python gcamconftester.py -c "8.2riv.xml" --custom 2 -a 0de3694 -v 04008052:24008052:44008052```

Это запишет в User Defined Value 2 адрес 0DE3694 и переберет значения 24008052,04008052,44008052
![изображение](https://user-images.githubusercontent.com/2606215/119966201-bfa14300-bfb3-11eb-8374-89e200edc713.png)




# Баги / особенности
1) ~~Для нормальной работы в конфиге уже должен существовать необходимый ключ и в патчере для него должно быть выставлено любое значение~~ Должен быть включен соответствующий раздел патчера
2) ~~Точно так же и с кастомными значениями - оно должно быть включено и там должны быть введены какие-нибудь значения до запуска~~
3) ~~Автоматическое нажатие кнопок может не работать на телефонах у которых разрешение НЕ 1080р~~ вроде работает
4) Количество итоговых фото всегда будет количество_значений_для_теста+1
