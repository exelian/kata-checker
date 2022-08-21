import argparse

from regex import generate_parser_regex

def main():
    parser = argparse.ArgumentParser(description='Check a kata description for specific information')
    parser.add_argument('filename', type=str, help='filename to check')
    args = parser.parse_args()

    MATCHER = generate_parser_regex()
    actions = set()
    with open(args.filename, 'r+') as f:
        for l in f:
            m = MATCHER.match(l.strip('\n'))
            techniques = [v.strip() for k, v in m.groupdict().items() if k.startswith('technique') and v]
            actions.update(techniques)
    
    print('\n'.join(sorted(actions)))

if __name__ == '__main__':
    main()