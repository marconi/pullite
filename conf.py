# -*- coding: utf-8 -*-

import os


class Config(object):
    """ Holds download settings and downloads dir creation. """

    download_path = os.path.join(os.path.dirname(__file__), 'downloads')

    def __new__(cls, *args, **kwargs):
        # don't allow config object creation
        raise ValueError

    @classmethod
    def get_config(cls):
        # create download path if it doesn't exist
        if not os.path.exists(Config.download_path):
            os.mkdir(Config.download_path)
        return Config
