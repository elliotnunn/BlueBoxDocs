#!/usr/bin/env python3

import argparse


parser = argparse.ArgumentParser(description='''
    Search a 68k binary file for the "MOVE.L <selector>,d0; DC.W $FE22"
    motif. Use the upper word of the selector to determine how many
    32-bit arguments the call takes. This is useful because, while many
    selector names are known from reversing the BlueAbstractionLayerLib,
    that PowerPC binary does not reveal anything about their function
    signatures. Instead this falls to 68k code, in which the number of
    arguments is often passed to a trap via the selector in order to
    avoid catastrophic stack damage in the unknown-selector case.
''')

parser.add_argument('src', action='store', help='Source file')
parser.add_argument('-o', nargs='?', action='store', help='Listing file to update')

args = parser.parse_args()


with open(args.src, 'rb') as f:
    binary = f.read()


def matches(long, short):
    keepers = bytearray()

    for i in range(len(short)):
        if short[i] == 0:
            keepers.append(long[i])

        if short[i] not in (0, long[i]):
            return False

    return bytes(keepers)


MOTIF = b'\x20\x3C\x00\x00\x00\x00\xFE\x22'

for i in range(len(binary) - len(MOTIF)):
    match = matches(binary[i:i+len(MOTIF)], MOTIF)

    if match:
        long = int.from_bytes(match, byteorder='big')

        selector = long & 0xFFFF
        nargs = long >> 16

        print('selector %04x: %d' % (selector, nargs))

        if args.o:
            with open(args.o) as f:
                lines = [l.rstrip('\n').split(' ') for l in f]

            for line in lines:
                line[0] = int(line[0], 16) # interpret the hex at the start!

            for line in lines:
                if line[0] == selector:
                    if line[1] == '?':
                        print('...updated')
                        line[1] = str(nargs)
                    elif line[1] != str(nargs):
                        print('...WARNING: the listing file says %s' % line[1])
                    break
            else:
                lines.append([selector, str(nargs), '???'])
                lines.sort()

            for line in lines:
                line[0] = '%04X' % line[0]

            with open(args.o, 'w') as f:
                f.write(''.join(' '.join(l)+'\n' for l in lines))
