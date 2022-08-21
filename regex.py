import re
import xml.etree.ElementTree as ET

__all__ = ['generate_parser_regex']

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
    def __init__(self, args, allow_empty=False):
        self.allow_empty = allow_empty
        self.items = args

    def __format__(self, spec):
        extra = [''] if self.allow_empty else []
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

    WEAPON = RegExFormat(output['WEAPON'], allow_empty=True)
    HANDEDNESS = RegExFormat(output['HANDEDNESS'], allow_empty=True)
    TARGET = RegExFormat(output['TARGET'], allow_empty=True)
    WAZA = RegExFormat(output['WAZA'])
    TECHNIQUE_MODIFIERS = RegExFormat(output['TECHNIQUE_MODIFIERS'], allow_empty=True)
    MOVEMENT_TYPE = RegExFormat(['tenkan', 'tenshin', 'yori ashi', 'tsugi ashi', 'surikomi ashi', 'ayumi ashi', 'tobi'])
    LEFT_RIGHT = RegExFormat(['migi', 'hidari'])
    MOVEMENT = fr'(?:(mae|ushiro)\s)?({MOVEMENT_TYPE})\s?({LEFT_RIGHT})?'

    DIRECTIONS = RegExFormat(['N', 'NO', 'O', 'ZO', 'Z', 'ZW', 'W', 'NW'])
    DIRECTION = fr'(?:\|(?:{DIRECTIONS})\|)'

    WAZA_PREFIX = RegExFormat(output['WAZA_PREFIX'])
    WAZA_SUFFFIX = RegExFormat(['komi'])
    TECHNIQUE = fr'({WEAPON})?\s?({HANDEDNESS})\s?(?:({TARGET})\s)*(?:{WAZA_PREFIX})?({WAZA})\s?({WAZA_SUFFFIX})?'
    MOROTE = fr'(?P<technique2>{TECHNIQUE}) & (?P<technique3>{TECHNIQUE})\s*(\(morote\))?'
    FOLLOWUP = fr'(?P<technique4>{TECHNIQUE}) -> (?P<technique5>{TECHNIQUE})\s*(\(nidan\))?'
    FOLLOWUP3 = fr'(?P<technique6>{TECHNIQUE}) -> (?P<technique7>{TECHNIQUE}) -> (?P<technique8>{TECHNIQUE})\s*(\(sandan\))?'

    BUNKAI = r'^=>(?P<attack>.*?):(?P<uke>(?s:.*))\.'

    COUNT_LINE = fr'(?P<step>\d+): (?P<desc>.*) {DIRECTION}'
    STANCE_LINE = fr'- (hanmi\s*)?(?P<stance>{STANCES:X} dachi)\s*({LEFT_RIGHT})?\s*({DIRECTION})?'
    TECHNIQUE_LINE = fr'  - (?P<actions>(?P<technique1>{TECHNIQUE})|{MOROTE}|{FOLLOWUP}|{FOLLOWUP3}|{MOVEMENT})\s*(?P<mod>{TECHNIQUE_MODIFIERS})'

    COMMENT = r'(?:\s*#(?P<comment>.*))?$'
    LINE = fr'^({COUNT_LINE}|{STANCE_LINE}|{TECHNIQUE_LINE}|{BUNKAI}|){COMMENT}'

    return re.compile(LINE)
