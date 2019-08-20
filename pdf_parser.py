from PyPDF4.pdf import PdfFileReader
import re

LIKED = 'Liked'
LACKED = 'Lacked'
LEARNED = 'Learned'
LONGED_FOR = 'Longed For'


def to_lines(text):
    return re.split('\n', text)


def get_raw_text(reader):
    return '\n'.join([
        reader.getPage(pagenum).extractText() for pagenum in range(reader.getNumPages())
    ]).strip()


def header(lines):
    # lines[0] Sprint title
    # lines[1] Date MMM DD, YYYY
    # lines[2] Participation Rate: % Card Count: #
    return lines[:3]


def body(lines):
    return lines[3:]


def divide(lines):
    return header(lines), body(lines)


def votes_to_csv_line(head):
    title = head[0]
    date = head[1].replace(',', '')

    def mapper_by_name(name):

        def mapper(lines):
            res = []

            class Packer:
                packing = False
                package = ['', []]  # Accumulator for packing lines in a group
                packer_joiner = lambda p: ' - '.join([p[0], ' / '.join(p[1])])

                @staticmethod
                def packer_appender():
                    _vote, _subject = re.split(' - ', Packer.packer_joiner(Packer.package))
                    _, quantity = re.split(' ', _vote)
                    # We still need the closure for the method
                    res.append(', '.join([name, _subject, quantity, title, date]))

            for line, ix in zip(lines, range(len(lines))):
                try:
                    vote, subject = re.split(' - ', line)  # eg. 'Votes 2 - New Group'

                    if Packer.packing:  # Always append if packing
                        Packer.packer_appender()

                    if subject == 'New Group':  # Time to reset anyway
                        Packer.packing = True
                        Packer.package = [vote, []]

                    else:
                        _, quantity = re.split(' ', vote)

                        res.append(', '.join([name, subject, quantity, title, date]))

                        Packer.packing = False
                        Packer.package = ['', []]

                except ValueError:  # It means, it wasn't possible to unpack the values since it didn't split on ' - '
                    if not line:  # No time to waste on empty strings
                        continue

                    line = line.replace(',', '')  # Removes commas given we are dealing with a CSV

                    if Packer.packing:  # This is for every line after a New Group, aka the merged cards
                        Packer.package[1].append(line)

                        if ix == len(lines) - 1:  # If it's the last line in the section, we should append it
                            Packer.packer_appender()

                    else:  # Deals with line breaks when we are not packing up
                        _, subject, quantity, _, _ = res[-1].split(', ')
                        res[-1] = ', '.join([name, ' / '.join([subject, line]), quantity, title, date])

            return res

        return mapper

    return mapper_by_name


def section_list(lines, section_name, section_end=''):
    start_ix = lines.index(section_name)
    end_ix = lines.index(section_end) if section_end else len(lines)
    return lines[start_ix + 1: end_ix]


def liked(lines):
    return section_list(lines, LIKED, LACKED)


def lacked(lines):
    return section_list(lines, LACKED, LEARNED)


def learned(lines):
    return section_list(lines, LEARNED, LONGED_FOR)


def longed_for(lines):
    return section_list(lines, LONGED_FOR)


def to_csv_generator(text):
    head, content = divide(text)
    mapper = votes_to_csv_line(head)

    return (
            list(mapper(LIKED)(liked(content))) +
            list(mapper(LACKED)(lacked(content))) +
            list(mapper(LEARNED)(learned(content))) +
            list(mapper(LONGED_FOR)(longed_for(content)))
    )


def titles():
    return ['verb, subject, votes, title, date']


def toCSVContent(file):
    reader = PdfFileReader(file)
    text = to_lines(get_raw_text(reader))
    return '\n'.join(titles() + to_csv_generator(text))
