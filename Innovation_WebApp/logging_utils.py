# Innovation_WebApp/logging_utils.py
import logging
import re

class TableFormatter(logging.Formatter):
    def format(self, record):
        fields = {
            'method': 'N/A',
            'path': 'N/A',
            'status': 'N/A',
            'duration': 'N/A',
            'ip': 'N/A',
            'user': 'N/A'
        }

        if ' | ' in record.msg:
            try:
                for part in record.msg.split(' | '):
                    if ': ' in part:
                        key, value = part.split(': ', 1)
                        key = key.lower().strip()
                        if key in fields:
                            fields[key] = value.strip()
            except (ValueError, AttributeError):
                pass

        return (
            f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S'):<25} | "
            f"{record.levelname:<8} | {record.module:<15} | "
            f"Method: {fields['method']:<6} | Path: {fields['path']:<40} | "
            f"Status: {fields['status']:<6} | Duration: {fields['duration']:<10} | "
            f"IP: {fields['ip']:<15} | User: {fields['user']:<15}"
        )

class DjangoServerFilter(logging.Filter):
    def filter(self, record):
        if record.name == 'django.server':
            match = re.match(r'\[.*?\] "(\w+) (.*?) HTTP/1\.1" (\d+) \d+', record.msg)
            if match:
                method, path, status = match.groups()
                record.msg = (
                    f"Method: {method} | Path: {path} | Status: {status} | "
                    f"Duration: N/A | IP: N/A | User: N/A"
                )
            else:
                record.msg = f"Message: {record.msg}"
        return True