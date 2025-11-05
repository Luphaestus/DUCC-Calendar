from datetime import datetime, timedelta
import calendar
import sys
import subprocess
import os
from urllib import response
import requests
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import re
from collections import Counter
import traceback


class ducc_event:
    title = ""
    description = ""
    date = None

    def print_event(self):
        print(f"Title: {self.title}")
        print(f"Date: {self.date}")


class website:
    url = "https://durhamunicanoe.co.uk/events.php"
    url2 = "https://durhamunicanoe.co.uk/events.php?past_events=1&page=0"

    @staticmethod
    def _download_page(url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    @staticmethod
    def _downloadWholeWebsite():
        url = "https://durhamunicanoe.co.uk/events.php"

        if hasattr(website, 'websiteContent'):
            return website.websiteContent
        website.websiteContent = website._download_page(url)

        import concurrent.futures

        def fetch_page(i):
            url2 = f"https://durhamunicanoe.co.uk/events.php?past_events=1&page={i}"
            return website._download_page(url2)

        with tqdm(total=52, desc="Downloading pages") as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(fetch_page, i): i for i in range(52)}
                results = [None] * 52
                for fut in concurrent.futures.as_completed(futures):
                    i = futures[fut]
                    try:
                        results[i] = fut.result()
                    except Exception as e:
                        results[i] = ""
                    pbar.update(1)
                for page_content in results:
                    website.websiteContent += page_content

        return website.websiteContent

    def _text_between(self, text, start_str, end_str):
        start = text.find(start_str)
        if start == -1:
            return ""
        start += len(start_str)
        end = text.find(end_str, start)
        if end == -1:
            return ""
        return text[start:end]
    
    def get_events(self, whole_website=False):
        if whole_website:
            page_content = self._downloadWholeWebsite()
        else:
            page_content = self._download_page(self.url) + self._download_page(self.url2)

        events = page_content.split('event.php?id=')[1:]

        compiled_events = []

        for e in events:
            event = ducc_event()

            event.title = (self._text_between(e, '>', '<') or '')
            
            event.description = (self._text_between(e, '<p><p>', '</article>') or '').replace("\n", " ").replace("</p>", "\n").replace("<p>", "").strip()

            website_date = (self._text_between(e, '<em>', '</em>') or '')
            year = int(website_date[website_date[:website_date.find(' <strong>')].rfind(" ") + 1:website_date.find(' <strong>')])   
            month = list(calendar.month_name).index(self._text_between(website_date, '/sup> ', ' '))
            day = int(self._text_between(website_date, ' ', '<'))
            hour = int(self._text_between(website_date, '<strong>', ':'))
            minute = int(self._text_between(website_date, ':', '</strong>'))
            event.date = datetime(year, month, day, hour, minute)

            if compiled_events and compiled_events[-1].date == event.date:
                continue

            compiled_events.append(event)

        return compiled_events

def weekly_calendar(calendar_date = None, whole_website=False):

    title = """# DUCC - Calendar

> **Info:** This calendar shows upcoming and past DUCC events. See DUCC stats [here](stats.md).

"""

    def create_image(date=None, whole_website=False):
    
        if not date: date = datetime.now()
        day = (date.day) - ((-1) if date.weekday() == 6 else date.weekday())

        if day <= 0:
            new_month = date.month - 1 if date.month > 1 else 12
            new_year = date.year if date.month > 1 else date.year - 1
            days_in_prev_month = calendar.monthrange(new_year, new_month)[1]
            day = days_in_prev_month + day
            date = datetime(new_year, new_month, day)

        start_of_week = datetime(date.year, date.month, day)
        end_of_week = start_of_week + timedelta(days=7)

        current_events = [e for e in events if e.date and start_of_week <= e.date <= end_of_week]
        current_events.sort(key=lambda x: x.date)

        if not current_events:
            return
        if not whole_website:
            for event in current_events:
                event.print_event()
        
        img = Image.open(template_img)
        I1 = ImageDraw.Draw(img)

        titleFont = ImageFont.truetype('title.ttf', 60)
        eventFont = ImageFont.truetype('event.ttf', 19)


        date_start = 62
        date_end = 386
        date_width = date_end - date_start

        event_start = 402
        event_end = 1026
        event_width = event_end - event_start
        event_top = 170
        event_bottom = 269
        event_height = event_bottom - event_top
        event_text_spacing = 5
        event_vertical_padding = 6

        title_top = 80

        chill1 = None
        chill2 = None

        title_text = start_of_week.strftime('%d/%m/%y')
        _, _, line_w, _ = I1.textbbox((0, 0), title_text, font=titleFont)
        I1.text((img.width / 2 - line_w / 2, title_top), title_text, font=titleFont, fill=(0, 0, 0))

        for event in current_events:
            event.title = event.title.replace("Monday", "").replace("Tuesday", "").replace("Wednesday", "").replace("Thursday", "").replace("Friday", "").replace("Saturday", "").replace("Sunday", "")
            event.title = re.sub(r'\b\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm|AM|PM)?\b', '', event.title).strip()
            if "chill paddle" in event.title.lower():
                if not chill1:
                    chill1 = event
                elif not chill2:
                    chill2 = event
        if chill1 and chill2:
            chillPadelTimes = f"{chill1.date.strftime('%H:%M')} and {chill2.date.strftime('%H:%M')}"
            current_events.remove(chill2)
        
        for i in range(7):

            y_offset = 116 * i

            I1.rounded_rectangle((date_start, 170 + y_offset, date_end, 270 + y_offset), fill=(0, 74, 171),
                    width=1.8, radius=108)

            day_date = start_of_week + timedelta(days=i)
            day_str = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"][i]
            day_num = day_date.day
            month_str = calendar.month_name[day_date.month]

            if 10 <= day_num % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
                
            date_str = f"{day_str} {month_str} {day_num}{suffix}"
            
            _, _, date_text_w, _ = I1.textbbox((0, 0), date_str, font=eventFont)

            I1.text((date_start + (date_width - date_text_w) / 2, 204 + y_offset), date_str, font=eventFont, fill=(245, 245, 245))

            #---------

            I1.rounded_rectangle((event_start, event_top + y_offset, event_end, event_bottom + y_offset), fill=(0, 74, 171),
                            width=1.8, radius=108)
            
            event_texts = []
            for event in current_events:
                if event.date.day == day_date.day and event.date.month == day_date.month:
                    if event == chill1 and chill2:
                        event_texts.append(f"{chillPadelTimes} - Chill Paddle")
                    else:
                        event_texts.append(f"{event.date.strftime('%H:%M')} - {event.title}")

            total_event_height = -1
            sized_event_font = eventFont

            while total_event_height == -1 or total_event_height > event_height:
        
                total_event_height = event_text_spacing * (len(event_texts) - 1) + event_vertical_padding
                event_text_ws = []
                for event_text in event_texts:
                    _, _, event_text_w, event_text_h = I1.textbbox((0, 0), event_text, font=sized_event_font)
                    total_event_height += event_text_h
                    event_text_ws.append(event_text_w)
                if total_event_height > event_height:
                    sized_event_font_size = sized_event_font.size - 1
                    sized_event_font = ImageFont.truetype('event.ttf', sized_event_font_size)

            for i, event_text in enumerate(event_texts):
                _, _, event_text_w, event_text_h = I1.textbbox((0, 0), event_text, font=sized_event_font)
                event_text_x = event_start + (event_width - event_text_w) / 2
                event_text_y = event_top + y_offset + (event_height - total_event_height) / 2
                for j in range(i):
                    _, _, _, prev_event_text_h = I1.textbbox((0, 0), event_texts[j], font=sized_event_font)
                    event_text_y += prev_event_text_h + event_text_spacing
                I1.text((event_text_x, event_text_y), event_text, font=sized_event_font, fill=(245, 245, 245))

        if not whole_website: img.show()

        os.makedirs("./output", exist_ok=True)
        img.save("./output/duccWeeklyCalendar-" + start_of_week.strftime('%d%m%y') + ".png")

        
        entry = """
## **Week of """ + start_of_week.strftime('%d/%m/%Y') + """**

![DUCC CALENDAR](output/duccWeeklyCalendar-""" + start_of_week.strftime('%d%m%y') + """.png)
"""

        if not whole_website:
            if not os.path.exists("readme.md"):
                with open("readme.md", "w") as f:
                    f.write(title)

            with open("readme.md", "r+") as f:
                readme_content = f.read()
                if not start_of_week.strftime('%d/%m/%Y') in readme_content:
                    new_readme = title + entry + readme_content[len(title):]
                    f.seek(0)
                    f.write(new_readme)
                    f.truncate()
        else:
            return (start_of_week.strftime('%d/%m/%Y'), entry)

    template_img = 'duccEmpty.png'
    website_instance = website()
    events = website_instance.get_events(whole_website=whole_website)

    if whole_website:
        start_date = datetime(2012, 10, 9, 17, 0)
        now = datetime.now()

        if now.weekday() == 6:
            now += timedelta(days=1)

        current_week_start = now - timedelta(days=now.weekday())
        week_start = start_date - timedelta(days=start_date.weekday())

        total_weeks = ((current_week_start - week_start).days // 7) + 1
        import concurrent.futures

        new_readme = title
        entries = {}

        
        def process_week(week_start):
            result = create_image(week_start, whole_website=True)
            if result is not None:
                date, entry_text = result
                entries[date] = entry_text
         

        week_starts = []
        temp_week_start = week_start


        while temp_week_start <= current_week_start + timedelta(days=7):
            week_starts.append(temp_week_start)
            temp_week_start += timedelta(days=7)

        with tqdm(total=total_weeks, desc="Generating weekly calendars") as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_week, ws) for ws in week_starts]
                for fut in concurrent.futures.as_completed(futures):
                    try:
                        fut.result()  
                    except Exception as e:
                        print("Worker failed:", e)
                        tb = traceback.extract_tb(e.__traceback__)
                        if tb:
                            print("Error occurred at line:", tb[-1].lineno)
                    pbar.update(1)
        for date in sorted(entries.keys(), key=lambda d: datetime.strptime(d, '%d/%m/%Y'), reverse=True):
            new_readme += entries[date]
        with open("readme.md", "w") as f:
            f.write(new_readme)
    else:
        create_image(calendar_date)



with open("readme.md", "r") as f:
    readme = f.read()

if "15/10/2012" not in readme:
    weekly_calendar(whole_website=True)
else:  
    weekly_calendar()

