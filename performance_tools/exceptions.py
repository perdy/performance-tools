# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class PerformanceException(Exception):
    pass


class ProgressBarException(PerformanceException):
    pass


class ElasticsearchException(PerformanceException):
    pass