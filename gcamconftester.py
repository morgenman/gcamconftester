from lxml import etree
import os, sys

def get_key_from_camera_preferences(config_key):
    """
    Ищу ключ в camera_preferences.xml чтобы по нему узнать массивы для entries и entryValues
    """
    try:
        tree = etree.parse("camera_preferences.xml")
        root = tree.getroot()
        search_string = ".//ListPreference[@android:key='"+ config_key + "']"
        key_element = root.find(search_string, root.nsmap)
    except IOError as e:
        print("Не могу обработать camera_preferences.xml - %sn" % e)
    
    return key_element

#def save_to_xml(config_to_save):

#def connect_with_adb():



if __name__ == "__main__":
    config_name = "8.2riv.xml"
    config_key = "lib_sharpness_key"
    print(get_key_from_camera_preferences(config_key))