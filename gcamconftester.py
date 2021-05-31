from lxml import etree
import os, sys, math, logging, subprocess, re, glob, time, argparse
import numpy as np  
from sys import argv
from pathlib import Path
from shutil import copyfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("gcam.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
camera_folder = '/storage/self/primary/DCIM/Camera' #папка в которой сохраняются фото
config_folder = '/storage/self/primary/ConfigsSettings8.2' #папка куда закидывать конфиги
gcam_package = 'com.google.android.GoogleCameraEng'
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def msg(name=None):
    return '''
    Использование:
    python gcamconftester.py [-h] -c конфиг.xml [-k какой ключ перебирать] [-n количество значений для теста]
    python gcamconftester.py [-h] -c конфиг.xml [-custom номер кастомного адреса] [-a адрес] [-v значения через двоеточие]
    python gcamconftester.py [-h] -c конфиг.xml [-p название параметра в конфиге] [-l название модуля камеры] [-n количество значений для теста]

    Пример:
    python gcamconftester.py -c "8.2riv.xml" -k lib_sharpness_key -n 3
    python gcamconftester.py -c "8.2riv.xml" --custom 2 -a 0de3694 -v 04008052:24008052:44008052
    python gcamconftester.py -c "8.2riv.xml" -p "Sharp Depth 2" -l "LDR"
        '''
def adb_command(command):
    """
    Вызывает адб из папки adb/adb и выполняет command через него
    """
    try:
        response = subprocess.check_output(os.path.join(__location__, "adb/adb") + " " + command, timeout=5)
    except subprocess.CalledProcessError:
        logging.error('Произошла ошибка adb. Проверьте, подключен ли телефон.')
        exit()
        response = 'Ошибка!'
    except subprocess.TimeoutExpired:
        logging.error('Процесс adb превысил время ожидания и был закрыт. Попробуем еще раз')
        response = adb_command(command)
    return response

def get_screen_size():
    res = adb_command("shell wm size")
    size = re.findall(r"\d{3,4}", str(res))
    return size

def tap_shutter():
    #shutter 550 1930
    #config 730 1930
    #ok 910 1384
    adb_command('shell input keyevent 25')
    logging.info("Жамкаю на кнопку спуска")

def gcam_open_config():
    logging.info("Восстанавливаю конфиг в гкаме")
    scr_size = get_screen_size()
    w_conf = int(348 / 1080 * int(scr_size[0]))
    h_conf = int(1903 / 2400 * int(scr_size[1]))
    logging.info("Даблтап в {0} {1} для открытия меню конфигов".format(w_conf, h_conf))
    adb_command(f"shell input tap {w_conf} {h_conf} & sleep 0.1; input tap {w_conf} {h_conf}")
    #adb_command('shell input tap 730 1930 & sleep 0.1; input tap 730 1930')
    time.sleep(1)
    w_ok = int(881 / 1080 * int(scr_size[0]))
    h_ok = int(1381 / 2400 * int(scr_size[1]))
    logging.info("Жму в точку {0} {1} для восстановления конфига".format(w_ok, h_ok))
    adb_command(f"shell input tap {w_ok} {h_ok}")

def gcam_push_config(config_name):
    adb_command('root')
    logging.info("Закидываю конфиг")
    adb_command(f'push {config_name} /data/data/{gcam_package}/shared_prefs/{gcam_package}_preferences.xml')
    logging.info("Перезапускаю гкам {0}".format(gcam_package))
    adb_command(f'shell am force-stop {gcam_package}')
    adb_command(f'shell am start -n {gcam_package}/com.google.android.apps.camera.legacy.app.activity.main.CameraActivity')
    time.sleep(1)

def push_config(config_name):
    """
    Пушит конфиг config_name по адб в папку с конфигами
    """
    adb_command(f'push {config_name} {config_folder}')
    logging.info("Закинул конфиг {0} в {1}".format(config_name, config_folder))

# pull_last_photo(get_last_modified_file(camera_folder))
def pull_last_photo(filename, config_key, value):
    """
    Вытаскивает файл по адб и сохраняет его как key_value.jpg'
    """
    Path("{0}".format(config_key)).mkdir(parents=True, exist_ok=True)
    logging.info("Выгружаю фото с телефона в папку {0}".format(config_key))
    adb_command(f'pull {filename} {config_key}\{value}.jpg')

def get_last_modified_file(folder, local=False):
    """
    Возвращает название последнего тронутого файла в folder
    """
    if local:
        list_of_files = glob.glob(folder) 
        latest_file = max(list_of_files, key=os.path.getctime)
        return folder + "/" + latest_file
    res = str(adb_command(f'shell "ls -lt {folder} | head"'))
    res2 = [r for r in res.split(r'\r\n')]
    res3 = res2[1].split()[-1]
    return folder + "/" + res3

def wait_for_new_photo(folder, local=False):
    """
    Ждет появление нового фото в папке folder и если оно появилось то возращает имя
    """
    logging.info("Жду появления нового фото")
    was = get_last_modified_file(folder, local)
    for i in range(20):
        now = get_last_modified_file(folder, local)
        if now != was:
            logging.info("Новое фото найдено: {0}".format(now))
            logging.info('Жду окончания обработки фото...')
            for j in range(10):
                was = now
                now = get_last_modified_file(folder, local)
                if now != was:
                    return now
                time.sleep(1)

            return now
        else:
            was = now
            time.sleep(1)
    logging.error("Не могу найти новое фото...Скорее всего гкам вылетел :(")
    tap_shutter()

def get_key_from_camera_preferences(config_key):
    """
    Ищет ключ camera_key в camera_preferences.xml чтобы по нему узнать массивы для entries и entryValues
    """
    try:
        tree = etree.parse("camera_preferences.xml")
        logging.info("Нашел camera_preferences.xml")
        root = tree.getroot()
        search_string = ".//ListPreference[@android:key='" + config_key + "']"
        key_element = root.find(search_string, root.nsmap)
        logging.info("Нашел нужный ключ - {0}".format(config_key))
    except IOError as e:
        logging.error("Не могу обработать camera_preferences.xml - %sn" % e)
    
    entries = key_element.attrib.get('{http://schemas.android.com/apk/res/android}entries') #лол блять
    entryValues = key_element.attrib.get('{http://schemas.android.com/apk/res/android}entryValues')
    logging.info("Нашел массивы значений для ключа {0}: {1} и {2}".format(config_key, entries[7:], entryValues[7:]))
    return entries, entryValues

def get_values_from_arrays(entries, entryValues):
    """
    Ищет значения в нормальном виде и в хексе в arrays.xml по ключам из entries и entryValues
    """
    try:
        tree = etree.parse("arrays.xml")
        logging.info("Нашел arrays.xml")
        root = tree.getroot()
        entries = entries[7:]
        entryValues = entryValues[7:]
        entries_search_string = ".//string-array[@name='" + entries + "']"
        entries_element = root.find(entries_search_string)
        entryValues_search_string = ".//string-array[@name='" + entryValues + "']"
        entryValues_element = root.find(entryValues_search_string)
    except IOError as e:
        logging.error("Не могу обработать arrays.xml - %sn" % e)

    entries_array = [element.text for element in entries_element]
    entryValues_array = [element.text for element in entryValues_element]
    
    entries_hash = np.array(list(zip(entries_array,entryValues_array)))
    logging.info("Нашел список значений для ключа: от {0} ({1}) до {2} ({3})".format(entries_array[0], entryValues_array[0], entries_array[-2], entryValues_array[-2]))
    return entries_hash

def get_number_of_items_from_array(entries_hash, div):
    """
    Делит массив entries_hash на div значений и возвращает их
    """
    num = len(entries_hash)
    if div >= num:
        logging.warning("В этом массиве меньше {0} значений. Просто возьму все значения".format(div)) #TODO: переделай дебил
        div = num
    else:
        logging.info("Делю весь массив из {0} значений на {1} равных промежутков".format(num, div))
    entries_hash_count = [num // div + (1 if x < num % div else 0)  for x in range (div)]
    entries_hash_count = np.cumsum(entries_hash_count)
    entries_hash_count = np.insert(entries_hash_count, 0, 1)
    logging.info("Магические числа {0}".format(entries_hash_count-1))
    entries_hash = np.array(entries_hash)
    return entries_hash[entries_hash_count-1]

def find_and_write_to_xml(config_name, config_key, value):
    """
    Ищет ключ config_key в config_name и меняет его значение на value
    """
    try:
        tree = etree.parse(config_name)
        root = tree.getroot()
        config_search_string = ".//string[@name='" + config_key + "']"
        config_element = root.find(config_search_string)
        if config_element.text == value:
            logging.info("Текущее значение для {0} совпадает с нужным {1}".format(config_key, config_element.text))
            return
        logging.info("Текущее значение для {0} = {1}. Меняю на {2}".format(config_key, config_element.text, value))
        if config_element is not None:
            config_element.text = value
            etree.ElementTree(root).write(config_name, pretty_print=True)
        else:
            logging.error("В конфиге нет записи с этим ключем. Потом исправлю эту ошибку и сделаю добавление ключа вместо замены") #TODO: исправить
    except IOError as e:
        logging.error("Не могу обработать {0} - {1}".format(config_name, e))

def get_camera_id_from_input(config_name, camera_name):
    try:
        tree = etree.parse(config_name)
        root = tree.getroot()
        camera_ids = [1, 2, 3, 4, 5, "ldr"]
        for idx, camera in enumerate(camera_ids):
            aux_search_string = ".//string[@name='pref_manual_aux_name_" + str(camera) + "_key']"
            aux_element = root.find(aux_search_string)
            if aux_element.text == camera_name:
                return idx
    except IOError as e:
        logging.error("Не могу найти модуль с именем {0} в конфиге {1} - {2}".format(camera_name, config_name, e))

def get_key_by_camera_and_name(camera_id, key_name):
    """
    Ищет ключ в camera_preferences.xml по camera_id и key_name
    """
    #patcher_prefixes = ["", "tele", "wide", "n4", "n5", "ldr"]
    try:
        tree = etree.parse("camera_preferences.xml")
        logging.info("Ищу название ключа патчера для {0} (модуль {1})".format(key_name, camera_id))
        root = tree.getroot()
        search_string = ".//ListPreference[@android:title='" + key_name + "']"
        key_element = root.findall(search_string, root.nsmap)
        try:
            key = key_element[camera_id].attrib.get('{http://schemas.android.com/apk/res/android}key')
            return key
        except IndexError as e:
            logging.error("Не могу найти ключ - {0}".format(e))
            exit()
        except TypeError as e:
            logging.error("Не могу найти модуль камеры - {0}".format(e))
            exit()
        #logging.info("Нашел нужный ключ для {0} - {1}".format(key_name, key_element))
    except IOError as e:
        logging.error("Не могу обработать camera_preferences.xml - %sn" % e)

if __name__ == "__main__":
    #pref_aux_key - ид камеры 0-5 на какую переключится
    #pref_manual_aux_name_1-6_key - ручное название камеры типа Макро
    # <set name="pref_list_camera_key">
    #     <string>0</string>
    #     <string>22</string>
    #     <string>1</string>
    #     <string>21</string>
    # </set>
    #logging.info("Разрешение экрана - {0}".format(get_screen_size()))
    parser = argparse.ArgumentParser(usage=msg())
    group = parser.add_mutually_exclusive_group(required=True)
    parser._optionals.title = 'Список аргументов'
    parser._actions[0].help='Показать информацию для помощи'
    parser.add_argument("-c", "--config", required=True, help="Имя конфига")
    group.add_argument("-k", "--key", required=False, help="Название ключа для перебора настроек (Например: \"lib_sharpness_key\")")
    parser.add_argument("-l", "--lens", required=False, help="Имя модуля камеры на котором тестировать патчер (Например: \"LDR\") (по умолчанию: 1х)")
    group.add_argument("-p", "--parameter", required=False, help="Название параметра в патчере для которого проводить тесты (Например: \"Sharp Depth 2\")")
    parser.add_argument("-n", "--num", required=False, help="Количество значений для перебора (по умолчанию: 5)")
    group.add_argument("-custom", "--custom", required=False, help="Номер кастомного значения в патчере (от 1 до 12) в который вносить данные")
    parser.add_argument("-a", "--address", required=False, help="Адрес кастомного значения")
    parser.add_argument("-v", "--values", required=False, help="Кастомные значения через двоеточие")
    args = parser.parse_args()
    if args.custom and (args.address is None or args.values is None):
        parser.error("Для работы --custom нужны --address адрес и --values значения")
    if args.custom:
        config_name = args.config
        custom_addr_num = "lib_user_addr_" + args.custom
        custom_value_num = "lib_user_value_" + args.custom
        custom_value_key = "lib_user_key_" + args.custom
        custom_addr = args.address
        custom_values = args.values
        custom_values = custom_values.split(":")
        new_config_name = config_name + "_test.xml"
        logging.info("Делаю копию конфига {0}".format(new_config_name))
        copyfile(config_name, new_config_name)
        config_name = new_config_name
        find_and_write_to_xml(config_name, custom_value_key, "1") # Пишу lib_user_key_ для включения кастомного значения
        # try:
        #     find_and_write_to_xml(config_name, "pref_spiner_key", "6") #меняю стиль окна конфигов на 7 на всякий случай
        # except AttributeError as e:
        #     logging.error("Не могу найти ключ со стилем окна конфигов - {0}".format(e))
        for entry in custom_values:
            logging.info("Обрабатываю {0} = {1}".format(custom_addr_num, custom_addr))
            find_and_write_to_xml(config_name, custom_addr_num, custom_addr)
            logging.info("Обрабатываю {0} = {1}".format(custom_value_num, entry))
            find_and_write_to_xml(config_name, custom_value_num, entry)
            #push_config(config_name)
            #gcam_open_config()
            gcam_push_config(config_name)
            time.sleep(2)
            tap_shutter()
            pull_last_photo(wait_for_new_photo(camera_folder), custom_addr, entry)
            time.sleep(1)
        exit()
    
    config_name = args.config
    config_key = args.key
    num_values_to_test = 5 if not args.num else int(args.num)
    
    new_config_name = config_name + "_test.xml"
    logging.info("Делаю копию конфига {0}".format(new_config_name))
    copyfile(config_name, new_config_name)
    config_name = new_config_name
    if args.parameter:
        cam_id = get_camera_id_from_input(args.config, args.lens) if args.lens else 0
        find_and_write_to_xml(config_name, "pref_aux_key", str(cam_id))
        config_key = get_key_by_camera_and_name(cam_id, args.parameter)
    logging.info("Буду подбирать значения ключа {0} для конфига {1}".format(config_key, config_name))
    entries, entryValues = get_key_from_camera_preferences(config_key)
    entries_hash = get_values_from_arrays(entries, entryValues)
    entries_hash = entries_hash[:-1] #убирает Off значение из списка
    entries_hash = get_number_of_items_from_array(entries_hash, num_values_to_test)
    for entry in entries_hash:
        find_and_write_to_xml(config_name, config_key, entry[1]) 
        # try:
        #     find_and_write_to_xml(config_name, "pref_spiner_key", "6") #меняю стиль окна конфигов на 7 на всякий случай
        # except AttributeError as e:
        #     logging.error("Не могу найти ключ со стилем окна конфигов - {0}".format(e))    
        #push_config(config_name)
        #gcam_open_config()
        gcam_push_config(config_name)
        time.sleep(2)
        tap_shutter()
        #pull_last_photo(get_last_modified_file(camera_folder), config_key, entry[0])
        pull_last_photo(wait_for_new_photo(camera_folder), config_key, entry[0])
        time.sleep(1)