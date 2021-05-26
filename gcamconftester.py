from lxml import etree
import os, sys, math
import numpy as np
from itertools import accumulate

def get_key_from_camera_preferences(config_key):
    """
    Ищет ключ в camera_preferences.xml чтобы по нему узнать массивы для entries и entryValues
    """
    try:
        tree = etree.parse("camera_preferences.xml")
        root = tree.getroot()
        search_string = ".//ListPreference[@android:key='" + config_key + "']"
        key_element = root.find(search_string, root.nsmap)
    except IOError as e:
        print("Не могу обработать camera_preferences.xml - %sn" % e)
    
    entries = key_element.attrib.get('{http://schemas.android.com/apk/res/android}entries') #лол блять
    entryValues = key_element.attrib.get('{http://schemas.android.com/apk/res/android}entryValues')
    return entries, entryValues

def get_values_from_arrays(entries, entryValues):
    """
    Ищет значения в нормальном виде и в хексе в arrays.xml по ключам из entries и entryValues
    """
    try:
        tree = etree.parse("arrays.xml")
        root = tree.getroot()
        entries = entries[7:]
        entryValues = entryValues[7:]
        entries_search_string = ".//string-array[@name='" + entries + "']"
        entries_element = root.find(entries_search_string)
        entryValues_search_string = ".//string-array[@name='" + entryValues + "']"
        entryValues_element = root.find(entryValues_search_string)
    except IOError as e:
        print("Не могу обработать arrays.xml - %sn" % e)

    entries_array = []
    entryValues_array = []
    for element in entries_element:
        entries_array.append(element.text)
    
    for element in entryValues_element:
        entryValues_array.append(element.text)
    
    entries_hash = np.array(list(zip(entries_array,entryValues_array)))
    #print(entries_hash)
    return entries_hash

def get_number_of_items_from_array(entries_hash, div):
    """
    Выдает нужное количество значений из массива расположенных на равном промежутке
    """
    num = len(entries_hash)
    #div = 5
    entries_hash_count = [num // div + (1 if x < num % div else 0)  for x in range (div)]
    entries_hash_count = np.cumsum(entries_hash_count)
    entries_hash_count = np.insert(entries_hash_count, 0, 0)
    entries_hash = np.array(entries_hash)
    return entries_hash[entries_hash_count-1]
#def save_to_xml(config_to_save):

#def connect_with_adb():



if __name__ == "__main__":
    config_name = "8.2riv.xml"
    config_key = "lib_grid_key"
    entries, entryValues = get_key_from_camera_preferences(config_key)
    entries_hash = get_values_from_arrays(entries, entryValues)
    entries_hash = entries_hash[:-1] #убирает Off значение из списка
    print(get_number_of_items_from_array(entries_hash, 5))
    