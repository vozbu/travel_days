#!/usr/bin/env python3

from datetime import date
import travel_days


def test__convert_dates__positive_one_row():
    data = [
          {'country': 'cnt1', 'entry_date': '2020-01-01', 'departure_date': '2020-02-29'}
    ]
    assert travel_days.convert_dates(data) is True
    assert len(data) == 1
    row = data[0]
    assert row['country'] == 'cnt1'
    assert row['entry_date'] == '2020-01-01'
    assert row['departure_date'] == '2020-02-29'
    assert row['entry_date_as_date'] == date(2020, 1, 1)
    assert row['departure_date_as_date'] == date(2020, 2, 29)


def test__convert_dates__positive_one_row_with_now():
    data = [
          {'country': 'cnt1', 'entry_date': '2020-01-01', 'departure_date': 'now'}
    ]
    assert travel_days.convert_dates(data) is True
    assert len(data) == 1
    row = data[0]
    assert row['country'] == 'cnt1'
    assert row['entry_date'] == '2020-01-01'
    assert row['departure_date'] == 'now'
    assert row['entry_date_as_date'] == date(2020, 1, 1)
    assert row['departure_date_as_date'] == date.today()


def test__convert_dates__positive_many_rows_with_now():
    data = [
          {'country': 'cnt1', 'entry_date': '2020-01-01', 'departure_date': '2020-01-31'},
          {'country': 'cnt2', 'entry_date': '2020-01-31', 'departure_date': '2020-05-01'},
          {'country': 'cnt1', 'entry_date': '2020-05-01', 'departure_date': '2020-05-10'},
          {'country': 'cnt3', 'entry_date': '2020-05-10', 'departure_date': 'now'},
    ]

    assert travel_days.convert_dates(data) is True
    assert len(data) == 4

    row = data[0]
    assert row['country'] == 'cnt1'
    assert row['entry_date'] == '2020-01-01'
    assert row['departure_date'] == '2020-01-31'
    assert row['entry_date_as_date'] == date(2020, 1, 1)
    assert row['departure_date_as_date'] == date(2020, 1, 31)

    row = data[1]
    assert row['country'] == 'cnt2'
    assert row['entry_date'] == '2020-01-31'
    assert row['departure_date'] == '2020-05-01'
    assert row['entry_date_as_date'] == date(2020, 1, 31)
    assert row['departure_date_as_date'] == date(2020, 5, 1)

    row = data[2]
    assert row['country'] == 'cnt1'
    assert row['entry_date'] == '2020-05-01'
    assert row['departure_date'] == '2020-05-10'
    assert row['entry_date_as_date'] == date(2020, 5, 1)
    assert row['departure_date_as_date'] == date(2020, 5, 10)

    row = data[3]
    assert row['country'] == 'cnt3'
    assert row['entry_date'] == '2020-05-10'
    assert row['departure_date'] == 'now'
    assert row['entry_date_as_date'] == date(2020, 5, 10)
    assert row['departure_date_as_date'] == date.today()


def test__convert_dates__negative_one_row():
    data = [
        [{'country': 'cnt1', 'entry_date': 'bad_date', 'departure_date': '2020-02-29'}],
        [{'country': 'cnt2', 'entry_date': '2020-01-01', 'departure_date': 'bad_date'}],
        [{'country': 'cnt3', 'entry_date': 'now', 'departure_date': '2020-02-29'}],
        [{'country': 'cnt4', 'entry_date': '2020-02-30', 'departure_date': '2020-02-29'}],
        [{'country': 'cnt5', 'entry_date': '2019-02-29', 'departure_date': '2020-02-29'}],
        [{'country': 'cnt6', 'entry_date': '2019-04-31', 'departure_date': '2020-02-29'}],
    ]

    for array in data:
        assert travel_days.convert_dates(array) is False


def test__convert_dates__negative_may_rows():
    data = [
        [{'country': 'cnt1', 'entry_date': '2020-01-01', 'departure_date': '2020-02-29'},
         {'country': 'cnt1', 'entry_date': 'bad_date', 'departure_date': '2020-02-29'}],

        [{'country': 'cnt2', 'entry_date': '2020-01-01', 'departure_date': 'bad_date'},
         {'country': 'cnt3', 'entry_date': 'now', 'departure_date': '2020-02-29'},
         {'country': 'cnt4', 'entry_date': '2020-02-20', 'departure_date': '2020-02-29'}],
    ]

    for array in data:
        assert travel_days.convert_dates(array) is False
