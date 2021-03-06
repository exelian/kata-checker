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
        KEYWORD_CLASSES[tag.attrib['name']]: (tag.text or "").split()
        for tag in keyword_tags
        if tag.attrib['name'].startswith('Keywords')
    }

def generate_parser_regex():
    output = parse_xml_file(LANGUAGE_FILE)

    STANCES = RegExFormat([
        'Zenkutsu',
        'Mae kiba',
        'Yonjugo kiba',
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
        'Juji',
        'Shiko'
    ])

    WEAPON = RegExFormat(output['WEAPON'])
    HANDEDNESS = RegExFormat(output['HANDEDNESS'])
    TARGET = RegExFormat(output['TARGET'])
    WAZA = RegExFormat(output['WAZA'])
    TECHNIQUE_MODIFIERS = RegExFormat(output['TECHNIQUE_MODIFIERS'])
    MOVEMENT_TYPE = RegExFormat(['tenkan', 'tenshin', 'yori ashi', 'tsugi ashi', 'surikomi ashi', 'ayumi ashi', 'tobi'])
    LEFT_RIGHT = RegExFormat(['migi', 'hidari'])
    MOVEMENT = fr'(?:(mae|ushiro)\s)?({MOVEMENT_TYPE})\s?({LEFT_RIGHT})?'

    DIRECTIONS = RegExFormat(['N', 'NO', 'O', 'ZO', 'Z', 'ZW', 'W', 'NW'])
    DIRECTION = fr'(?:\|(?:{DIRECTIONS})\|)'

    WAZA_PREFIX = RegExFormat(output['WAZA_PREFIX'])
    WAZA_SUFFFIX = RegExFormat(['komi'])
    TECHNIQUE = fr'({WEAPON: })?\s?({HANDEDNESS: })\s?(?:({TARGET: })\s)*(?:{WAZA_PREFIX})?({WAZA})\s?({WAZA_SUFFFIX})?'
    MOROTE = fr'{TECHNIQUE} & {TECHNIQUE}\s*(\(morote\))?'
    FOLLOWUP = fr'{TECHNIQUE} -> {TECHNIQUE}\s*(\(nidan\))?'
    FOLLOWUP3 = fr'{TECHNIQUE} -> {TECHNIQUE} -> {TECHNIQUE}\s*(\(sandan\))?'

    BUNKAI = r'^=>(?P<attack>.*?):(?P<uke>(?s:.*))\.'

    COUNT_LINE = fr'(?P<step>\d+): (?P<desc>.*) {DIRECTION}'
    STANCE_LINE = fr'- (hanmi\s*)?(?P<stance>{STANCES:X} dachi)\s*({LEFT_RIGHT})?\s*({DIRECTION})?'
    TECHNIQUE_LINE = fr'  - (?P<actions>{TECHNIQUE}|{MOROTE}|{FOLLOWUP}|{FOLLOWUP3}|{MOVEMENT})\s*(?P<mod>{TECHNIQUE_MODIFIERS: })'

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