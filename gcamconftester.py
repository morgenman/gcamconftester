from lxml import etree
import os, sys, math, logging
import numpy as np  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("gcam.log"),
        logging.StreamHandler()
    ]
)

def get_key_from_camera_preferences(config_key):
    """
    Ищет ключ в camera_preferences.xml чтобы по нему узнать массивы для entries и entryValues
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
    Выдает нужное количество значений из массива расположенных на равном промежутке
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
    Ищет и пишет в хмл нужное значений в нужный ключ 
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
    except IOError as e:
        logging.error("Не могу обработать {0} - {1}".format(config_name, e))

#def save_to_xml(config_to_save):

#def connect_with_adb():

if __name__ == "__main__":
    config_name = "8.2riv.xml"
    config_key = "lib_sharpness_key"
    logging.info("Буду подбирать значения ключа {0} для конфига {1}".format(config_key, config_name))
    entries, entryValues = get_key_from_camera_preferences(config_key)
    entries_hash = get_values_from_arrays(entries, entryValues)
    entries_hash = entries_hash[:-1] #убирает Off значение из списка
    entries_hash = get_number_of_items_from_array(entries_hash, 130)
    for entry in entries_hash:
        logging.info("Обрабатываю {0} = {1}".format(entry[0], entry[1]))
        find_and_write_to_xml(config_name, config_key, entry[1])
