
# trim FASTA sequences

Some FASTA databases can be really big - even limiting the number of sequences
by removing redundance is sometimes not enough (NCBI's non-redundant nrdb is
still many GBs in size, and growing).
Several tools have difficulties, dealing with such big databases.
One option is to limit your search to exactly the taxon you're interested in.
The script `trim_fasta_db_by_taxon.py` does exactly that for you!

You give it FASTA database and a taxonomic range and it will parse the file and
spit out a copy of the FASTA file with only those sequences belonging to the
taxon range you defined.

For example, taking all of NCBI nrdb and filter it to bacteria only, you would type:

    trim_fasta_db_by_taxon.py ./databases/nrdb.fasta bacteria

Use quotes, if you want to define a taxon with spaces in the name:

    trim_fasta_db_by_taxon.py ./databases/nrdb.fasta 'homo sapiens'


## Notes

Non-redundant databases are created by merging multiple identical sequences
into one entry. Often the header of all these sequences are merged into one,
resulting in one very long line. In order to save space in the output file,
`trim_fasta_db_by_taxon.py` by default will produce FASTA headers which will be
trimmed to the first one. You can switch this off by setting `TRIM_HEADER` to `False`...
