from oura_bot.utils import second_to_hms


def test_seconds_to_hms():
    seconds = 3665
    expected = '1:01:05'
    assert second_to_hms(seconds) == expected


def test_hms_to_seconds_errors():
    seconds = 0
    expected = '0:00:00'
    assert second_to_hms(seconds) == expected
    seconds = 86400
    expected = '1 day, 0:00:00'
    assert second_to_hms(seconds) == expected
    seconds = -1
    expected = '-1 day, 23:59:59'
    assert second_to_hms(seconds) == expected
