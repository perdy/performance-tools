# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from abc import ABCMeta
import csv

from performance_tools.exceptions import ProgressBarException
from performance_tools.utils.progress_bar import create_progress_bar


class BaseURLFlowBackend(object):
    """Collect URL flow from backend. URL Flow: Referrer, Request, Time.
    It's necessary to implement extract_url_from_result and __iter__ methods.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._total_hits = 0

    def extract_url_from_result(self, result, regex=None):
        """Extract origin url and destination url for each entry in result and construct a list with them.

        :param result: results obtained from backend in each iteration.
        :type result: object
        :param regex: Regular expression to normalize id's in URL.
        :type regex: re
        :return: List of origin urls and destination urls.
        :rtype: list
        """
        raise NotImplementedError

    def to_csv(self, filename, regex=None, verbose=2):
        """Save results as a CSV file.

        :param filename: CSV output file.
        :type filename: str
        :raise: ValueError if not found any result.
        """
        total_hits = 0

        if verbose == 2:
            try:
                progress = create_progress_bar(total_hits, 'Extract URLs', 'url')
            except ProgressBarException:
                verbose = 1

        try:
            with open(filename, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['Referrer', 'Request', 'Time'])
                count = 0
                for result in self:
                    rows = self.extract_url_from_result(result, regex)
                    writer.writerows(rows)

                    count += len(rows)
                    if verbose == 2:
                        if not total_hits:
                            progress.maxval = self._total_hits
                        progress.update(count)
                    elif verbose == 1:
                        print "{:d}/{:d} ({:d}%)".format(count, self._total_hits, count * 100 / self._total_hits)
        except (KeyError, ZeroDivisionError):
            raise ValueError("Search doesn't return any result")

    def __iter__(self):
        """Iterate over each result.
        """
        raise NotImplementedError
