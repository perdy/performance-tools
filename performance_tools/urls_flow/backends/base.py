# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from abc import ABCMeta
import csv

from performance_tools.exceptions import ProgressBarException, ElasticsearchException
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
        progress = None

        try:
            with open(filename, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['Referrer', 'Request', 'Time'])
                count = 0
                for result in self:
                    # Create progress bar or down verbose level
                    if verbose == 2 and progress is None:
                        try:
                            progress = create_progress_bar(self._total_hits, 'Extract URLs', 'url')
                        except ProgressBarException:
                            verbose = 1

                    # Write results to csv
                    rows = self.extract_url_from_result(result, regex)
                    writer.writerows(rows)

                    # Update progress
                    count += len(rows)
                    if verbose == 2:
                        progress.update(count if count < self._total_hits else self._total_hits)
                    elif verbose == 1:
                        print "{:d}/{:d} ({:d}%)".format(count, self._total_hits, count * 100 / self._total_hits)
        except ZeroDivisionError:
            raise ElasticsearchException("Search doesn't return any result")
        except KeyError:
            raise ElasticsearchException("Invalid result")

    def __iter__(self):
        """Iterate over each result.
        """
        raise NotImplementedError
