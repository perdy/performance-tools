"""Module that provides some tools to compare web applications performance based on url's request time.
"""
import pandas as pd
import numpy as np
import os
from collections import OrderedDict
from performance_tools.urls_flow.backends import ElasticURLFlowBackend


class RequestAnalyzer(object):
    """Class that gathers and analyze a web application based on his url's request time.
    """

    def __init__(self, input_file, noise=0.1):
        """RequestAnalysis init method.

        :param input_file: Input CSV file.
        :type input_file: str
        :param noise: Percentage of data that will be considered noise (0-1).
        :type noise: float
        """
        self._noise = noise
        self._lower_quantile = self._noise / 2
        self._upper_quantile = 1 - (self._noise / 2)
        self._data = pd.read_csv(input_file)

        self._functions = OrderedDict((
            ('Count By Week', len),
            ('Count By Day', lambda x: len(x) / 5),
            ('Mean', np.mean),
            ('Std', np.std),
            ('Max', np.max),
            ('Min', np.min),
            ('Sum', np.sum),
            ('Median', np.median),
        ))

    @classmethod
    def from_elasticsearch(cls, output_file, host, port, query, date_from, date_to, size=50, regex=None):
        """Gather all data from Elasticsearch source.

        :param output_file: Output csv file for gathered data.
        :type output_file: str
        :param host: Elasticsearch host.
        :type host: str
        :param port: Elasticsearch port.
        :type port: int
        :param query: Elastisearch query to be executed.
        :type query: str
        :param date_from: Query initial date.
        :type date_from: str
        :param date_to: Query end date.
        :type date_to: str
        :param size: Query block size.
        :type size: int
        :param regex: Regular expression to parse URLs gathered.
        :type regex: re
        :return: Analysis object constructed.
        :rtype: RequestAnalysis
        """
        output_file_path = os.path.realpath(os.path.join(os.path.curdir, output_file))
        es = ElasticURLFlowBackend(host=host, port=port, query=query, date_from=date_from, date_to=date_to, size=size)
        es.to_csv(output_file_path, regex=regex, verbose=2)
        return cls(output_file_path)

    @property
    def data(self):
        """Property to wrap data attribute.
        """
        return self._data

    def number_of_requests(self):
        """Gets the number of requests.

        :return: Number of requests.
        :rtype: int
        """
        return self._data['Request'].count()

    def time_stats(self):
        """Calculate global time stats: sum, mean, standard deviation, min and max.

        :return: Time stats.
        :rtype: pandas.DataFrame
        """
        df_without_noise = self._data[self._data.Time <= self._data.Time.quantile(self._upper_quantile)]
        df_without_noise = df_without_noise[df_without_noise.Time >= self._data.Time.quantile(self._lower_quantile)]
        df_without_noise.reset_index()

        stats = {
            'Sum': df_without_noise.Time.sum(),
            'Mean': df_without_noise.Time.mean(),
            'Std': df_without_noise.Time.std(),
            'Min': df_without_noise.Time.min(),
            'Max': df_without_noise.Time.max(),
        }

        return pd.DataFrame(stats.values(), index=stats.keys(), columns=['Time'])

    def _get_stats(self, df):
        """Auxiliary function to extract relevant stats from analysis data.

        :param df: DataFrame.
        :type df: pandas.DataFrame
        :return: Relevant stats calculated.
        :rtype: pandas.Series
        """
        df = df[df.Time >= df.Time.quantile(self._lower_quantile)]
        df = df[df.Time <= df.Time.quantile(self._upper_quantile)]
        values = []
        index = []
        for i, f in self._functions.items():
            values.append(f(df.Time))
            index.append(i)
        return pd.Series(values, index=index)

    def stats_by_request(self):
        """Extract relevant stats grouped by request.

        :return: Stats.
        :rtype: pandas.GroupedDataFrame
        """
        return self._data.groupby('Request').apply(self._get_stats)

    def stats_by_request_and_referrer(self):
        """Extract relevant stats grouped by request and referrer.

        :return: Stats.
        :rtype: pandas.GroupedDataFrame
        """
        return self._data.groupby(['Request', 'Referrer']).apply(self._get_stats)


class RequestComparator(object):
    """Class that uses different analyzers to compare results.
    """

    def __init__(self, *analyzers):
        """RequestComparator init method.

        :param analyzers: Analyzers contained in the comparator.
        :type analyzers: list
        """
        if not analyzers:
            analyzers = []

        self._analyzers = analyzers

    @property
    def analyzers(self):
        return self._analyzers

    @analyzers.deleter
    def analyzers(self):
        del self._analyzers

    def compare_requests(self, old=None, new=None, indexes=None):
        """Compare requests stats of two or more analyzers.

        :param old: Index of the analyzer that represents old data.
        :type old: int
        :param new: Index of the analyzer that represents new data.
        :type new: int
        :param indexes: Indexes of analyzers to compare.
        :type indexes: iter
        :return: DataFrame with the comparison.
        :rtype: pandas.DataFrame
        """
        if old is not None and new is not None:
            old_analyzer = self._analyzers[old]
            new_analyzer = self._analyzers[new]
            comparison = self._compare_two_requests(old_analyzer, new_analyzer)
        elif indexes:
            analyzers = [a for (i, a) in enumerate(self._analyzers) if i in indexes]
            comparison = self._compare_more_than_two_requests(analyzers)
        else:
            raise TypeError("compare_requests takes old and new, or indexes arguments")

        return comparison

    def _compare_two_requests(self, old, new):
        """Compare all requests stats from two analyzers.

        :param old: Analyzer that represents old data.
        :type old: RequestAnalyzer
        :param new: Analyzer that represents new data.
        :type new: RequestAnalyzer
        :return: Comparison.
        :rtype: pandas.DataFrame
        """
        # Prepare series for merging
        old_series = old.stats_by_request()['Mean'].reset_index()
        new_series = new.stats_by_request()['Mean'].reset_index()

        # Merge
        merged = pd.merge(old_series, new_series, on='Request', how='outer').set_index(['Request'])
        merged.index.name = None
        merged.columns = ['Old', 'New']

        # Add differences
        merged['Difference'] = merged['New'] - merged['Old']
        merged['Absolute improvement'] = - (merged['New'] - merged['Old']) / merged['Old'] * 100.
        merged['Absolute improvement'] = merged['Absolute improvement'].map("{:,.2f}%".format)
        merged['Relative improvement'] = merged['Old'] / merged['New'] * 100.
        merged['Relative improvement'] = merged['Relative improvement'].map("{:,.2f}%".format)

        return merged

    def _compare_more_than_two_requests(self, analyzers):
        pass