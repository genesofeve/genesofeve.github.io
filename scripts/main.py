#!/usr/bin/env python
import json
import re
import shutil
import string
import urllib.request as request

from Bio import Entrez, Medline

# from RNASeq.misc import pp
from jinja2 import Environment, FileSystemLoader, exceptions

templateDir = "templates"
env = Environment(loader=FileSystemLoader([templateDir]))

##########################
# Publication Information
##########################
### Fetch publications
pmIDs = [
    "34329587",
    "32386599",
    "31128945",
    "34796337",
    "34353350",
    "34660940",
    "34433496",
    "30143323",
    "33113347",
    "33600760",
    "33985562",
    "32167521",
    "30753828",
    "35101061",
    "32375049",
    "28968850",
    "31337651",
    "31121116",
    "30988181",
    "31843893",
    "29792227",
    "33219090",
    "29342249",
    "28174896",
    "31002670",
    "26523645",
    "24233779",
    "27650546",
    "35358296",  # Chen 2stage LCA
    "36214223",
    "36881486",
    "37067199",
    "37080163",
    "37316665",
    "37591207",
    "37602211",
    "37885016",
    "37989764",
    "38587552",
    "39151428",
    "39271675",
    "39320351",
    "39341835",
    "39567770",
    "40085647",
]

pmIDs.sort(reverse=True)

print(f"Fetching {len(pmIDs)} publication records from Entrez...")
Entrez.email = "gsteinobrien@gmail.com"
handle = Entrez.efetch(db="pubmed", id=pmIDs, rettype="medline", retmode="text")

records = Medline.parse(handle)
print("\tDone")

##########Hannah################
# Preprint Information
##########################
### Fetch Preprints
preprintIDs = [
    "083717",
    "114025",
    "136564",
    "196915",
    "378950",
    "395004",
    "479287",
    "328807",
    "726547",
    "779694",
    "577544",
    "2020.03.13.990549",
    "2021.03.17.435870",
    "2021.08.25.457650",
    "2021.04.06.438463",
    "2021.03.22.435728",
    "2022.06.02.490672",
    "2022.06.15.495952",
    "2022.06.19.494717",  # RNA Velocity Study
    "2022.07.09.499398",  # pyCoGAPS
    "2022.07.14.500096",
    "2022.08.04.502825",
    "2023.09.17.557982",  # Digitize your biology
    "2024.02.26.581612",  # Carlo
    "2024.07.01.599554",  # mult NMF
    "2024.09.22.613714",  # multiomics spatial
]

preprintIDs = reversed(preprintIDs)


def fetchBioRxiv(preprintID):
    biorxiv_api_url = f"https://api.biorxiv.org/details/biorxiv/10.1101/{preprintID}"
    response = request.urlopen(biorxiv_api_url)
    data = json.loads(response.read())
    return data


# print(fetchBioRxiv(preprintIDs[0]))
print("Fetching Preprints from BioRxiv...")
preprints = [fetchBioRxiv(id)["collection"][0] for id in preprintIDs]
print(f"\t{len(preprints)} found")
# print(preprints[-1]

################
# Pages
################

pages = [
    ("/", "index", "", "Home"),
    # ('/', 'research', 'Experimental Biology','Research'),
    ("/", "people", "General", "People"),
    ("/", "publications", "Experimental Biology", "Publications"),
    ("/", "preprints", "Experimental Biology", "Preprints"),
    ("/", "teaching", "Teaching", "Teaching"),
    ("/", "software", "Computational Biology", "Software"),
    ("/", "datasets", "Computational Biology", "datasets"),
    ("/", "contact", "General", "Contact"),
    # ('/', 'about', 'General','About'),
    ("/", "join", "General", "Join"),
    # ('/', 'resources', 'General','Resources'),
    # ('/', 'links', 'General','Links'),
    # ('/', 'news', 'General', 'News')
    ("/", "blog", "General", "Blog"),
    ("/", "lab_resources", "General", "Lab Resources"),
]

# pp(list(records))


def pubs():
    template = env.get_template("pubs.html")
    outHandle = open(outFile, "w")
    print >> outHandle, template.render(records=list(records))


# def preprints():
#    template=env.get_template('preprints.html')


def renderPage(pageName, **kwargs):
    fname = pageName + ".html"
    template = env.get_template(fname)
    outHandle = open(fname, "w")
    # print >>outHandle, template.render(**kwargs)
    print(template.render(**kwargs), file=outHandle)


def nameBoldPubs(string):
    return re.sub(
        "Stein-O'Brien,? G\.? ?[L]?\.?,?",
        '<span class="font-weight-bold" style="font-size: 1.0rem"><u>Stein-O\'Brien GL</u></span>,',
        string,
    )


env.filters["nameBoldPubs"] = nameBoldPubs


def split_doi(string):
    if " [pii] " in string:
        return string.split(" [pii] ")[1]
    else:
        return string


env.filters["split_doi"] = split_doi


def biorxiv_logo(string):
    if string == "biorxiv":
        return 'bio<span style="color: red">R</span><sub><em>&Chi;</em></sub>iv'
    else:
        return string


env.filters["biorxiv_logo"] = biorxiv_logo

if __name__ == "__main__":
    for page in pages:
        try:
            if page[1] == "publications":
                renderPage(
                    page[1], activePage=page[1], pages=pages, records=list(records)
                )
            elif page[1] == "preprints":
                renderPage(
                    page[1], activePage=page[1], pages=pages, preprints=preprints
                )
            else:
                renderPage(page[1], activePage=page[1], pages=pages)
        except exceptions.TemplateNotFound:
            print("No good template for %s" % (page[1]))
            # shutil.copy(templateDir+"/min.template",templateDir+"/"+page[1]+".html")
            # renderPage(page[1],activePage=page[1],pages=pages)
