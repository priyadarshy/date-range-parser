#### date_range_parser

```python
import pytz
import datetime
import date_range_parser

# Create a source/reference time 
tz_name = u'America/New_York'
timezone = pytz.timezone(tz_name)
src_time = timezone.localize(datetime.datetime(2014, 8, 3, 10, 0, 32))

parse = date_range_parser.parse("after tomorrow and before next wednesday", src_time)

```
