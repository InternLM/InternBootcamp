import datetime

def format_time_now(format_str: str = "%Y%m%d%H%M%S") -> str:
    return datetime.datetime.now().strftime(format_str)