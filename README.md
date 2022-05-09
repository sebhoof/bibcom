<h1 align="center">BibCom &ndash; a BibTeX bibliography creator</h1>

[![DOI]()]() [![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The Bibliography Compiler (BibCom) is a simple tool for automatically populating a BibTeX bibliography file for physics (and possibly other) papers.


## Summary

Creating a bibliography can take up significant amounts of time.
In physics, popular data bases such as [ADS](https://adsabs.harvard.edu) or [Inspire HEP](https://inspirehep.net/) have made this task fairly simple.

Still, adding new entries one by one or a few at a time is time-consuming.
The same is true for choosing citation keys and adjusting the bib file accordingly.
Long arguments between co-authors about persistent vs memorable keys can ensue.

BibCom can mitigate these problems by automatically generating bib entries for missing citations.
It populates a bib file based on &ldquo;missing citation&rdquo; entries from the LaTeX log file.
The new bib entries with correct keys will be copied straight to the clipboard (good for online tools such as Overleaf) or appended to a local bib file.
The only requirement is that the keys used in the file are _any_ the following persistent identifiers:

- an [arXiv](https://arxiv.org/) preprint number (with or without `arXiv:` in front)
- a DOI (with or without `doi:` in front)
- an Inspire key

The preferred database for queries is ADS; Inspire is used as a fallback option. To use ADS you have to create an account and generate an API token for ADS, which [is explained below](#recommend-additional-steps).


## How to install

### Minimal install

To install, simply clone the repository
```
git clone https://github.com/sebhoof/bibcom
```
and make sure that your local Python supports the following packages: `numpy`, `pyperclip`, and `requests`. The only uncommon package is `pyperclip`, which allows the output of a string to be copied into the clipboard. If in doubt, run
```
python -m pip install numpy pyperclip requests
```

### Recommended additional steps

Create an ADS account following [this link](https://ui.adsabs.harvard.edu/user/account/register).
Apart from getting an API token, this is also useful for creating a custom email alerts for new arXiv papers (no, I am not affiliated with ADS).
You can then generate the API token under `Account -> Settings -> API Token`.
Paste it into a plain text file and save the file as e.g. `my.token` in your local copy of the BibCom repository.


## How to use

### Quickstart guide

With the LaTeX log file named `main.log` and your ADS API token in the first line of the file `my.token`, run
```
python compile_bibliography.py main.log my.token
```
and just paste the results into your bib file afterwards (using Ctrl+V, Cmd+V, or right click and paste).

### Detailed guide

If you main file is named `main.tex`, a log file named `main.log` should be present in the in the same folder as `main.tex`. Running
```
python compile_bibliography.py main.log
```
will copy the missing bib entries into your clipboard and you can paste them into your bib file.

To use ADS, you need to supply your ADS token in a text file e.g. named `my.token`.

If you provide the name of a bib file, say `/some/folder/my.bib`, the results will additionally be appended to the file.
Should the file not exist, a new file with that name will be created.
The code will test your bib file for duplicates.

The order of the arguments and the names of the files are _not_ relevant as long as the files end in `.log`, `.bib`, and `.token`. For example, you may call
```
python compile_bibliography.py main.log /some/folder/my.bib my.token
```

The ADS BibTeX entries use LaTeX macros to abbreviate some of the commonly encountered journal names, as described [here](https://ui.adsabs.harvard.edu/help/actions/journal-macros).
For convenience, this repo contains the file [jdefs.tex](jdefs.tex), which can be included in your LaTeX file preamble via `\include{jdefs}`.
