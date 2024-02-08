import re

time_pattern_single_first = re.compile(r"[0-1][0-9] *: *[0-5][0-9]")
time_pattern_single_second = re.compile(r"2[0-3] *: *[0-5][0-9]")

time_pattern_interval_first = re.compile(r"[0-1][0-9] *: *[0-5][0-9] *- *[0-1][0-9] *: *[0-5][0-9]")
time_pattern_interval_second = re.compile(r"[0-1][0-9] *: *[0-5][0-9] *- *2[0-3] *: *[0-5][0-9]")
time_pattern_interval_third = re.compile(r"2[0-3] *: *[0-5][0-9] *- *2[0-3] *: *[0-5][0-9]")
time_pattern_interval_fourth = re.compile(r"2[0-3] *: *[0-5][0-9] *- *1[0-9] *: *[0-5][0-9]")

