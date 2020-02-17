from datetime import datetime, timedelta
import os.path
import emoji
import regex
from collections import defaultdict
import math


filename = "_chat.txt"

# Comma-separated list of old_name,new_name
# One rename per line, no quotes needed
rename_list_file = "rename_list.txt"
rename = {}
if os.path.isfile(rename_list_file):
    with open(rename_list_file, "r") as f:
        rename_list = [r.split(",") for r in f.read().splitlines()]
        if rename_list:
            rename = {names[0]: names[1] for names in rename_list}


def load_data(filename):
    with open(filename, "r") as f:
        lines = [i.replace("\u200e", "") for i in f.read().splitlines()]
    return lines


def separate_data(raw_lines):
    separated_lines = []

    for line in raw_lines:
        if line:
            if line[0] == "[":  # normal case
                pos = line.find("]")
                pub_time = datetime.strptime(line[1:pos], "%m/%d/%y, %H:%M:%S")
                text = line[pos + 2 :]
                if len(text.split(": ", maxsplit=1)) == 2:
                    author, message = text.split(": ", maxsplit=1)
                    if author in rename:
                        author = rename[author]
                    if (
                        message
                        == "Messages to this group are now secured with end-to-end encryption."
                    ):
                        continue

                else:  # someone did an action
                    # TODO: split on keywords: ['created', 'added', 'changed']
                    author = " ".join(text.split()[:2])
                    message = " ".join(text.split()[2:])
                    if author in rename:
                        author = rename[author]

                separated_lines.append([pub_time, author, message])
            else:  # line break-continued from previous message
                separated_lines[-1][2] += "\n" + line

    return separated_lines


def get_author_list(cleaned_data):
    authors = set()
    for _, author, _ in cleaned_data:
        authors.add(author)
    return sorted(authors)


def calculate_stats(cleaned_data, authors):
    num_messages = dict.fromkeys(authors, 0)
    num_chars = dict.fromkeys(authors, 0)
    hours = {h: 0 for h in range(0, 24)}
    gifs = dict.fromkeys(authors, 0)
    images = dict.fromkeys(authors, 0)
    liked = dict.fromkeys(authors, 0)
    emojis = defaultdict(int)
    emoji_authors = dict.fromkeys(authors, 0)
    last_sent = dict.fromkeys(authors, cleaned_data[0][0])

    min_date = cleaned_data[0][0].date()
    max_date = cleaned_data[-1][0].date()
    delta = (max_date - min_date) + timedelta(days=1)
    dates = {min_date + timedelta(d): 0 for d in range(0, delta.days)}

    # weeks = {min_date+7*timedelta(d):0 for d in range(0,math.floor(delta.days/7))}
    # todo: write a bin_week or something function that will return which week a date 'belongs' to

    for pub_time, author, message in cleaned_data:
        num_messages[author] += 1
        num_chars[author] += len(message)
        hours[pub_time.hour] += 1
        dates[pub_time.date()] += 1
        if pub_time > last_sent[author]:
            last_sent[author] = pub_time
        if message == "GIF omitted":
            gifs[author] += 1
        elif message == "image omitted":
            images[author] += 1
        elif message.startswith("Liked"):
            liked[author] += 1

        data = regex.findall(r"\X", message)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                emojis[word] += 1
                emoji_authors[author] += 1

    print("Number of Messages Sent")
    print("Name\tNumber of Messages Sent")
    for author in num_messages:
        print(author, "\t", num_messages[author])
    print()

    print("Average Message Length")
    print("Name\tAverage Message Length")
    for author in num_chars:
        print(author, "\t", round(num_chars[author] / num_messages[author]))
    print()

    print("Messages by Hour")
    print("Hour\tNumber of Messages Sent")
    for hour in hours:
        print(f"{hour}\t{hours[hour]}")
    print()

    print("Number of Images Sent")
    print("Name\tNumber of Images Sent")
    for author in images:
        print(author, "\t", images[author])
    print()

    # print('GIFs sent')
    # for author in gifs:
    #   print(author,'\t',gifs[author])
    # print()

    print("% GIFs")
    print("Name\t%GIFs")
    for author in gifs:
        print(author, "\t", round(gifs[author] / num_messages[author], 4))
    print()

    print("% Images+GIFs")
    print("Name\t%Images+GIFs")
    for author in gifs:
        print(
            author,
            "\t",
            round((gifs[author] + images[author]) / num_messages[author], 4),
        )
    print()

    # print('Liked...')
    # for author in liked:
    #   print(author,'\t',liked[author])
    # print()

    print("Emojis")
    print("Emoji\tCount")
    for e in emojis:
        print(e, "\t", emojis[e])
    print()

    print("Number of Emojis Sent")
    print("Name\tNumber of Emojis Sent")
    for author in emoji_authors:
        print(author, "\t", emoji_authors[author])
    print()

    print("Percentage of emojis")
    print("Name\t%Emojis")
    for author in emoji_authors:
        print(author, "\t", round(emoji_authors[author] / num_chars[author], 6))
    print()

    print("Messages per day")
    print("Day\t# of messages")
    for date in dates:
        print(date, "\t", dates[date])

    min_sent = min(dates.values())
    max_sent = max(dates.values())

    min_sent_dates = [date for date in dates if dates[date] == min_sent]
    max_sent_dates = [date for date in dates if dates[date] == max_sent]

    print(f"The most messages sent in a day was {max_sent}:")
    for msd in sorted(max_sent_dates):
        print(f"\t{msd}")
    print(f"The least messages sent in a day was {min_sent}:")
    for msd in sorted(min_sent_dates):
        print(f"\t{msd}")
    print()

    print("Last message sent")
    print("Name\tLast message sent")
    for author, date in sorted(last_sent.items(), key=lambda x: x[1]):
        print(author, "\t", date)
    print()

    print("Number of characters sent")
    print("Name\t# of chars")
    for author, chars in sorted(num_chars.items(), reverse=True, key=lambda x: x[1]):
        print(author, "\t", chars)
    print()


cleaned_data = separate_data(load_data(filename))
authors = get_author_list(cleaned_data)
calculate_stats(cleaned_data, authors)
