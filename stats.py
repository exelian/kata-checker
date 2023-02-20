import argparse
import re

from regex import generate_parser_regex

def extract_parts(m, group_name):
    return [
        v.strip()
        for k, v in m.groupdict().items() 
        if k.startswith(group_name) and v
    ]

def print_list(l, sort_list=True):
    pretty_list = [i.lower().capitalize() for i in set(l) if i]
    if sort_list:
        pretty_list.sort()

    for item in pretty_list:
        print('- ' + item)

def main():
    parser = argparse.ArgumentParser(description='Check a kata description for specific information')
    parser.add_argument('filename', type=str, help='filename to check')
    args = parser.parse_args()

    MATCHER = generate_parser_regex()
    actions = set()
    stances = set()
    with open(args.filename, 'r+') as f:
        for l in f:
            m = MATCHER.match(l.strip('\n'))
            if m is None:
                print(l)
                continue

            actions.update(extract_parts(m, 'technique'))
            stances.update(extract_parts(m, 'stance'))
    
    
    print('# Techniques')
    print_list(actions)

    print('# Stances')
    print_list(stances)

if __name__ == '__main__':
    main()