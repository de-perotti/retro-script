from PyPDF4.pdf import PdfFileReader
import re

LIKED = 'Liked'
LACKED = 'Lacked'
LEARNED = 'Learned'
LONGED_FOR = 'Longed For'

def toLines(text):
    return re.split('\n', text)


def getRawText(reader):
    return '\n'.join([
        reader.getPage(pagenum).extractText() for pagenum in range(reader.getNumPages())
    ]).strip()


def header(lines):
    return lines[:3]


def body(lines):
    return lines[3:]


def divide(lines):
    return header(lines), body(lines)


def votes_to_csv_line(head):
    title = head[0]
    date = head[1].replace(',', '')
    def curried (name):
        def more_curring(line):
            vote, subject = re.split(' - ', line)
            _, qt = re.split(' ', vote)
            return ', '.join([name, subject, qt, title, date])
        return more_curring
    return curried


def liked(lines):
    liked_ix= lines.index(LIKED)
    lacked_ix= lines.index(LACKED)
    return lines[liked_ix + 1 : lacked_ix]


def lacked(lines):
    lacked_ix= lines.index(LACKED)
    learned_ix= lines.index(LEARNED)
    return lines[lacked_ix + 1: learned_ix]


def learned(lines):
    learned_ix= lines.index(LEARNED)
    longed_for_ix = lines.index(LONGED_FOR)
    return lines[learned_ix + 1: longed_for_ix]


def longed_for(lines):
    longed_for_ix = lines.index(LONGED_FOR)
    return lines[longed_for_ix + 1:]

def toCSVGenerator(text):
    head, content = divide(text)
    mapper = votes_to_csv_line(head)

    return (
        list(map(mapper(LIKED), liked(content))) +
        list(map(mapper(LACKED), lacked(content))) +
        list(map(mapper(LEARNED), learned(content))) +
        list(map(mapper(LONGED_FOR), longed_for(content))))

def titles():
    return ['verb, subject, votes, title, date']

def toCSVContent(file):
    reader = PdfFileReader(file)
    text = toLines(getRawText(reader))
    return '\n'.join(titles() + toCSVGenerator(text))

    