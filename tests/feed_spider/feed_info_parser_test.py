from datetime import datetime

from dateutil.tz import tzutc

from feedsearch_crawler.feed_spider.feed_info_parser import FeedInfoParser


def test_entry_velocity_no_dates():
    dates = []
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 0


def test_entry_velocity_identical_dates():
    dates = [datetime(2020, 1, 1), datetime(2020, 1, 1), datetime(2020, 1, 1)]
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 0


def test_entry_velocity():
    dates = [
        datetime(2019, 1, 1),
        datetime(2019, 1, 2),
        datetime(2019, 1, 3),
        datetime(2019, 1, 4),
        datetime(2019, 1, 5),
    ]
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 1.0

    dates = [
        datetime(2019, 1, 1, 1),
        datetime(2019, 1, 1, 2),
        datetime(2019, 1, 1, 3),
        datetime(2019, 1, 1, 4),
        datetime(2019, 1, 1, 5),
    ]
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 24

    dates = [
        datetime(2019, 1, 1),
        datetime(2019, 1, 7),
        datetime(2019, 1, 14),
        datetime(2019, 1, 21),
        datetime(2019, 1, 27),
    ]
    dates = sorted(dates, reverse=True)
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 0.154

    dates = [
        datetime(2019, 9, 21, 13, 10, 3, tzinfo=tzutc()),
        datetime(2019, 9, 21, 13, 10, 3, tzinfo=tzutc()),
        datetime(2019, 9, 21, 2, 20, 32, tzinfo=tzutc()),
        datetime(2019, 9, 21, 2, 20, 32, tzinfo=tzutc()),
        datetime(2019, 9, 20, 20, 15, 45, tzinfo=tzutc()),
        datetime(2019, 9, 20, 20, 15, 45, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 40, 40, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 40, 40, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 38, 23, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 38, 23, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 23, 20, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 23, 20, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 8, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 8, tzinfo=tzutc()),
        datetime(2019, 9, 20, 18, 41, 57, tzinfo=tzutc()),
        datetime(2019, 9, 20, 18, 41, 57, tzinfo=tzutc()),
        datetime(2019, 9, 20, 17, 36, 30, tzinfo=tzutc()),
        datetime(2019, 9, 20, 17, 36, 30, tzinfo=tzutc()),
        datetime(2019, 9, 20, 17, 18, 2, tzinfo=tzutc()),
        datetime(2019, 9, 20, 17, 18, 2, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 35, 53, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 35, 53, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 25, 13, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 25, 13, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 0, 49, tzinfo=tzutc()),
        datetime(2019, 9, 20, 16, 0, 49, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 35, 50, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 35, 50, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 31, 35, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 31, 35, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 30, 48, tzinfo=tzutc()),
        datetime(2019, 9, 20, 15, 30, 48, tzinfo=tzutc()),
        datetime(2019, 9, 20, 11, 0, 53, tzinfo=tzutc()),
        datetime(2019, 9, 20, 11, 0, 53, tzinfo=tzutc()),
        datetime(2019, 9, 20, 10, 45, 16, tzinfo=tzutc()),
        datetime(2019, 9, 20, 10, 45, 16, tzinfo=tzutc()),
        datetime(2019, 9, 20, 10, 0, 49, tzinfo=tzutc()),
        datetime(2019, 9, 20, 10, 0, 49, tzinfo=tzutc()),
        datetime(2019, 9, 19, 22, 6, 47, tzinfo=tzutc()),
        datetime(2019, 9, 19, 22, 6, 47, tzinfo=tzutc()),
    ]
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 11.676

    dates = [
        datetime(2019, 9, 16, 14, 8, 51, tzinfo=tzutc()),
        datetime(2019, 9, 16, 14, 8, 51, tzinfo=tzutc()),
        datetime(2019, 9, 18, 4, 44, 14, tzinfo=tzutc()),
        datetime(2019, 9, 18, 4, 44, 14, tzinfo=tzutc()),
        datetime(2019, 9, 18, 9, 0, 16, tzinfo=tzutc()),
        datetime(2019, 9, 18, 9, 0, 16, tzinfo=tzutc()),
        datetime(2019, 9, 19, 14, 1, 56, tzinfo=tzutc()),
        datetime(2019, 9, 19, 14, 1, 56, tzinfo=tzutc()),
        datetime(2019, 9, 19, 20, 58, 52, tzinfo=tzutc()),
        datetime(2019, 9, 19, 20, 58, 52, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 41, 7, tzinfo=tzutc()),
        datetime(2019, 9, 20, 19, 41, 7, tzinfo=tzutc()),
        datetime(2019, 9, 20, 23, 2, 15, tzinfo=tzutc()),
        datetime(2019, 9, 20, 23, 2, 15, tzinfo=tzutc()),
        datetime(2019, 9, 21, 2, 53, 22, tzinfo=tzutc()),
        datetime(2019, 9, 21, 2, 53, 22, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 28, 43, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 28, 43, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 28, 44, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 28, 44, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 38, 3, tzinfo=tzutc()),
        datetime(2019, 9, 21, 5, 38, 3, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 0, 1, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 0, 1, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 36, 12, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 36, 12, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 39, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 39, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 54, 27, tzinfo=tzutc()),
        datetime(2019, 9, 21, 9, 54, 27, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 24, 14, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 24, 14, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 54, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 54, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 11, 57, 55, tzinfo=tzutc()),
        datetime(2019, 9, 21, 12, 50, 21, tzinfo=tzutc()),
        datetime(2019, 9, 21, 12, 50, 21, tzinfo=tzutc()),
        datetime(2019, 9, 21, 13, 26, 45, tzinfo=tzutc()),
        datetime(2019, 9, 21, 13, 26, 45, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 7, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 7, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 7, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 7, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 50, 13, tzinfo=tzutc()),
        datetime(2019, 9, 21, 17, 50, 13, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 9, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 10, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 10, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 10, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 10, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 12, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 3, 12, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 39, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 39, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 2, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 4, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 5, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 6, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 6, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 7, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 44, 7, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 50, 33, tzinfo=tzutc()),
        datetime(2019, 9, 21, 18, 50, 33, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 32, 23, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 32, 23, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 32, 25, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 32, 25, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 21, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 21, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 22, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 22, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 42, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 42, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 44, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 44, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 45, tzinfo=tzutc()),
        datetime(2019, 9, 21, 19, 50, 45, tzinfo=tzutc()),
    ]
    result = FeedInfoParser.entry_velocity(dates)
    assert result == 7.255


def test_is_podcast_no_data():
    data = {}
    result = FeedInfoParser.is_podcast(data)
    assert result is False


def test_is_podcast_not_podcast():
    data = {"entries": [{}]}
    result = FeedInfoParser.is_podcast(data)
    assert result is False


def test_is_podcast_no_namespace():
    data = {"entries": [{"enclosures": [{"media": "file_url"}]}]}
    result = FeedInfoParser.is_podcast(data)
    assert result is False


def test_is_podcast_is_true():
    data = {
        "namespaces": {"itunes": "testing"},
        "entries": [{"enclosures": [{"media": "file_url"}]}],
    }
    result = FeedInfoParser.is_podcast(data)
    assert result is True


def test_is_podcast_no_enclosures():
    data = {"namespaces": {"itunes": "testing"}, "entries": [{}]}
    result = FeedInfoParser.is_podcast(data)
    assert result is False
