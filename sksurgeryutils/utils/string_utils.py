# coding=utf-8

"""
Various string parsing utils.
"""

def split_string(param_string):
    """
    Splits a comma separated list of rx,ry,rz,tx,ty,tz to a list of floats.
    :param param_string: string
    :return: list of float
    """
    result = [0, 0, 0, 0, 0, 0]
    if param_string is not None:
        split = param_string.split(',')
        if len(split) != 6:
            raise ValueError('List is wrong length:' + str(split))
        for i in range(6):
            result[i] = float(split[i])
    return result
