

import logging

class SkipAutoreloadFilter(logging.Filter):
    def filter(self, record):
        # Skip log records that contain "autoreload" in the message
        if hasattr(record, 'message') and 'autoreload' in record.message:
            return False
        return True
