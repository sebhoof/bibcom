<h1 align="center">BibCom &ndash; a BibTeX bibliography creator</h1>

[![DOI](https://zenodo.org/badge/485510848.svg)](https://zenodo.org/badge/latestdoi/485510848) [![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

BibCom simplifies the creation of a BibTeX bibliography for scientific papers, specifically in physics.
The tool automatically generates BibTeX entries from ADS or INSPIRE for missing citations in LaTeX documents.
The new BibTeX entries are copied to the clipboard (useful for online tools such as [Overleaf](https://www.overleaf.com)) or appended to a local BibTeX file.


## Introduction

Creating a BibTeX bibliography is necessary but tedious.
Databases such as [NASA/ADS](https://adsabs.harvard.edu) or [HEP INSPIRE](https://inspirehep.net/) provide an immense help, but adding new entries a few at a time is still time-consuming.
The same is true for adjusting the bib file accordingly to match the preferred citation key style.

Enter BibCom! This tool automatically generates bib entries for missing citations from the &ldquo;missing citation&rdquo; entries from the `.log` file.
New bib entries will be copied to the clipboard or appended to a local bib file.
The only requirement is that the citation keys correspond to _any_ combination of the following persistent identifiers:

- an [arXiv](https://arxiv.org/) preprint number (with or without `arXiv:` in front)
- a DOI (with or without `doi:` in front)
- a [HEP INSPIRE](https://inspirehep.net/) key
- a [NASA/ADS](https://ui.adsabs.harvard.edu/) key 

The recommended database for queries is ADS, but INSPIRE can be used as a fallback option.
To query ADS, you need to create a free account and generate an API token, [as explained below](#recommended-additional-steps).

## Installation

Clone the repository and ensure that the following Python packages are installed: `numpy`, `pyperclip`, and `requests`.
If in doubt, run
```
python -m pip install numpy pyperclip requests
```

### Recommended additional steps

Create an ADS account following [this link](https://ui.adsabs.harvard.edu/user/account/register).
Apart from getting an API token, this is also useful for creating a custom email alerts for new arXiv papers.
You can then generate the API token under `Account -> Settings -> API Token`.
Paste it into a plain text file and save the file as e.g. `my.token` in your local copy of the BibCom repository.


## How to use BibCom

Compiling your LaTeX paper `[main].tex` creates a log file named `[main].log` in the in the same folder.
If you are using [Overleaf](https://www.overleaf.com), it can be downloaded after clicking on the &ldquo;Logs and output files&rdquo;, scrolling down and clicking on &ldquo;Other logs and files&rdquo;.

Then simpliy update your bibliography as needed with Bibcom until you are ready to submit.
At that point, you may want to check your bibliography for duplicates (see [Complete overview](#complete-overview)).

### Quickstart

To query the INSPIRE database, simply run
```
python compile_bib.py [main].log
```
and paste the results into your bib file (using Ctrl+V, Cmd+V, or right click -> paste).
If you provide your ADS API in a file `my.token` or via the environment variable `ADS_API_TOKEN`, the ADS database will be queried instead.

### Complete overview

The full range of options for `compile_bib.py` also allows for adding the name of a bib file `/some/folder/to/my.bib` and/or the name of a file `my.token` containing your ADS API:
```
python compile_bib.py [main].log my.token /some/folder/to/my.bib
```
In this case, the new bib entires will be additionally appended to the file.
If the file `/some/folder/to/my.bib` does not exist, it will be created.
When providing a bib file name, BibCom will automatically check for duplicates.

Note that the order of the arguments and the names of the files do _not_ matter as long as the files end in `.log`, `.bib`, and `.token`. For example, any of the below will work
```
python compile_bib.py my.token [main].log
python compile_bib.py [main].log my.token
python compile_bib.py /some/folder/to/my.bib [main].log my.token
```

The ADS BibTeX entries use LaTeX macros to abbreviate some of the commonly encountered journal names, as described [here](https://ui.adsabs.harvard.edu/help/actions/journal-macros).
For convenience, this repo contains the file [jdefs.tex](jdefs.tex), which can be downloaded and included in your LaTeX file preamble via `\include{jdefs}`.

To check an exiting bib file `/some/folder/to/my.bib` for duplicates, run
```
python check_bib.py /some/folder/to/my.bib
```
The check is based on arXiv/eprint IDs and DOIs.
The code will print the names of any duplicates that the user needs to fix.