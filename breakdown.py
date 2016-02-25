#!/usr/bin/env python
from __future__ import print_function
import argparse


def orphans(hiloci):
    """
    Determine orphan iLoci from the hiLocus data table and store in memory.
    """
    orphan_iloci = dict()
    for record in hiloci:
        values = record.strip().split('\t')
        if values[1] != '1':
            continue
        for ilocus in values[2].split(','):
            orphan_iloci[ilocus] = True
    return orphan_iloci


def conserved(hicons):
    """
    Load conserved iLoci into memory from the conserved hiLocus data table.
    """
    conserved_iloci = dict()
    next(hicons)
    for record in hicons:
        values = record.strip().split('\t')
        assert len(values) == 4, values
        hilocus = values[0]
        ilocus = values[1]
        conserved_iloci[ilocus] = hilocus
    return conserved_iloci


def get_parser():
    """Define the program command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--counts', action='store_true',
                        help='report iLocus counts; by default, the amount of '
                        'the genome occupied (in bp) is reported')
    parser.add_argument('-l', '--length', type=int, metavar='LEN',
                        default=50000, help='length cutoff above which piLoci '
                        'are designated as `LongMatch` instead of `Match; '
                        'default is 50000`')
    parser.add_argument('iloci', type=argparse.FileType('r'),
                        help='ilocus data table')
    parser.add_argument('hiloci', type=argparse.FileType('r'),
                        help='hilocus data table')
    parser.add_argument('hicons', type=argparse.FileType('r'),
                        help='conserved hilocus data table')
    return parser


def main(args):
    """Main procedure."""
    orphan_iloci = orphans(args.hiloci)
    conserved_iloci = conserved(args.hicons)
    outcols = ['Conserved', 'Matched', 'LongMatched', 'Orphan', 'Complex',
               'ncRNA', 'Intergenic', 'Fragment']
    breakdown = dict()
    for record in args.iloci:
        if record.startswith('Species'):
            continue
        values = record.rstrip().split('\t')
        species = values[0]
        ilcid = values[1]
        eff_len = int(values[4])
        ilclass = values[8]

        if species not in breakdown:
            breakdown[species] = dict((col, list()) for col in outcols)

        if ilclass == 'iiLocus':
            breakdown[species]['Intergenic'].append(values)
        elif ilclass == 'fiLocus':
            breakdown[species]['Fragment'].append(values)
        elif ilclass == 'ciLocus':
            breakdown[species]['Complex'].append(values)
        elif ilclass == 'niLocus':
            breakdown[species]['ncRNA'].append(values)
        else:
            assert ilclass == 'piLocus', ilclass
            if ilcid in orphan_iloci:
                breakdown[species]['Orphan'].append(values)
            elif ilcid in conserved_iloci:
                breakdown[species]['Conserved'].append(values)
            elif eff_len > args.length:
                breakdown[species]['LongMatched'].append(values)
            else:
                breakdown[species]['Matched'].append(values)

    print('\t'.join(['Species'] + outcols))
    for species in sorted(breakdown):
        print(species, end='', sep='')
        for col in outcols:
            iloci = breakdown[species][col]
            if args.counts:
                print('\t%d' % len(iloci), end='', sep='')
            else:
                cumlength = sum([int(x[4]) for x in iloci])
                print('\t%d' % cumlength, end='', sep='')
        print('\n', end='')


if __name__ == '__main__':
    main(get_parser().parse_args())
