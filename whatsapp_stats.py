from datetime import datetime
import os.path

filename = '_chat.txt'

rename_list_file = 'rename_list.txt'

rename = {}
if os.path.isfile(rename_list_file):
  with open(rename_list_file, 'r') as f:
    rename_list = [r.split(',') for r in f.read().splitlines()]
    if rename_list:
      rename = {names[0]: names[1] for names in rename_list}

title_file_list = 'titles.txt'
titles = []
if os.path.isfile(title_file_list):
  with open(title_file_list, 'r') as f:
    titles = f.read().splitlines()

def load_data(filename):
  with open(filename, 'r') as f:
    lines = [i.replace('\u200e','') for i in f.read().splitlines()]
  
  return lines

def separate_data(raw_lines):
  separated_lines = []

  for line in raw_lines:
    if line:
      if line[0] == '[':          # normal case
        pos = line.find(']')
        pub_time = datetime.strptime(line[1:pos], '%m/%d/%y, %H:%M:%S')
        text = line[pos+2:]
        if len(text.split(':', maxsplit=1)) == 2:
          author, message = text.split(': ', maxsplit=1)
          if author in rename:
            author = rename[author]
          if author in titles:
            continue

        else:                     # someone did an action
          author = ' '.join(text.split()[:2])
          message = ' '.join(text.split()[2:])
          if author in rename:
            author = rename[author]
          if author in titles:
            continue
        
        separated_lines.append([pub_time, author, message])
      else:                       # line break-continued from previous message
        separated_lines[-1][2] += '\n' + line

  return separated_lines

def get_author_list(cleaned_data):
  authors = set()
  for _, author, _ in cleaned_data:
    authors.add(author)
  
  return sorted(authors)

def calculate_stats(cleaned_data, authors):
  num_messages = dict.fromkeys(authors, 0)
  num_chars = dict.fromkeys(authors, 0)
  hours = {h:0 for h in range(0,24)}
  gifs = dict.fromkeys(authors, 0)
  images = dict.fromkeys(authors, 0)
  liked = dict.fromkeys(authors, 0)

  for pub_time, author, message in cleaned_data:
    num_messages[author] += 1
    num_chars[author] += len(message)
    hours[pub_time.hour] += 1
    if message == 'GIF omitted':
      gifs[author] += 1
    elif message == 'image omitted':
      images[author] += 1
    elif message.startswith('Liked'):
      liked[author] += 1
  
  print('Number of Messages Sent')
  print('Name\tNumber of Messages Sent')
  for author in num_messages:
    print(author,'\t',num_messages[author])
  print()

  print('Average Message Length')
  print('Name\tAverage Message Length')
  for author in num_chars:
    print(author,'\t',round(num_chars[author]/num_messages[author]))
  print()

  print('Messages by Hour')
  print('Hour\tNumber of Messages Sent')
  for hour in hours:
    print(f'{hour}\t{hours[hour]}')
  print()

  print('Number of Images Sent')
  print('Name\tNumber of Images Sent')
  for author in images:
    print(author,'\t',images[author])
  print()

  # print('GIFs sent')
  # for author in gifs:
  #   print(author,'\t',gifs[author])
  # print()

  print('% GIFs')
  print('Name\t%GIFs')
  for author in gifs:
    print(author,'\t',round(gifs[author]/num_messages[author],4))
  print()

  print('% Images+GIFs')
  print('Name\t%Images+GIFs')
  for author in gifs:
    print(author,'\t',round((gifs[author]+images[author])/num_messages[author],4))
  print()

  # print('Liked...')
  # for author in liked:
  #   print(author,'\t',liked[author])
  # print()


cleaned_data = separate_data(load_data(filename))
authors = get_author_list(cleaned_data)
calculate_stats(cleaned_data, authors)
