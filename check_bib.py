import numpy as np

def check_bib_file_for_duplicates(bibfile):
    arxiv, doi = [], []
    print("% Checking bib file {:s} for duplicates...".format(bibfile))
    with open(bibfile, "r") as f:
        for line in f:
            for e in line.split("@"):
                t = e.split("eprint = ")
                if len(t) > 1:
                    arxiv.append(t[1].split(",\n")[0][1:-1])
                t = e.split("doi = ")
                if len(t) > 1:
                    doi.append(t[1].split(",\n")[0][1:-1])
    s, c = np.unique(arxiv, return_counts=True)
    n_d_arxiv = sum(c > 1)
    if n_d_arxiv > 0:
        print("% The following {:d} arXiv IDs are duplicated:".format(n_d_arxiv))
        print(s[c > 1])
    s, c = np.unique(doi, return_counts=True)
    n_d_doi = sum(c > 1)
    if n_d_doi > 0:
        print("% The following {:d} DOI IDs are duplicated:".format(n_d_doi))
        print(s[c > 1])
    if n_d_arxiv + n_d_doi > 0:
        print(
            "% WARNING. Duplicates detected (see above)! Please remove them from the bib file."
        )
    else:
        print("% No duplicates detected!")