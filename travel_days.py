#!/usr/bin/env python3

import argparse
from collections import defaultdict
import csv
from datetime import date


def parse_args():
    parser = argparse.ArgumentParser(
            prog='travel_days',
            description='Helps you to track count of days you stay in different countries',
            add_help=True,
            exit_on_error=True)

    parser.add_argument('-f', '--file', default='travel_days.csv')

    subparsers = parser.add_subparsers(title="command to execute", required=True, dest='command')

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('-y', '--year', default='all', help='year to show: use \'last\' for last'
                             ' rolling year or specify year number. \'all\' means no filter')

    parser_days = subparsers.add_parser('days')
    parser_days.add_argument('-y', '--year', default='all', help='year to show: use \'last\' for last'
                             ' rolling year or specify year number. \'all\' means no filter (default)')
    parser_days.add_argument('-l', '--last', default=False, action=argparse.BooleanOptionalAction,
                             help='last visit total days. Ignores --year')

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('country', help='country - use quotes if it contains space in it\'s name')
    parser_add.add_argument('entry_date', help='date of entry in format YYYY-MM-DD')
    parser_add.add_argument('departure_date', help='date of departure in format YYYY-MM-DD (use \'now\' if '
                            'you are still there)')

    parser_del = subparsers.add_parser('del')
    parser_del.add_argument('line', type=int, help='line number to delete (obtain it from `list` command')

    args = parser.parse_args()

    return args


# reads CSV file in list of dicts in the same order as in file
def read(filename):
    data = []
    try:
        file = open(filename, newline='')
        # fieldnames = ['country', 'entry_date', 'departure_date']
        # don't specify fieldnames - assume csv file has a header
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    except IOError:
        return data

    return data


# Converts string dates to date dates handling 'now' and checking for errors
# Returns False in case of error
def convert_dates(data):
    line = 1
    for row in data:
        try:
            row['entry_date_as_date'] = date.fromisoformat(row['entry_date'])
        except ValueError:
            print(f"bad entry date '{row['entry_date']}' in line {line}, entry skipped")
            return False

        try:
            row['departure_date_as_date'] = date.fromisoformat(row['departure_date'])
        except ValueError:
            if row['departure_date'] == 'now':
                row['departure_date_as_date'] = date.today()
            else:
                print(f"bad departure date '{row['departure_date']}' in line {line}, entry skipped")
                return False

        line += 1

    return True


# Sorts records by entry date, then by departure date
# Assumes that entry date <= departure date, although I'm not sure that this is always the case
# Returns data again as a list
def sort(data):
    sorted_items = sorted(data, key=lambda x:
                          str(x['entry_date_as_date']) + '%%%' + str(x['departure_date_as_date']))
    return sorted_items


# Checks that each entry is valid and entries are not overlapping
def check(data):
    last_departure_date = None
    last_departure_country = None
    for row in data:
        if row['entry_date_as_date'] > row['departure_date_as_date']:
            print(f"in country {row['country']} entry date {row['entry_date']} is after departure date"
                  f" {row['departure_date']}")
            return False
        if last_departure_date is not None:
            diff = row['entry_date_as_date'] - last_departure_date
            if diff.days not in (0, 1):
                print(f"entry date {row['entry_date']} to {row['country']} is too far from last departure"
                      f" date {last_departure_date} from country {last_departure_country}")
                return False
        if row['departure_date'] == 'now':
            last_departure_date = None
        else:
            last_departure_date = row['departure_date_as_date']
        last_departure_country = row['country']
    return True


# Combines all load file steps above
def load_data(args):
    data = read(args.file)
    if not convert_dates(data):
        return None
    data = sort(data)
    if not check(data):
        return None
    return data


def filter_data_by_year(data, year):
    if year == 'all':
        return data

    start_date = None
    end_date = None

    if year == 'last':
        end_date = date.today()
        # TODO what if current date is 29th of February?
        # TODO handles last day of month correctly?
        start_date = date(end_date.year - 1, end_date.month, end_date.day + 1)
    else:
        end_date = date(int(year), 12, 31)
        start_date = date(int(year), 1, 1)

    res = []
    for row in data:
        if row['entry_date_as_date'] < start_date:
            row['entry_date_as_date'] = start_date
        if row['departure_date_as_date'] > end_date:
            row['departure_date_as_date'] = end_date
        if row['entry_date_as_date'] < row['departure_date_as_date']:
            res.append(row)

    return res


def list(data):
    if len(data) == 0:
        print('No entries')
    line = 1
    for row in data:
        print(f"{line}: {row['country']} {row['entry_date']} => {row['departure_date']}")
        line += 1


def days(data):
    res = defaultdict(lambda: 0)
    for row in data:
        res[row['country']] += (row['departure_date_as_date'] - row['entry_date_as_date']).days + 1
    for country in res:
        print(country, res[country])


def last(data):
    for row in data:
        if row['departure_date'] == 'now':
            days = (row['departure_date_as_date'] - row['entry_date_as_date']).days + 1
            print(f"Your current visit in {row['country']} lasts for {days} days already")
            return
    print("Couldn't find the country you are now in")


# Leave only fields from source CSV file
def filter_data_fields(data):
    res = []
    fieldnames = ['country', 'entry_date', 'departure_date']
    for row in data:
        wrow = {}
        for f in fieldnames:
            wrow[f] = row[f]
        res.append(wrow)
    return res


def write(filename, data):
    file = open(filename, 'w', newline='')
    writer = csv.DictWriter(file, fieldnames=['country', 'entry_date', 'departure_date'])

    writer.writeheader()
    data = filter_data_fields(data)
    for row in data:
        writer.writerow(row)


def add(data, args):
    # Make, convert and check one line
    res = [{'country': args.country, 'entry_date': args.entry_date, 'departure_date': args.departure_date}]
    if not convert_dates(res):
        return False
    if not check(res):
        return False

    # Add it to main array and check as a whole
    data.append(res[0])
    if not check(data):
        return False

    # if prev record has 'now' as it's departure date - update it to new entry date
    if len(data) >= 2:
        prev = data[-2]
        cur = data[-1]
        if prev['departure_date'] == 'now' and cur['entry_date_as_date'] > prev['entry_date_as_date']:
            prev['departure_date'] = cur['entry_date']

    write(args.file, data)

    return True


def delete(data, args):
    if args.line > len(data):
        print(f"you data has only {len(data)} lines")
        return

    print(f"entry with country {data[args.line - 1]['country']} are being deleted")
    del data[args.line - 1]
    print('your data are probably invalid now - check with `list` command')

    write(args.file, data)


def main():
    args = parse_args()
    data = load_data(args)
    if data is None:
        return

    match args.command:
        case 'list':
            data = filter_data_by_year(data, args.year)
            list(data)
        case 'days':
            if not args.last:
                data = filter_data_by_year(data, args.year)
                days(data)
            else:
                last(data)
        case 'add':
            if add(data, args):
                list(data)
        case 'del':
            delete(data, args)


if __name__ == "__main__":
    main()
