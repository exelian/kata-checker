import argparse
import re
import xml.etree.ElementTree as ET

LANGUAGE_FILE = 'userDefineLang.xml'
KEYWORD_CLASSES = {
    'Keywords1': 'WEAPON',
    'Keywords2': 'HANDEDNESS',
    'Keywords3': 'TARGET',
    'Keywords4': 'WAZA',
    'Keywords5': 'WAZA_PREFIX',
    'Keywords6': 'DIRECTIONS',
    'Keywords7': 'TECHNIQUE_MODIFIERS',
    'Keywords8': 'errors'
}

class RegExFormat(object):
    def __init__(self, args):
        self.items = args

    def __format__(self, spec):
        extra = [''] if ' ' in spec else []
        joined = '|'.join(self.items + extra)

        if 'X' in spec:
            return f'(?:{joined})'

        return joined

def parse_xml_file(filename):
    xml_doc = ET.parse(filename)
    root = xml_doc.getroot()
    keyword_tags = root.findall('./UserLang/KeywordLists/Keywords')

    return {
        KEYWORD_CLASSES[tag.attrib['name']]: tag.text.split(' ')
        for tag in keyword_tags
        if tag.attrib['name'].startswith('Keywords')
    }

def generate_parser_regex():
    output = parse_xml_file(LANGUAGE_FILE)

    STANCES = RegExFormat([
        'Zenkutsu',
        'Kiba',
        'Kokutsu',
        'Nekoashi',
        'Moroashi',
        'Musubi',
        'Heisoku',
        'Heiko',
        'Fudo',
        'Sanchin',
        'Uchi hachiji',
        'Tsuruashi',
        'Mami',
        'Kosa',
        'Kake',
        'Juji'
    ])

    WEAPON = RegExFormat(output['WEAPON'])
    HANDEDNESS = RegExFormat(output['HANDEDNESS'])
    TARGET = RegExFormat(output['TARGET'])
    WAZA = RegExFormat(output['WAZA'])
    TECHNIQUE_MODIFIERS = RegExFormat(output['TECHNIQUE_MODIFIERS'])
    SPECIAL_TECHNIQUE = RegExFormat(['Kanku', 'Tensho'])

    LEFT_RIGHT = RegExFormat(['migi', 'hidari'])
    DIRECTIONS = RegExFormat(['N', 'NO', 'O', 'ZO', 'Z', 'ZW', 'W', 'NW'])
    DIRECTION = fr'(?:\|(?:{DIRECTIONS})\|)'

    WAZA_PREFIX = '(uchi|soto|morote|mae|kake|mawashi|nagashi)-'
    TECHNIQUE = fr'({WEAPON: })?\s?({HANDEDNESS: })\s?({TARGET: })\s?(?:{WAZA_PREFIX})?({WAZA})'
    MOROTE = fr'{TECHNIQUE} & {TECHNIQUE}\s*(\(morote\))?'
    FOLLOWUP = fr'{TECHNIQUE} -> {TECHNIQUE}\s*(\(nidan\))?'

    BUNKAI = r'^=>(?P<attack>.*?):(?P<uke>(?s:.*))\.'

    COUNT_LINE = fr'(?P<step>\d+): (?P<desc>.*) {DIRECTION}'
    STANCE_LINE = fr'- (?P<stance>{STANCES:X} dachi) ({LEFT_RIGHT}|{DIRECTION})'
    TECHNIQUE_LINE = fr'  - (?P<actions>{TECHNIQUE}|{MOROTE}|{FOLLOWUP})\s*(?P<mod>{TECHNIQUE_MODIFIERS: })'

    COMMENT = r'(?:\s*#(?P<comment>.*))?$'
    LINE = fr'^({COUNT_LINE}|{STANCE_LINE}|{TECHNIQUE_LINE}|{BUNKAI}|){COMMENT}'

    return re.compile(LINE)

def main():
    parser = argparse.ArgumentParser(description='Check a kata description for correctness')
    parser.add_argument('filename', type=str, help='filename to check')
    args = parser.parse_args()

    MATCHER = generate_parser_regex()
    with open(args.filename, 'r+') as f:
        for i, l in enumerate(f):
            m = MATCHER.match(l.strip('\n'))
            if not m:
                print(i, l, m)
                break

if __name__ == '__main__':
    main()