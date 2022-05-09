# MakeBibFile bibliography creator
A simple tool for automatically populating a bibliography file for physics papers.

## Summary

Creating bibliography for scientific papers or theses can take up significant amounts of time.
In physics, thanks to popular data bases such as [ADS](https://adsabs.harvard.edu) or [Inspire HEP](https://inspirehep.net/) has made this task considerably simpler.

However, adding new entries one by one or a few at a time from these databases can still be time-consuming. The same is true for choosing citation keys and adjusting the bib file accordingly. Long arguments between co-authors about unique and persistent vs memorable keys can ensue.

This tool can mitigate these problems as it automatically generates bib entries from missing citation errors.
The user may populates a bib file by copying the missing entries to the clipboard (good for online tools such as Overleaf) or appending a bib file on disk.
The only requirement is that the keys used in the file are _any_ the following persistent identifiers:

- an [arXiv](https://arxiv.org/) preprint number (with or without `arXiv:` in front)
- a DOI (with or without `doi:` in front)
- an Inspire key

The preferred database for queries is ADS; Inspire is used as a fallback option.You need to you create an account and generate an API token for ADS, which [is explained below](#recommend-additional-steps).

## How to install

### Minimal install

To install, simply clone the repository
```
git clone https://github.com/sebhoof/make_bib_file
```
and make sure that your local Python supports the following packages: `numpy`, `pyperclip`, and `requests`. The only uncommon package is `pyperclip`, which allows the output of a string to be copied into the clipboard. If in doubt, run
```
python -m pip install numpy pyperclip requests
```

### Recommend additional steps

- [ ] Consider adding a `make_install.sh` that appends the path to the `${PATH}` variable
- [ ] Explain ADS account creating and token.

## How to use

Simply invoke the script on the log file created by LaTeX. If you main file is named `main.tex`, a your log named `main.log` will be created in the same folder. Running

```
python make_bib_file.py main.log
```
will copy the missing bib entries into your clipboard and you can paste them into your bib file.

It is recommended that you supply your ADS token e.g. named `my.token` to the script.

You may also supply the name of a bib file, say `my.bib`, the results will be appended to the file and not just pasted to the clipboard. A test is run on your bib file afterwards to detect possible duplicates.

The order of the arguments is _not_ relevant as long as the files end in `.log`, `.bib`, and `.token`. For example, you may call

```
python make_bib_file.py main.log my.bib my.token
```

- [ ] Talk about ADS journal abbrevs

## Citation
If this tool has saved you time and enabled your research, please consider acknowledging it in your work using the BibTeX entry below -- or better still by generating it automatically by putting `\cite{doi:}` in your paper!

```
@MISC{doi:,
}
```
