from lxml import etree
import os, sys
import numpy as np

def get_key_from_camera_preferences(config_key):
    """
    Ищу ключ в camera_preferences.xml чтобы по нему узнать массивы для entries и entryValues
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
    Ищу значения в нормальном виде и в хексе в arrays.xml по ключам из entries и entryValues
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
    print(entries_hash)
    return entries_hash
#def save_to_xml(config_to_save):

#def connect_with_adb():



if __name__ == "__main__":
    config_name = "8.2riv.xml"
    config_key = "lib_sharpness_key"
    entries, entryValues = get_key_from_camera_preferences(config_key)
    entries_hash = get_values_from_arrays(entries, entryValues)
    print(entries_hash[1][0], entries_hash[1][1])