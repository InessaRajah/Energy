import pytz
from datetime import datetime

cat = pytz.timezone('Africa/Johannesburg')
today = datetime.date(datetime.now(tz = cat))
print("Current Date Hour in South Africa =",
today
)
