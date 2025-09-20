import datetime
from events.models import Events

sample_events = []
base_date = datetime.datetime(2025, 6, 1, 10, 0)

for i in range(1, 101):
    sample_events.append(
        Events(
            name=f"Event {i}",
            category="WEB",
            title=f"Test Event {i}",
            description=f"This is test event number {i}.",
            date=base_date + datetime.timedelta(days=i),
            location="KCA University",
            organizer="Test Org",
            contact_email=f"event{i}@example.com",
            is_virtual=bool(i % 2),
        )
    )

Events.objects.bulk_create(sample_events)
print("✅ 100 events added.")
