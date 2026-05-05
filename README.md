# cronparse

> Human-readable cron expression parser and scheduler inspector with timezone support

---

## Installation

```bash
pip install cronparse
```

---

## Usage

```python
from cronparse import CronExpression

cron = CronExpression("0 9 * * MON-FRI", timezone="America/New_York")

# Get a human-readable description
print(cron.describe())
# → "At 09:00 AM, Monday through Friday, Eastern Time"

# Get the next 5 scheduled run times
for dt in cron.next_runs(count=5):
    print(dt)
# → 2024-03-11 09:00:00-05:00
# → 2024-03-12 09:00:00-05:00
# → ...

# Validate an expression
if CronExpression.is_valid("*/15 * * * *"):
    print("Valid cron expression")

# Check time until next run
print(cron.time_until_next())
# → "in 3 hours, 42 minutes"
```

---

## Features

- Parse standard 5-field cron expressions
- Generate plain-English descriptions of schedules
- Calculate next/previous run times
- Full timezone support via `pytz` / `zoneinfo`
- Validate expressions with detailed error messages

---

## Requirements

- Python 3.8+
- `pytz` or `zoneinfo` (stdlib, Python 3.9+)

---

## License

This project is licensed under the [MIT License](LICENSE).