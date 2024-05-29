import datetime

def date_to_int(date):
    return int(date.strftime("%Y%m%d"))

def int_to_date(int_date):
    return datetime.date(int_date // 10000, (int_date // 100) % 100, int_date % 100)