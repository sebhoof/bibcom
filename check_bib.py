import sys
import numpy as np


def print_duplicates(non_uniques, ids, keys):
    """
    Helper function for a nice printout of duplicates.
    """
    for e in non_uniques:
        equiv_str = ""
        for id, key in zip(ids, keys):
            if id == e:
                equiv_str += key + " <-> "
        print(e + " | " + equiv_str[:-5])


def check_bib_file_for_duplicates(bibfile):
    """
    This function checks a bib file for duplicates and prints the findings.

    Parameters
    ----------
    bibfile : str
        The name of the bib file to be checked.

    Returns
    -------
    None

    Prints
    ------
        Prints the arXiv and DOI IDs that are duplicated in the bib file.
    """
    arxiv, doi = [], []
    arxiv_key, doi_key = [], []
    print("% Checking bib file {:s} for duplicates...".format(bibfile))
    with open(bibfile, "r") as f:
        key = ""
        for line in f:
            t = line.split("@")
            if len(t) > 1:
                key = t[1].split("{")[1].split(",")[0]
            t = line.split("eprint = ")
            if len(t) > 1:
                arxiv.append(t[1].split(",\n")[0][1:-1])
                arxiv_key.append(key)
            t = line.split("doi = ")
            if len(t) > 1:
                doi.append(t[1].split(",\n")[0][1:-1])
                doi_key.append(key)
    u, c = np.unique(arxiv, return_counts=True)
    d_arxiv = u[c > 1]
    n_d_arxiv = len(d_arxiv)
    u, c = np.unique(doi, return_counts=True)
    d_doi = u[c > 1]
    n_d_doi = len(d_doi)
    if n_d_arxiv + n_d_doi > 0:
        print(
            "% WARNING. {:d} duplicate arXiv ID(s) and {:d} duplicate DOI(s) detected!".format(
                n_d_arxiv, n_d_doi
            )
        )
        print(
            "% You need to fix the following equivalent keys for the unique IDs listed below:"
        )
        print("ID | Keys")
        if n_d_arxiv > 0:
            print_duplicates(d_arxiv, arxiv, arxiv_key)
        if n_d_doi > 0:
            print_duplicates(d_doi, doi, doi_key)
    else:
        print("% Done, no duplicates detected!")


# If the script is run directly, run the main function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        bibfile = sys.argv[1]
        check_bib_file_for_duplicates(bibfile)
    else:
        print("Please provide a BibTeX filename!")
