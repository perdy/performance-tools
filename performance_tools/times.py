from collections import OrderedDict

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


class Distribution(object):
    def __init__(self, data, spurious=0.1):
        """Store time series and remove spurious data.

        :param data: Time series data.
        :type data: numpy.array
        :param spurious: Spurious data coefficient.
        :type spurious: float
        """
        if spurious < 1:
            self.data = self._remove_spurious(data, spurious)
        elif spurious < 0 or spurious > 1:
            raise AttributeError
        else:
            self.data = np.sort(data)

        self.mu, self.std, self.median, self.max, self.min = self._statistical_data()

    def _remove_spurious(self, data, spurious=0.1):
        spurious_coefficient = spurious / 2
        num_spurious = int(len(data) * spurious_coefficient)
        return np.sort(data)[num_spurious:-num_spurious]

    def _statistical_data(self):
        mu, std = stats.norm.fit(self.data)
        median = self.data[len(self.data) / 2]
        max_ = self.data[-1]
        min_ = self.data[0]

        return mu, std, median, max_, min_

    def plot(self, normal=True, pareto=True):
        """Plot data.

        :param normal: If true, plot normal distribution.
        :type normal: bool
        :param pareto: If true, plot pareto distribution (80-20 law).
        :type pareto: bool
        """
        if pareto:
            pareto = 1.161

        # Plot the histogram.
        plt.hist(self.data, bins=25, normed=True, alpha=0.6, color='g')

        # Plot normal PDF.
        xmin, xmax = plt.xlim()
        grid_granularity = 100 if len(self.data) > 100 else len(self.data)
        x = np.linspace(xmin, xmax, grid_granularity)
        if normal:
            norm_pdf = stats.norm.pdf(x, self.mu, self.std)
            plt.plot(x, norm_pdf, 'k', linewidth=2, label='Normal')

        # Plot pareto PDF.
        if pareto:
            pareto_pdf = stats.pareto.pdf(x, pareto)
            plt.plot(x, pareto_pdf, 'r', linewidth=2, label='Pareto')

        title = "Fit results: mu = %.2f,  std = %.2f" % (self.mu, self.std)
        plt.title(title)

        plt.legend()
        plt.show()

    def __repr__(self):
        return "Max: {}\nMin: {}\nMean: {}\nStandard Deviation: {}\nMedian: {}".format(
            self.max, self.min, self.mu, self.std, self.median
        )


class Classification(object):
    def __init__(self, data, **classes):
        """Classify time series.

        :param data: Time series data.
        :type data: numpy.array
        :keyword classes: Classes and values.
        """
        if len(classes) == 0:
            classes = {
                'excellent': 0.4,
                'good': 1.0,
                'ok': 1.5,
                'bad': 3.0,
                'ugly': None,
            }

        self.classes = OrderedDict(sorted(classes.items(), key=lambda t: t[1], reverse=True))
        self.data = np.sort(data)
        self.classified_data = self._classify()

    def _classify(self):
        result = {k: 0 for k in self.classes.keys()}

        for data in self.data:
            current_klass = None
            for klass, max_value in ((k, v) for k, v in self.classes.items()):
                if data < max_value or (current_klass is None and max_value is None):
                    current_klass = klass

            result[current_klass] += 1

        return result

    def __repr__(self):
        total = float(sum(self.classified_data.values())) / 100
        return "\n".join(["{}: {:d} ({:.2f}%)".format(k, v, v / total) for (k, v) in self.classified_data.items()])
