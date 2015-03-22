# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from abc import ABCMeta
import csv


class BaseURLFlowBackend(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._total_hits = 0

    def extract_url_from_result(self, result):
        """Extract origin url and destination url for each entry in result and construct a list with them.

        :param result: results obtained from backend in each iteration.
        :type result: object
        :return: List of origin urls and destination urls.
        :rtype: list
        """
        raise NotImplementedError

    def to_csv(self, filename):
        """Save results as a CSV file.

        :param filename: CSV output file.
        :type filename: str
        :raise: ValueError if not found any result.
        """
        try:
            with open(filename, 'w') as csvfile:
                writer = csv.writer(csvfile)
                count = 0
                for result in self:
                    rows = self.extract_url_from_result(result)
                    writer.writerows(rows)

                    count += len(rows)
                    print "{:d}/{:d} ({:d}%)".format(count, self._total_hits, count * 100 / self._total_hits)
        except (KeyError, ZeroDivisionError):
            raise ValueError("Search doesn't return any result")

    def __iter__(self):
        """Iterate over each result.
        """
        raise NotImplementedError
