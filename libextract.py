import struct, binascii, mmap
import numpy as np

def get_data_offset(tuned_file_name):
    """
    Возвращает смещение для начала блока data в файле tuned_file_name
    """
    if "tuned" not in tuned_file_name:
        raise NameError("Это точно tuned либа?")
    try:
        with open(tuned_file_name, "rb") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) 
            mm.seek(192, 0) #оффсет даты всегда будет через C0 (192) от начала файла
            return int.from_bytes(mm.read(4), "little")
    except Exception as e:
        print(e)
        exit()

def get_offsets_and_lengths(tuned_file_name, name):
    """
    Возвращает массив смещений и длинн для name из tuned либы
    """
    offsets = []
    lengths = []
    if "tuned" not in tuned_file_name:
        raise NameError("Это точно tuned либа?")
    try:
        with open(tuned_file_name, "rb") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) 
            index = mm.find(name.encode(), 0)
            while index >= 0:
                index = index + 48 #оффсет будет через 30 (48) после названия
                mm.seek(index, 0) 
                offsets.append(int.from_bytes(mm.read(4), "little")) #перевод 4 байтов длины в инт
                index = index + 8 #длина будет через 4 байта после оффсета
                mm.seek(index, 0) 
                length = mm.read(2).hex() #длина всего 2 байта
                length = length[2:4] + length[0:2] #переворот длины в хексе с предподвыподвертом
                lengths.append(int(length, 16)) #перевод в инт из хекса
                index = mm.find(name.encode(), index) #дальше пусть ищет по циклу
    except Exception as e:
        print(e)
        exit()
    return list(zip(offsets, lengths))
    
def extract_data_by_offsets(tuned_file_name, data_offset, offsets):
    """
    Возвращает массив hex значений из tuned лежащий по offsets
    """
    hexdata = []
    if "tuned" not in tuned_file_name:
        raise NameError("Это точно tuned либа?")
    try:
        with open(tuned_file_name, "rb") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) 
            for offset in offsets:
                mm.seek(data_offset, 0) #перехожу на начало блока дата
                mm.seek(offset[0], 1)
                hexdata.append(mm.read(offset[1]).hex())
    except Exception as e:
        print(e)
        exit()
    return hexdata

def decode_awb(hexdata):
    """
    Переводит hexdata в пары авб
    """
    if len(hexdata) % 4 == 0:
        raise ValueError("Что-то пошло не так")
    n = 8 #8 символов = 4 байта
    hexdata = [hexdata[0][i:i+n] for i in range(0, len(hexdata[0]), n)] #деление всей строки на список значений по 4 байта
    filter_hex = ["01000000", "02000000", "00000000"] #фильтр мусора
    hexdata = [i for i in hexdata if not any([e for e in filter_hex if e in i])] #удаление мусора по фильтру
    awb_float = [struct.unpack('<f', binascii.unhexlify(value)) for value in hexdata] #перевод из хекса во флоат
    awb_float = [ '%.6f' % elem for elem in awb_float] #оставляю 6 знаков после запятой
    #awb_float = list(zip(awb_float[0::2], awb_float[1::2])) #хз надо ли
    return awb_float


def decode_cct(hexdata):
    """
    Переводит hexdata в матрицы сст по 9 значений
    """
    cct_float = []
    if len(hexdata) % 4 == 0:
        raise ValueError("Что-то пошло не так")
    n = 8 #8 символов = 4 байта
    for cct_hex in hexdata:
        cct_hex = [cct_hex[i:i+n] for i in range(0, len(cct_hex), n)] #деление всей строки на список значений по 4 байта
        filter_hex = ["01000000", "02000000", "00000000"] #фильтр мусора
        cct_hex = [i for i in cct_hex if not any([e for e in filter_hex if e in i])]
        cct_hex = [struct.unpack('<f', binascii.unhexlify(value)) for value in cct_hex]
        cct_hex = [ '%.5f' % elem for elem in cct_hex]
        cct_start = cct_hex[0::11] #короче в строке нулевое значение и каждое одиннадцатое это начало ренжа температуры
        cct_end = cct_hex[1::11] #точно так же первое значение и через каждые 11 значений это конец ренжа температуры
        cct_values = [x for x in cct_hex if x not in cct_start] 
        cct_values = [x for x in cct_values if x not in cct_end] #убираю ренж температур потому что не нужны
        cct_values = list(filter(None, cct_values)) #пустые значения
        cct_values = [x for x in cct_values if x] #пустые значения
        if len(cct_values) % 9 == 0 and cct_values != []: #еще раз пустые значения потому что пиздец
            cct_float += zip(*[iter(cct_values)]*9) #каждые 9 значений это одна матрица
    return cct_float

if __name__ == "__main__":
    tuned_file_name = "com.qti.tuned.j20c_ofilm_imx682_wide_global.bin"
    data_offset = get_data_offset(tuned_file_name)
    cc13_offsets = get_offsets_and_lengths(tuned_file_name, "mod_cc13_cct_data")
    cc12_offsets = get_offsets_and_lengths(tuned_file_name, "mod_cc12_cct_data")
    refptv1_offset = get_offsets_and_lengths(tuned_file_name, "refPtV1")
    hex_awb = extract_data_by_offsets(tuned_file_name, data_offset, refptv1_offset)
    #print(decode_awb(hex_awb))
    cct13 = decode_cct(extract_data_by_offsets(tuned_file_name, data_offset, cc13_offsets))
    cct12 = decode_cct(extract_data_by_offsets(tuned_file_name, data_offset, cc12_offsets))
    cct = cct13 + cct12
    cct = list(dict.fromkeys(cct)) #убирает дубликаты
    print(cct)