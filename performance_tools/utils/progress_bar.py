from __future__ import unicode_literals
from optparse import make_option
from performance_tools.exceptions import ProgressBarException


PROGRESS_BAR_OPTION_LIST = (
    make_option(
        '-p', '--progress',
        action='store_true',
        dest='progress',
        default=False,
        help='progress bar'
    ),
    make_option(
        '-s', '--silent',
        action='store_true',
        dest='silent',
        default=False,
        help='silent mode'
    ),
)


def create_progress_bar(max_value, label='', item_name=''):
    """Create and initialize a progress bar.

    :param max_value: Number of items to process.
    :type max_value: int
    :param label: Bar label.
    :type label: str
    :param item_name: Name of the item that will be processed.
    :type item_name: str
    :return: Progress bar.
    :raise: If couldn't create a progress bar.
    """
    try:
        from progressbar import ProgressBar, Percentage, Bar, SimpleProgress, AdaptiveETA

        widgets = [label, ': ', Percentage(), ' ', Bar(marker='#', left='[', right=']'), ' ',
                   SimpleProgress(), ' ', item_name, ' ', AdaptiveETA()]
        bar_obj = ProgressBar(widgets=widgets, maxval=max_value)
        progressbar = bar_obj((i for i in range(max_value))).start()
    except Exception as e:
        raise ProgressBarException(str(e))

    return progressbar