import argparse

from regex import generate_parser_regex

def main():
    parser = argparse.ArgumentParser(description='Check a kata description for correctness')
    parser.add_argument('filename', type=str, help='filename to check')
    args = parser.parse_args()

    MATCHER = generate_parser_regex()
    with open(args.filename, 'r+') as f:
        last_step = 0

        for i, l in enumerate(f):
            m = MATCHER.match(l.strip('\n'))

            if not m:
                print(i, l, m)
                break

            if m.group('step') is not None:
                this_step = int(m.group('step'))
                if this_step != (last_step + 1):
                    print('#{} Step count should always increment by 1 - {}'.format(i, l))
                    break
                last_step = this_step

if __name__ == '__main__':
    main()