import sys
import time
import requests
import json
import pyperclip
import numpy as np

# User needs to supply their ADS token here
token = ""

def create_payloads(logfilename):
   log_file = open(logfilename, 'r')
   log_lines = log_file.read().split('\n')
   log_file.close()
   arxiv, inspire, doi, nn = [], [], [], []
   for l in log_lines:
      # Read the log file and find missing bib entries
      if 'Citation' in l:
         bibcode = l.split('`')[1].split('\'')[0]
         # DOIs should start with '10.'; check these first
         if bibcode[:3] == '10.':
            doi.append(bibcode)
         # Arxiv ID contains '.' or '/'
         elif ('.' in bibcode) or ('/' in bibcode):
            arxiv.append(bibcode)
         # Also allow INSPIRE TeX keys
         elif ':' in bibcode:
            inspire.append(bibcode)
         # Otherwise, the ID is not known
         else:
            nn.append(bibcode)
   return [arxiv, inspire, doi, nn]

def reformat_inspire_entry(request, new_key):
   data = request.json()
   bibstring = requests.get(data['links']['bibtex'])
   if len(bibstring) > 0: 
      t1, t2 = bibstring.text.split('{',1)
      t2, t3 = t2.split(',',1)
      return t1 + '{' + new_key + ',' + t3
   else:
      return ""

def reformat_ads_entries(bibcodes, original_keys):
   payload = { 'bibcode': bibcodes }
   serialized_payload = json.dumps(payload)
   data = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex", 
                        headers={'Authorization': 'Bearer ' + token},
                        data=serialized_payload)
   bibfile_lines = data.json()['export'].splitlines()
   keyword_type = "eprint"
   if bibcodes[0][0] == "d":
      keyword_type = "doi"
   for i in range(len(bibfile_lines)):
      l = bibfile_lines[i]
      if len(l) > 0:
         if l[0] == '@':
            tmp = l.split('{')
            i0 = i
            while not(keyword_type in l):
                i += 1
                l = bibfile_lines[i]
            id = l.split('{')[1][:-2]
            original_key = [s for s in original_keys if id in s][0]
            bibfile_lines[i0] = tmp[0] + '{' + original_key + ','
   return ''.join([b+'\n' for b in bibfile_lines])


def make_bib_file(payloads, bibfile="", print_results=False):
   arxiv, inspire, doi = payloads[:3]
   bib_entries = ""

   if token == "":
      print("# No ADS token supplied in the script. Will now use INSPIRE as a fallback.")
      n_total = sum([len(p) for p in payloads[:-1]])
      if n_total > 7:
         print("# WARNING: The INSPIRE API is limited to 15 queries/5 sec (need 2 queries/entry).")
         print("# {:d} entries requested; will create the file 'dummy_file.tex' in the current directory instead.".format(n_total))
         print("# Please upload it to https://inspirehep.net/bibliography-generator")
         dummy_tex_file = open('dummy_file.tex', 'w')
         for p in payloads[:-1]:
            for e in p:
               dummy_tex_file.write("\cite{{{:s}}}\n".format(e))
         dummy_tex_file.close()
      else:
         url = 'https://labs.inspirehep.net/api/'
         for x in arxiv:
            r = requests.get(url+'/arxiv/'+str(x))
            bib_entries += reformat_inspire_entry(r, x)
         for x in doi:
            r = requests.get(url+'/doi/'+str(x))
            bib_entries += reformat_inspire_entry(r, x)
         for x in inspire:
            # For some reason, the INSPIRE API cannot handle its own TeX keys
            # Need to perform a regular query instead
            r = requests.get(url+'/literature?q='+str(x))
            bib_entries += reformat_inspire_entry(r, x)
   else:
      print("# ADS token supplied. Will use ADS for all bib entries.")
      if len(arxiv) > 0:
         arxiv_mod = [x if x[0]=="a" else "arXiv:"+x for x in arxiv]
         bib_entries += reformat_ads_entries(arxiv_mod, arxiv)
      if len(doi) > 0:
         doi_mod = [x if x[0]=="d" else "doi:"+x for x in doi]
         bib_entries += reformat_ads_entries(doi_mod, doi)
      n_inspire = len(inspire)
      if n_inspire > 7:
         print("# WARNING: The INSPIRE API is limited to 15 queries/5 sec (need 2 queries/entry).")
         print("# {:d} entries requested; this will take about {:.0f} seconds".format(n_inspire, 5*n_inspire//7))
      for i,x in enumerate(inspire):
         if i % 8 == 0:
            time.sleep(5)
         r = requests.get(url+'/literature?q='+str(x))
         temp = reformat_inspire_entry(r, x)
         # Try to get ADS entries via arXiv ID or DOI
         arxiv_id = temp.split("eprint = \"")[1].split("\",")[0]
         doi_id = temp.split("doi = \"")[1].split("\",")[0]
         if len(arxiv_id) > 0:
            bib_entries += reformat_ads_entries(["arXiv:"+arxiv_id], x)
         elif len(doi_id) > 0:
            bib_entries += reformat_ads_entries(["doi:"+doi_id], x)
         else:
            print("# Could not get an ADS entry for {:s}; use INSPIRE instead.".format(x))
            bib_entries += temp

   # Copy the bibfile to the clipboard
   pyperclip.copy(bib_entries)

   # Print results if requested
   if print_results:
      print("# Bib entries:")
      print(bib_entries)

   # Append to bibfile if requested
   if bibfile != "":
      bibfile_obj = open(bibfile, 'a')
      bibfile_obj.write(bib_entries)
      bibfile_obj.close()


def check_bib_file_for_duplicates(bibfile):
   arxiv, doi = [], []
   print("# Checking bib file {:s} for duplicates...".format(bibfile))
   with open(bibfile, 'r') as f:
      for line in f:
         for e in line.split('@'):
            t = e.split("eprint = ")
            if len(t) > 1:
               arxiv.append(t[1].split(",\n")[0][1:-1])
            t = e.split("doi = ")
            if len(t) > 1:
               doi.append(t[1].split(",\n")[0][1:-1])
   s, c = np.unique(arxiv, return_counts=True)
   n_d_arxiv = sum(c > 1)
   if n_d_arxiv > 0:
      print("# WARNING: The following {:d} arXiv IDs are duplicated:".format(n_d_arxiv))
      print(s[c > 1])
   s, c = np.unique(doi, return_counts=True)
   n_d_doi = sum(c > 1)
   if n_d_doi > 0:
      print("# WARNING: The following {:d} DOI IDs are duplicated:".format(n_d_doi))
      print(s[c > 1])
   if n_d_arxiv + n_d_doi > 0:
      print("# Duplicates detected (see above)! Please remove them from the bib file.")
   else:
      print("# No duplicates detected!")
   

if __name__ == "__main__":
   lfile = "main.log"
   bfile = ""
   if len(sys.argv) > 1:
      for a in sys.argv[1:]:
         if "log" in a:
            lfile = a
         if "bib" in a:
            bfile = a
   
   print("# Generating bib file entries with the physics bib file creator tool v0.9")
   message = "# Will read log file {:s}".format(lfile)
   if bfile != "":
      message += ", append them to the bib file {:s},".format(bfile)
   print(message+" and copy them to the clipboard.")

   payloads = create_payloads(lfile)

   nn = payloads[-1]
   if len(nn) > 0:
      print("# There are {:d} unidentifiable bib codes. These are".format(len(nn)))
      print(nn)

   make_bib_file(payloads, bibfile=bfile)

   if bfile != "":
      check_bib_file_for_duplicates(bfile)
