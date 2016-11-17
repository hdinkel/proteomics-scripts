#!env python


"""
Script to parse a given FASTA file and filter it to a give taxonomic range

For example, take all of NCBI nrdb, filter it to bacteria only.

PARAMETERS:
    - 1. fasta_filename = name of the file to be filtered
    - 2. root_taxon = name of the NCBI taxon-id to filter on; use quotes!

"""

import sys
import os
import re
from ete3 import NCBITaxa

def read_fasta(fastafile):
    """
    Generator to read a fasta file
    """
    name, seq = None, []
    for line in fastafile:
        line = line.strip()
        if line.startswith(">"):
            if name:
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name:
        yield (name, ''.join(seq))

if __name__ == '__main__':
    DEBUG = True
    DEBUG = False
    TRIM_HEADER = True  # Do we want to shorten overlong FASTA headers to save space?

    taxon_regexes = {'ncbi': '\[(.*?)\]', 'uniprot': 'OS=(.*?) GN='} # add more regexes here
    taxon_re = None

    print("Reading NCBI Taxa...")
    ncbi = NCBITaxa()
    print("Done...")

    if len(sys.argv) < 2:
        print("\nNeed exactly two parameters! None given...\n")
        print("Documentation:")
        print(__doc__)
        sys.exit(9)

    #root_taxon = 'Leptospira alexanderi'
    root_taxon = sys.argv[2]
    lineage = ncbi.get_descendant_taxa(root_taxon, intermediate_nodes=True)
    root_taxon_id =ncbi.get_name_translator([root_taxon])[root_taxon][0]
    lineage.append(root_taxon_id)
    names = ncbi.translate_to_names(lineage)
    seqs_by_taxon = dict()
    for name in names:
        seqs_by_taxon[name] = []
    if DEBUG: print("Total # of Taxons: %s " % (len(seqs_by_taxon)))
    if DEBUG: print("First 10 taxons: %s" % seqs_by_taxon.keys()[:10])


    FASTAFILE = sys.argv[1]
    FASTAFILE = os.path.expanduser(FASTAFILE)
    OUTFILE = os.path.splitext(FASTAFILE)[0] + '_' + root_taxon.replace(' ','_') + os.path.splitext(FASTAFILE)[1]

    if not os.path.isfile(FASTAFILE):
        raise OSError(2, 'No such file or directory:', FASTAFILE)
    else:
        with open(FASTAFILE, 'r') as f:
            for name, seq in read_fasta(f):
                if not taxon_re:
                    for dbtype, regex in taxon_regexes.items():
                        print("DBType: '%s', Regex: '%s'" % (dbtype, regex))
                        test_re = re.compile(regex)
                        if test_re.search(name):
                            taxon_re = test_re
                            print("Found match of regex '%s' in FASTA header '%s'" % (taxon_re.pattern, name[:50]))
                            print("Using DBType '%s'" % dbtype)
                            break
                    if not taxon_re:
                        print("could not parse taxon from FASTA headers")
                        sys.exit(9)
                taxon_match = taxon_re.search(name)
                if taxon_match:
                    taxon = taxon_match.group(1)
                    if TRIM_HEADER:
                        name = name[:taxon_match.span()[1]]  # This trims off overly long FASTA headers (trim after first taxon name)
                    if taxon in seqs_by_taxon:
                        seqs_by_taxon[taxon].append([name,seq])
                    else:
                        if DEBUG: print("Not including taxon: '%s'" % (taxon))
                        else: pass

        print("Number of Seqs by Taxon:", len(seqs_by_taxon))
        with open(OUTFILE, 'w') as fout:
            for taxon, fastaitems in seqs_by_taxon.items():
                for fastaitem in fastaitems:
                    name, seq = fastaitem
                    fout.write(name + '\n')
                    fout.write(seq + '\n')

