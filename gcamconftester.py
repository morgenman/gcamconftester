from lxml import etree
import os, sys, math, logging, subprocess, re, glob, time
import numpy as np  
from sys import argv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("gcam.log"),
        logging.StreamHandler()
    ]
)
camera_folder = '/storage/self/primary/DCIM/Camera' #папка в которой сохраняются фото
config_folder = '/storage/self/primary/ConfigsSettings8.2' #папка куда закидывать конфиги
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

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
    adb_command('shell input tap 730 1930 & sleep 0.1; input tap 730 1930')
    time.sleep(1)
    adb_command('shell input tap 910 1384')

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
    logging.info("Выгружаю фото с телефона")
    adb_command(f'pull {filename} {config_key}_{value}.jpg')

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
    logging.error("Не могу найти новое фото...")
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

    entries_array = []
    entryValues_array = []
    for element in entries_element:
        entries_array.append(element.text)
    
    for element in entryValues_element:
        entryValues_array.append(element.text)
    
    entries_hash = np.array(list(zip(entries_array,entryValues_array)))
    logging.info("Нашел список значений для ключа: от {0} ({1}) до {2} ({3})".format(entries_array[0], entryValues_array[0], entries_array[-2], entryValues_array[-2]))
    return entries_hash

def get_number_of_items_from_array(entries_hash, div):
    """
    Делит массив entries_hash на div значений и возвращает их
    """
    num = len(entries_hash)
    if div >= num:
        logging.warning("В этом массиве меньше {0} значений. Просто возьму все значения".format(div))
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
        logging.info("Текущее значение в конфиге - {0}. Меняю на {1}".format(config_element.text, value))
        if config_element is not None:
            config_element.text = value
            etree.ElementTree(root).write(config_name, pretty_print=True)
        else:
            logging.error("В конфиге нет записи с этим ключем. Потом исправлю эту ошибку и сделаю добавление ключа вместо замены") #TODO: исправить
    except IOError as e:
        logging.error("Не могу обработать {0} - {1}".format(config_name, e))

if __name__ == "__main__":
    if len(argv) <2:
        logging.error("Использвание: python gcamconftester.py \"имя_конфига\" \"название_ключа_для_теста\"")
        config_name = "8.2riv.xml"
        config_key = "lib_sharpness_key"
    else:
        config_name = argv[1]
        config_key = argv[2]
    logging.info("Буду подбирать значения ключа {0} для конфига {1}".format(config_key, config_name))
    entries, entryValues = get_key_from_camera_preferences(config_key)
    entries_hash = get_values_from_arrays(entries, entryValues)
    entries_hash = entries_hash[:-1] #убирает Off значение из списка
    entries_hash = get_number_of_items_from_array(entries_hash, 5)
    for entry in entries_hash:
        logging.info("Обрабатываю {0} = {1}".format(entry[0], entry[1]))
        find_and_write_to_xml(config_name, config_key, entry[1])        
        push_config(config_name)
        gcam_open_config()
        time.sleep(2)
        tap_shutter()
        #pull_last_photo(get_last_modified_file(camera_folder), config_key, entry[0])
        pull_last_photo(wait_for_new_photo(camera_folder), config_key, entry[0])
        time.sleep(1)