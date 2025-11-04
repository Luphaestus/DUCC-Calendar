from main import website
from collections import Counter
from datetime import timedelta
import calendar

def cool_stats():
    website_instance = website()
    events = website_instance.get_events(whole_website=True)

    import matplotlib.pyplot as plt

    # Events per week
    event_counts = {}
    for event in events:
        week_start = event.date - timedelta(days=event.date.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_key = week_start.strftime('%Y-%m-%d')
        event_counts[week_key] = event_counts.get(week_key, 0) + 1

    weeks = sorted(event_counts.keys())
    counts = [event_counts[w] for w in weeks]

    plt.figure(figsize=(12, 6))
    plt.plot(weeks, counts, marker='o')
    plt.xticks(rotation=45)
    plt.xlabel('Week Starting')
    plt.ylabel('Number of Events')
    plt.title('Number of Events per Week Over Time')
    plt.tight_layout()
    plt.savefig('./output/events_per_week.png')
    plt.close()

    # Events by weekday
    weekday_counts = Counter(event.date.strftime('%A') for event in events)
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_values = [weekday_counts.get(day, 0) for day in weekdays]

    plt.figure(figsize=(8, 5))
    plt.bar(weekdays, weekday_values, color='skyblue')
    plt.xlabel('Weekday')
    plt.ylabel('Number of Events')
    plt.title('Events by Weekday')
    plt.tight_layout()
    plt.savefig('./output/events_by_weekday.png')
    plt.close()

    # Events by month
    month_counts = Counter(event.date.strftime('%B') for event in events)
    months = list(calendar.month_name)[1:]
    month_values = [month_counts.get(month, 0) for month in months]

    plt.figure(figsize=(10, 5))
    plt.bar(months, month_values, color='orange')
    plt.xlabel('Month')
    plt.ylabel('Number of Events')
    plt.title('Events by Month')
    plt.tight_layout()
    plt.savefig('./output/events_by_month.png')
    plt.close()

    # Most common event titles
    title_counts = Counter(event.title for event in events if event.title)
    common_titles = title_counts.most_common(10)
    titles, title_freqs = zip(*common_titles) if common_titles else ([], [])

    plt.figure(figsize=(10, 5))
    plt.barh(titles, title_freqs, color='green')
    plt.xlabel('Number of Occurrences')
    plt.title('Top 10 Most Common Event Titles')
    plt.tight_layout()
    plt.savefig('./output/top_event_titles.png')
    plt.close()

    

cool_stats()

with open('stats.md', 'w+') as f:
    f.truncate(0)
    f.seek(0)
    f.write("# Event Statistics\n\n")
    f.write("> **Warning:** This page is only updated once a month.\n\n")
    f.write("## Events per Week Over Time\n")
    f.write("![Events per Week](output/events_per_week.png)\n\n")
    f.write("## Events by Weekday\n")
    f.write("![Events by Weekday](output/events_by_weekday.png)\n\n")
    f.write("## Events by Month\n")
    f.write("![Events by Month](output/events_by_month.png)\n\n")
    f.write("## Top 10 Most Common Event Titles\n")
    f.write("![Top Event Titles](output/top_event_titles.png)\n")
