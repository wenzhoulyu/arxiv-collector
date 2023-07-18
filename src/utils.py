from datetime import datetime, timedelta


def get_previous_weekdays(start_date, count):
    weekdays = []
    current_date = start_date
    while len(weekdays) < count:
        current_date -= timedelta(days=1)
        if current_date.weekday() < 5:  # Monday(0) to Friday(4) are weekdays
            weekdays.append(current_date.strftime('%Y%m%d'))
    return weekdays


def check_multiple_strings(main_string, substrings):
    lower_main_string = main_string.lower()
    is_all_caps_in_original = all(substring in main_string for substring in substrings if substring.isupper())
    is_not_all_caps_in_lower = all(
        substring in lower_main_string for substring in substrings if not substring.isupper())
    return is_all_caps_in_original and is_not_all_caps_in_lower

