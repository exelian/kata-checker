import argparse
import re

class RegExFormat(object):
    def __init__(self, args):
        self.items = args

    def __format__(self, spec):
        extra = [''] if ' ' in spec else []
        joined = '|'.join(self.items + extra)

        if 'X' in spec:
            return f'(?:{joined})'

        return joined

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

WEAPON = RegExFormat([
    'Seiken',
    'Tettsui',
    'Chusoku',
    'Haito',
    'Shotei',
    'Empi',
    'Shuto',
    'Nukite',
    'Hiza',
    'Uraken',
    'Haisoku',
    'Hirate',
    'Haishu',
    'Teisoku',
    'Toho',
    'Sokuto',
    'Yoko'
])

HANDEDNESS = RegExFormat([
    'oi',
    'gyaku',
    'juji',
    'morote',
    'yama',
    'jun',
    'migi',
    'hidari'
])

TARGET = RegExFormat([
    'gedan',
    'jodan',
    'chudan',
    'hizo',
    'ganmen',
    'ago',
    'yoko',
    'shita',
    'soto',
    'sakotsu',
    'mae',
    'mawashi',
    'osai',
    'hitai',
    'komekami',
    'ushiro',
    'kansetsu',
    'kakiwake'
])

WAZA = RegExFormat([
    'uke',
    'barai',
    'tsuki',
    'geri',
    'ate',
    'uchi',
    'hikite',
    'hikiashi'
])

SPECIAL_TECHNIQUE = RegExFormat(['Kanku', 'Tensho'])

TECHNIQUE_MODIFIERS = RegExFormat(['ibuki', 'kiai'])

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
MATCHER = re.compile(LINE)

def main():
    parser = argparse.ArgumentParser(description='Check a kata description for correctness')
    parser.add_argument('filename', type=str, help='filename to check')
    args = parser.parse_args()

    with open(args.filename, 'r+') as f:
        for i, l in enumerate(f):
            m = MATCHER.match(l.strip('\n'))
            if not m:
                print(i, l, m)
                break

if __name__ == '__main__':
    main()