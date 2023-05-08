DATE_FORMAT = "j m Y"  # '25 Oct 2006'
TIME_FORMAT = "H:i:s"  # '14:30:00
DATETIME_FORMAT = "d/m/Y, H:i:s"  # '25/10/2006, 14:30:00.'
YEAR_MONTH_FORMAT = "F Y"  # 'October 2006'
MONTH_DAY_FORMAT = "j F"  # '25 October'
SHORT_DATE_FORMAT = "d/m/Y"  # '25/10/2006'
SHORT_DATETIME_FORMAT = "d/m/Y H:i:s"  # '25/10/2006 2:30 p.m.'
FIRST_DAY_OF_WEEK = 1  # Monday

DATE_INPUT_FORMATS = [
    "%d/%m/%Y",  # '25/10/2006'
    "%d/%m/%y",  # '25/10/06'
]

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # '2006-10-25 14:30:59'
    "%Y-%m-%d %H:%M:%S.%f",  # '2006-10-25 14:30:59.000200'
    "%Y-%m-%d %H:%M",  # '2006-10-25 14:30'
    "%d/%m/%Y %H:%M:%S",  # '25/10/2006 14:30:59'
    "%d/%m/%Y %H:%M:%S.%f",  # '25/10/2006 14:30:59.000200'
    "%d/%m/%Y %H:%M",  # '25/10/2006 14:30'
    "%d/%m/%y %H:%M:%S",  # '25/10/06 14:30:59'
    "%d/%m/%y %H:%M:%S.%f",  # '25/10/06 14:30:59.000200'
    "%d/%m/%y %H:%M",  # '25/10/06 14:30'
]

DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","
NUMBER_GROUPING = 3
