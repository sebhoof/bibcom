import sys, os
import time
import requests
import json
import pyperclip

from check_bib import check_bib_file_for_duplicates

# Define the version number
bibcom_ver = "v0.4"

# User needs to supply their ADS token as the 'token' variable, via then env variable $ADS_API_TOKEN, or later in a file
token = os.getenv("ADS_API_TOKEN")
token = "" if token is None else token
inspire_api_url = "https://labs.inspirehep.net/api/"
ads_api_url = "https://api.adsabs.harvard.edu/v1/export/bibtex"


def check_and_append(bibcode: str, lst: list[str]):
    """
    This function checks if a bibcode is already being considered and adds it to the list of codes if necessary.

    Parameters
    ----------
    bibcode : str
        A bibcode.
    lst : list
        The list to check if it already contains the bibcode

    Returns
    -------
    None
    """
    if not (bibcode in lst):
        lst.append(bibcode)


def create_payloads(logfilename: str):
    """
    Creates a list of lists of bibcodes by sorting the bibcodes according to origin.

    Parameters
    ----------
    logfilename : str
        The name of a LaTeX log file

    Returns
    -------
    list[list[str]]
        List of lists, where the bibcodes are sorted according to origin

    Raises
    ------
    FileNotFoundError
        If the log file cannot be found.
    """
    arxiv, inspire, doi, ads, nn = [], [], [], [], []
    try:
        with open(logfilename, "r") as f:
            log_lines = f.read().split("\n")
        for l in log_lines:
            # Read the log file and find missing bib entries
            if "Citation" in l:
                bibcode = l.split("`")[1].split("'")[0]
                try:
                    potential_arxiv = bibcode[4] == "."
                except IndexError:
                    potential_arxiv = False
                # DOIs should start with '10.' or 'doi'; check these first
                if (bibcode[:3] == "10.") or (bibcode[:3] == "doi"):
                    check_and_append(bibcode, doi)
                # Arxiv IDs contain 'YYMM.' or '/'; INSPIRE IDs should not
                elif (potential_arxiv) or ("/" in bibcode):
                    check_and_append(bibcode, arxiv)
                # Also allow INSPIRE TeX keys of type 'AUTHOR:YYYYaaa'
                elif ":" in bibcode:
                    check_and_append(bibcode, inspire)
                # Finally, try to identify an ADS code, which is always 19 chars long
                elif len(bibcode) == 19:
                    check_and_append(bibcode, ads)
                # Otherwise, the ID is not known
                else:
                    check_and_append(bibcode, nn)
    except FileNotFoundError as not_found:
        print("\n% ERROR! File", not_found.filename, "could not be found!\n")
        sys.exit()
    return [arxiv, inspire, doi, ads, nn]


def reformat_inspire_entry(request: requests.models.Response, new_key: str):
    """
    This function reformats an INSPIRE entry.

    Parameters
    ----------
    request : requests.models.Response
        The response from an INSPIRE API request.
    new_key : str
        The new key to use for the entry.

    Returns
    -------
    str
        The reformatted entry if found, else "".
    """
    # Get the INSPIRE results and replace the key of the first entry (if found)
    data = request.json()
    bibstring = requests.get(data["links"]["bibtex"]).text
    if len(bibstring) > 0:
        t1, t2 = bibstring.split("{", 1)
        t2, t3 = t2.split(",", 1)
        return t1 + "{" + new_key + "," + t3
    else:
        return ""


def reformat_ads_entries(bibcodes: list[str], original_keys: list[str]):
    """
    This function reformats the ADS entries.

    Parameters
    ----------
    bibcodes : list
        A list of bibcode strings.
    original_keys : list
        A list of the corresponding, original bib keys.

    Returns
    -------
    str
        A string of bibfile lines.
    """
    # Submit multiple missing entires to the ADS API
    payload = {"bibcode": bibcodes, "sort": "year desc"}
    serialized_payload = json.dumps(payload)
    data = requests.post(
        ads_api_url,
        headers={"Authorization": "Bearer " + token},
        data=serialized_payload,
    )
    try:
        bibfile_lines = data.json()["export"].splitlines()
    except:
        print(
            "% ERROR. The requested entry may not exist on ADS or the ADS website may be unavailable."
        )
        return ""
    keyword_type = "eprint"
    if bibcodes[0][0] == "d":
        keyword_type = "doi"
    elif len(bibcodes[0]) == 19:
        return "".join([b + "\n" for b in bibfile_lines])
    # Loop over the bibfile entires and replace the original keys
    for i in range(len(bibfile_lines)):
        l = bibfile_lines[i]
        if len(l) > 0:
            if l[0] == "@":
                tmp = l.split("{")
                i0 = i
                while not (keyword_type in l):
                    i += 1
                    l = bibfile_lines[i]
                id = l.split("{")[1][:-2]
                original_key = [s for s in original_keys if id in s]
                if len(original_key) > 0:
                    original_key = original_key[0]
                else:
                    # Assume this was a single query with INSPIRE key
                    original_key = original_keys[0]
                bibfile_lines[i0] = tmp[0] + "{" + original_key + ","
    return "".join([b + "\n" for b in bibfile_lines])


def compile_bibliography(payloads, bibfile="", print_results=False):
    """
    This function takes a list of bibcodes and creates a bibliography from them.
    The results can be appended to a bibfile, printed, and are copied to clipboard for pasting.

    Parameters
    ----------
    payloads : list
        A list of lists of bibcodes.
    bibfile : str, optional
        The name of the bibfile to which the bibliography should be appended.
        If not provided, the bibliography will not be appended to a file.
    print_results : bool, optional
        If True, the bibliography will be printed to the console.

    Returns
    -------
    int
        The number of bib entries created.

    Raises
    ------
    FileNotFoundError
        If the log file or the bibfile cannot be found.
    """
    arxiv, inspire, doi, ads = payloads[:-1]
    bib_entries = "% Bibliography entries created with the Bibcom tool "+bibcom_ver+"\n% Available on Github at https://github.com/sebhoof/bibcom\n\n"

    if token == "":
        print(
            "% No ADS token supplied in the script. Will now use INSPIRE as a fallback."
        )
        n_ads = len(ads)
        if n_ads > 0:
            print(
                "% Note that {:d} reference(s) with ADS keys will not be added because of this.".format(
                    n_ads
                )
            )
        n_total = sum([len(p) for p in payloads[:-1]])
        if n_total > 7:
            print(
                "% WARNING. The INSPIRE API is limited to 15 queries/5 sec (need 2 queries/entry)."
            )
            print(
                "% {:d} reference(s) requested; will create the file 'dummy_file.tex' in the current directory instead.".format(
                    n_total
                )
            )
            print(
                "% Please upload it to https://inspirehep.net/bibliography-generator to generate a bibliography."
            )
            dummy_tex_file = open("dummy_file.tex", "w")
            for p in payloads[:-1]:
                for e in p:
                    dummy_tex_file.write("\cite{{{:s}}}\n".format(e))
            dummy_tex_file.close()
        else:
            for x in arxiv:
                r = requests.get(inspire_api_url + "arxiv/" + str(x))
                bib_entries += reformat_inspire_entry(r, x)
            for x in doi:
                r = requests.get(inspire_api_url + "doi/" + str(x))
                bib_entries += reformat_inspire_entry(r, x)
            for x in inspire:
                # The INSPIRE API cannot handle INSPIRE TeX keys; need to perform a regular query instead
                r = requests.get(inspire_api_url + "literature?q=" + str(x))
                bib_entries += reformat_inspire_entry(r, x)
    else:
        print(
            "% ADS token supplied. Will use ADS where possible to create bib entires."
        )
        if len(arxiv) > 0:
            # Allow both plain ArXiv numbers or prepended by e.g. "arXiv:" or "arxiv:"
            arxiv_mod = [x if x[:2] == "ar" else "arXiv:" + x for x in arxiv]
            bib_entries += reformat_ads_entries(arxiv_mod, arxiv)
        if len(doi) > 0:
            # Allow both plain DOIs or prepended by "doi:"
            doi_mod = [x if x[:3] == "doi" else "doi:" + x for x in doi]
            bib_entries += reformat_ads_entries(doi_mod, doi)
        if len(ads) > 0:
            bib_entries += reformat_ads_entries(ads, ads)
        n_inspire = len(inspire)
        if n_inspire > 7:
            dt = 5 * (n_inspire // 7)
            if dt > 60:
                dt = "{:.1f} minutes".format(dt / 60.0)
            else:
                dt = "{:.0f} seconds".format(dt)
            print(
                "% WARNING. The INSPIRE API is limited to 15 queries/5 sec but {:d} TeX keys need to be identified.".format(
                    n_inspire
                )
            )
            print(
                "%          Need 2 queries/key, so this will take about {:s} (unless there are more errors).".format(
                    dt
                )
            )
        for i, x in enumerate(inspire):
            if (i > 0) and (i % 7) == 0:
                time.sleep(5)
            try:
                r = requests.get(inspire_api_url + "literature?q=" + str(x))
            except:
                print(
                    "% An error occured while querying INSPIRE. Website may unavailable."
                )
                continue
            temp = reformat_inspire_entry(r, x)
            num_at_symbols = len(temp.split("@")) - 1
            if num_at_symbols != 1:
                if num_at_symbols == 0:
                    print(
                        "% WARNING. {:s} looks like an INSPIRE key since it contains a ':', but I could find an INSPIRE entry.".format(
                            x
                        )
                    )
                else:
                    print(
                        "% WARNING. {:s}  looks like an INSPIRE key since it contains a ':', but {:d} different INSPIRE entries were found. Please check this key manually.".format(
                            x, num_at_symbols
                        )
                    )
                continue
            else:
                # Try to get ADS entries via arXiv ID or DOI
                arxiv_id = temp.split('eprint = "')
                doi_id = temp.split('doi = "')
                if len(arxiv) == 2:
                    arxiv_id = arxiv_id[1].split('",')[0]
                    bib_entries += reformat_ads_entries(["arXiv:" + arxiv_id], [x])
                elif len(doi_id) == 2:
                    doi_id = doi_id[1].split('",')[0]
                    bib_entries += reformat_ads_entries(["doi:" + doi_id], [x])
                else:
                    print(
                        "% Could not get an ADS entry for {:s}; use the result from INSPIRE instead.".format(
                            x
                        )
                    )
                    bib_entries += temp

    # Copy the bibfile to the clipboard
    pyperclip.copy(bib_entries)

    # Print results if requested
    if print_results:
        print("% Bib entries:")
        print(bib_entries)

    # Append to bibfile if requested
    if bibfile != "":
        # If the file does not exist, create it; else append to it
        with open(bibfile, "a") as f:
            f.write(bib_entries)
    return bib_entries.count("@")


# If the script is run directly, run the main function
if __name__ == "__main__":
    print("% Compiling a bibliography for missing BibTeX entries with BibCom "+bibcom_ver)
    lfile = "main.log"
    bfile = ""
    if len(sys.argv) > 1:
        # Interate over sys.argv and match arguments to their function
        for a in sys.argv[1:]:
            if "log" in a:
                lfile = a
            if "bib" in a:
                bfile = a
            if "token" in a:
                try:
                    with open(a, "r") as f:
                        token = f.readline().split("\n")[0]
                except FileNotFoundError as not_found:
                    print(
                        "\n% ERROR! File",
                        not_found.filename,
                        "could not be found!\n% ADS token will not be loaded.\n",
                    )

    message = "% Will read log file {:s}".format(lfile)
    if bfile != "":
        message += ", append the results to the bib file {:s},".format(bfile)
    print(message + " and copy the results to the clipboard.")

    payloads = create_payloads(lfile)
    reqs = sum([len(l) for l in payloads[:-1]])
    successes = compile_bibliography(payloads, bibfile=bfile)

    nn = payloads[-1]
    if len(nn) > 0:
        print("% WARNING. Found {:d} unidentifiable bib code(s):".format(len(nn)), nn)

    if bfile != "":
        check_bib_file_for_duplicates(bfile)

    print(
        "All done. Found and created {:d} bib {:s} ({:d} requested).".format(
            successes, ("entry" if successes == 1 else "entries"), reqs
        )
    )
