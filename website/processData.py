import json

f = open('data.json')
data = json.load(f)

# writing to file
file2 = open('processRaw.raw', 'w')

count = 0
for i1 in data[0]["https://bmovies.cloud/movie/filter/series/"]:
    str = ''
    for part in i1:
        if part != 'Title' and part != 'Actor' and part != 'Link':
            str += part
            str += ': '
            str += i1[part]
            str += ' '

    # str = line.split(None, 2)
    L = [".I %d\n" % (count + 1), ".T\n %s\n" % i1['Title'], ".C\n %s\n" % i1['Actor'], ".O\n %s\n" % str, ".L\n %s\n" % i1['Link']]
    file2.writelines(L)
    count = count + 1

for i1 in data[1]["https://dopebox.to/tv-show?page="]:
    str = ''
    for part in i1:
        if part != 'Title' and part != 'Actor' and part != 'Link':
            str += part
            str += ': '
            str += i1[part]
            str += ' '

    # str = line.split(None, 2)
    L = [".I %d\n" % (count + 1), ".T\n %s\n" % i1['Title'], ".C\n %s\n" % i1['Actor'], ".O\n %s\n" % str, ".L\n %s\n" % i1['Link']]
    file2.writelines(L)
    count = count + 1

for i1 in data[2]["https://www3.moviecrumbs.net/tv-shows?page="]:
    str = ''
    for part in i1:
        if part != 'Title' and part != 'Actor' and part != 'Link':
            str += part
            str += ': '
            str += i1[part]
            str += ' '

    # str = line.split(None, 2)
    L = [".I %d\n" % (count + 1), ".T\n %s\n" % i1['Title'], ".C\n %s\n" % i1['Actor'], ".O\n %s\n" % str, ".L\n %s\n" % i1['Link']]
    file2.writelines(L)
    count = count + 1

# Closing file
f.close()
file2.close()
