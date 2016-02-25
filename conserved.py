#!/usr/bin/env python
from __future__ import print_function
import argparse
import glob


simple_iloci = dict()
for infile in glob.glob('species/*/*.simple-iloci.txt'):
    with open(infile, 'r') as instream:
        for line in instream:
            ilocus = line.strip()
            simple_iloci[ilocus] = True


iloc2prot = dict()
for infile in glob.glob('species/*/*.protein2ilocus.txt'):
    with open(infile, 'r') as instream:
        for line in instream:
            protid, locusid = line.strip().split('\t')
            iloc2prot[locusid] = protid


class HiLocus(object):

    def __init__(self, record):
        self._rawdata = record
        values = record.strip().split('\t')
        self.iloci = values[2].split(',')
        self.species = values[3].split(',')
        self.iloci_by_species = dict()
        for locus in self.iloci:
            species = locus[13:17]
            if species not in self.iloci_by_species:
                self.iloci_by_species[species] = list()
            self.iloci_by_species[species].append(locus)

    def in_clade(self, clade):
        reps = list()
        for species in clade:
            if species not in self.iloci_by_species:
                continue
            copynumber = len(self.iloci_by_species[species])
            assert copynumber > 0
            if copynumber > 1:
                continue
            ilocus = self.iloci_by_species[species][0]
            if ilocus not in simple_iloci:
                continue
            reps.append(ilocus)
        if len(reps) == 0:
            reps = None
        return reps

    def in_seven(self):
        clade = ['Amel', 'Bter', 'Cflo', 'Hsal', 'Pcan', 'Pdom', 'Nvit']
        return self.in_clade(clade)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', default='0.0.0',
                        help='specify version for hiLocus labels; default is '
                        '"0.0.0"')
    parser.add_argument('hiloci', type=argparse.FileType('r'),
                        help='hilocus data table')
    return parser


def main(args):
    hilocus_count = 0
    print('hiLocus', 'iLocus', 'Species', 'Protein', sep='\t')
    for line in args.hiloci:
        hilocus = HiLocus(line)
        scos = hilocus.in_seven()
        if scos is None or len(scos) != 7:
            continue
        hilocus_count += 1
        for sco in scos:
            hid = 'HymHub-v{}-HILC-{}'.format(args.version, hilocus_count)
            print(hid, sco, sco[13:17], iloc2prot[sco], sep='\t')

if __name__ == '__main__':
    main(get_parser().parse_args())
