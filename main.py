from datetime import datetime, timedelta
import calendar
import sys
import subprocess
import os
from urllib import response
import requests
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm


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

    def _download_page(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def _downloadWholeWebsite(self):
        url = "https://durhamunicanoe.co.uk/events.php"

        website = self._download_page(url)

        with tqdm(total=52, desc="Downloading pages") as pbar:
            for i in range(0, 52):
                url2 = f"https://durhamunicanoe.co.uk/events.php?past_events=1&page={i}"
                website += self._download_page(url2)
                pbar.update(1)

        return website
    
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
    def create_image(date=None, show=True):
    
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
        if show:
            for event in current_events:
                event.print_event()
        

        img = Image.open(template_img)
        I1 = ImageDraw.Draw(img)

        titleFont = ImageFont.truetype('title.ttf', 100)
        eventFont = ImageFont.truetype('event.ttf', 38)

        date_start = 104
        date_end = 644  
        date_width = date_end - date_start

        event_start = 670
        event_end = 1710
        event_width = event_end - event_start
        event_top = 283
        event_bottom = 449
        event_height = event_bottom - event_top
        event_text_spacing = 8
        event_vertical_padding = 10

        chill1 = None
        chill2 = None

        title_text = start_of_week.strftime('%d/%m/%y')
        _, _, line_w, _ = I1.textbbox((0, 0), title_text, font=titleFont)
        I1.text((img.width / 2 - line_w / 2, 150), title_text, font=titleFont, fill=(0, 0, 0))

        for event in current_events:
            event.title = event.title.replace("Monday", "").replace("Tuesday", "").replace("Wednesday", "").replace("Thursday", "").replace("Friday", "").replace("Saturday", "").replace("Sunday", "")
            if "chill paddle" in event.title.lower():
                if not chill1:
                    chill1 = event
                elif not chill2:
                    chill2 = event
        if chill1 and chill2:
            chillPadelTimes = f"{chill1.date.strftime('%H:%M')} and {chill2.date.strftime('%H:%M')}"
            current_events.remove(chill2)
        
        for i in range(7):

            y_offset = 194 * i

            I1.rounded_rectangle((date_start, 283 + y_offset, date_end, 449 + y_offset), fill=(0, 74, 171),
                    width=3, radius=180)

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

            I1.text((date_start + (date_width - date_text_w) / 2, 340 + y_offset), date_str, font=eventFont, fill=(245, 245, 245))

            #---------

            I1.rounded_rectangle((event_start, event_top + y_offset, event_end, event_bottom + y_offset), fill=(0, 74, 171),
                            width=3, radius=180)
            
            event_texts = []
            for event in current_events:
                if event.date.day == day_date.day and event.date.month == day_date.month:
                    if event == chill1 and chill2:
                        event_texts.append(f"{chillPadelTimes} - Chill Padel")
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

        if show: img.show()

        os.makedirs("./output", exist_ok=True)
        img.save("./output/duccWeeklyCalendar-" + start_of_week.strftime('%d%m%y') + ".png")

        title = "# DUCC - Calendar\n\n"
        entry = """
## **Week of """ + start_of_week.strftime('%d/%m/%Y') + """**

![DUCC CALENDAR](output/duccWeeklyCalendar-""" + start_of_week.strftime('%d%m%y') + """.png)
"""

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

    template_img = 'duccEmpty.png'
    website_instance = website()
    events = website_instance.get_events(whole_website=whole_website)

    if whole_website:
        start_date = datetime(2012, 10, 9, 17, 0)
        now = datetime.now()
        current_week_start = now - timedelta(days=now.weekday())
        week_start = start_date - timedelta(days=start_date.weekday())

        total_weeks = ((current_week_start - week_start).days // 7) + 1
        with tqdm(total=total_weeks, desc="Generating weekly calendars") as pbar:
            while week_start <= current_week_start:
                create_image(week_start, False)
                week_start += timedelta(days=7)
                pbar.update(1)
    else:
        create_image(calendar_date)

weekly_calendar()

