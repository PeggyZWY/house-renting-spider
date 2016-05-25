# coding=utf-8
import ConfigParser


class Config(object):
    def __init__(self, config_file_name):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(config_file_name) # read(filename) 直接读取ini文件内容

        key_list = self.cf.get('common', 'key_search_word_list').split(',') # get(section,option) 得到section中option的值，返回为string类型
        custom_black_list = self.cf.get('common', 'custom_black_list').split(',')
        self.key_search_word_list = [key.strip() for key in key_list]
        self.custom_black_list = [key.strip() for key in custom_black_list]
        # 上面两行是去掉key_list和custom_black_list中防止用户输入有空格啊换行什么的，只留下字
        self.start_time = self.cf.get('common', 'start_time')

        self.douban_cookie = self.cf.get('douban', 'douban_cookie')
        self.douban_sleep_time = self.cf.getfloat('douban', 'douban_sleep_time')

"""

python-ConfigParser模块【读写配置文件】

1.读取配置文件
-read(filename) 直接读取ini文件内容
-sections() 得到所有的section，并以列表的形式返回
-options(section) 得到该section的所有option
-items(section) 得到该section的所有键值对
-get(section,option) 得到section中option的值，返回为string类型
-getint(section,option) 得到section中option的值，返回为int类型

2.写入配置文件
-add_section(section) 添加一个新的section
-set( section, option, value) 对section中的option进行设置

"""