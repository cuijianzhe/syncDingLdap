import pypinyin
def pinyin_transfer(name=None):
    pinyin_name = ''.join(pypinyin.lazy_pinyin(name))
    return pinyin_name