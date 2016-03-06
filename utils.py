# -*- coding: utf-8 -*-


def colorize(char, bool):
    ''' colorize a character with blue or red depending on bool
    :param char: a character
    :param bool: Boolean
    :return: HTML font tag string
    '''
    if bool:
        return '<font color="blue">{}</font>'.format(char)
    else:
        return '<font color="red">{}</font>'.format(char)
