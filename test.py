from datetime import datetime

# Example times (you can replace these with actual UTC and new post times)
utc_time = datetime.utcnow()  # Current UTC time
new_post_time = datetime(2024, 10, 11, 15, 30, 0)  # Example post time

# Find the difference
time_difference = new_post_time - utc_time

# Convert to seconds
seconds_difference = time_difference.total_seconds()
print(seconds_difference)

import pytz
from django.utils import timezone
from datetime import timedelta

time_zone ='Asia/Karachi'

user_tz = pytz.timezone(time_zone)
user_time = timezone.now().astimezone(user_tz)
# utc_time = user_time.astimezone(pytz.utc)

# delay = ((utc_time + timedelta(minutes=3))-utc_time).total_seconds()
# print(delay)