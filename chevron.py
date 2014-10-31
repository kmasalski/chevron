#!/usr/bin/python

from sys import argv


def tokenize(template):
    class UnclosedSection(Exception):
        pass

    def get(amount=1):
        return template[current:current + amount]

    def look(ahead=0, amount=1):
        idx = current + ahead
        if idx > len(template):
            raise EOFError()

        return template[idx:idx + amount]

    tag_types = {
        '!': 'comment',
        '#': 'section',
        '^': 'inverted section',
        '/': 'end',
        '>': 'partial',
        '=': 'set delimiter?',
        '{': 'no escape?',
        '&': 'no escape'
    }

    current = 0
    open_sections = []
    l_del = '{{'
    r_del = '}}'
    while current < len(template):
        try:
            size = 0
            while look(size, 2) != l_del:
                size += 1
        except EOFError:
            yield ('literal', get(size))
            return

        if size != 0:
            yield ('literal', get(size))

        current += size + 2

        tag_type = tag_types.get(get(), 'variable')
        if tag_type != 'variable':
            current += 1

        size = 1
        while look(size, 2) != r_del:
            size += 1

        tag_key = get(size).strip()
        current += size + 2

        if tag_type == 'no escape?':
            if look(-2, 3) == '}}}':
                tag_type = 'no escape'
                current += 1

        elif tag_type == 'set delimiter?':
            if look(-3) == '=':
                l_del, r_del = tag_key[:-1].split(' ')
                continue

        elif tag_type in ['section', 'inverted section']:
            open_sections.append(tag_key)

        elif tag_type == 'end':
            last_section = open_sections.pop()
            if tag_key != last_section:
                raise UnclosedSection()

        yield (tag_type, tag_key)

    return


if __name__ == '__main__':
    data = argv[1]
    template = argv[2]

    with open(template, 'r') as f:
        template = f.read()

    tokens = tokenize(template)
    for token in tokens:
        print(token)