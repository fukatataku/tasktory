#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import configparser

CONFIG = "test.conf"

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(CONFIG)
    section = config['TEST']
    num = int(section['NUM'])
    print(num)

    config['TEST']['NUM'] = str(num + 1)
    with open(CONFIG, 'w') as f:
        config.write(f)
    pass
