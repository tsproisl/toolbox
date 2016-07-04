#!/usr/bin/env python3
# Submodule name: extract_metadata.py

"""
Submodule with functions for reading selected text from TEI files.
To use the function of this file you have to import extract as library
@author: Christof Schöch
"""

import re
import os
import glob
from lxml import etree
import pandas as pd

def from_TEIP5(wdir, inpath, metadatafile, mode="opt-obl"):
    """
    Extracts metadata from the CLiGs teiHeader and writes it to CSV.
    mode (string): "obl", "obl-opt" or "beta-opt-obl".
    Example of how to use this function:
        from toolbox.extract import get_metadata        
        get_metadata.from_TEIP5("/home/jose/cligs/ne/","master/*.xml","metadata","beta-opt-obl")

    """

    ## USER: Set list of metadata items to extract (see xpaths for list)
    ## We can choose only the obligatory metadata, the optional or the beta. 
    ## labels = ("idno_header","author_short","author_viaf", "author-gender", "title_short", "title_viaf", "pub_year", "supergenre", "genre", "subgenre", "genre-label", "narration", "availability")
     
    labels_obl = ["idno","author-name", "author-gender", "title", "year", "supergenre", "genre",   "genre-subtitle", "availability"]
    labels_opt = ["subgenre","genre-label","narrative-perspective", "narrator","protagonist-gender","setting","subsubgenre","form"]
    labels_beta = [ "author-country", "author-continent",  "group-text", "subgroup-text","protagonist-name", "protagonist-social-level", "representation", "setting-continent", "setting-country", "setting-name", "setting-territory", "subgenre-lithist", "text-movement", "time-period", "time-span", "author-text-relation", "protagonist-profession","type-end","time-year","subgenre-edit","keywords-cert","author-period"]
    
    ## Dictionary of all relevant xpaths with their labels
    xpaths = {
              "title": '//tei:title[@type="short"]//text()',
              "author-name": '//tei:author//tei:name[@type="short"]//text()', 
              "author_viaf":'//tei:author//tei:idno[@type="viaf"]//text()',
              "author-gender":'//tei:term[@type="author-gender"]//text()',
              "title_viaf":'//tei:title//tei:idno[@type="viaf"]//text()',
              "year":'//tei:bibl[@type="edition-first"]//tei:date//text()',
              "supergenre":'//tei:term[@type="supergenre"]//text()',
              "genre": '//tei:term[@type="genre"]//text()',
              "genre-subtitle":'//tei:title[@type="sub"]//text()',
              "idno": '//tei:idno[@type="cligs"]//text()',
              "availability": '//tei:availability//@status',
              "author-country": '//tei:term[@type="author-country"]//text()',
              "author-continent": '//tei:term[@type="author-continent"]//text()',
              "genre-label":'//tei:term[@type="genre-label"]//text()',
              "narrative-perspective": '//tei:term[@type="narrative-perspective"]//text()',
              "narrator": '//tei:term[@type="narrator"]//text()',
              "setting": '//tei:term[@type="setting"]//text()',
              "protagonist-gender": '//tei:term[@type="protagonist-gender"]//text()',
              "subgenre":'//tei:term[@type="subgenre"][@subtype > parent::tei:keywords/tei:term[@type="subgenre"]/@subtype or not(parent::tei:keywords/tei:term[@type="subgenre"][2])]//text()',
              "subsubgenre":'//tei:term[@type="subsubgenre"]//text()',
              "protagonist-name": '//tei:term[@type="protagonist-name"]//text()',
              "protagonist-social-level": '//tei:term[@type="protagonist-social-level"]//text()',
              "representation": '//tei:term[@type="representation"]//text()',
              "setting-continent": '//tei:term[@type="setting-continent"]//text()',
              "setting-country": '//tei:term[@type="setting-country"]//text()',
              "setting-name": '//tei:term[@type="setting-name"]//text()',
              "setting-territory": '//tei:term[@type="setting-territory"]//text()',
              "subgenre-lithist":'//tei:term[@type="subgenre-lithist"][1]//text()',
              "text-movement": '//tei:term[@type="text-movement"]//text()',
              "time-period": '//tei:term[@type="time-period"]//text()',
              "time-span": '//tei:term[@type="time-span"]//text()',
              "group-text": '//tei:term[@type="group-text"]//text()',
              "subgroup-text": '//tei:term[@type="subgroup-text"]//text()',
              "author-text-relation": '//tei:term[@type="author-text-relation"]//text()',
              "protagonist-profession": '//tei:term[@type="protagonist-profession"]//text()',
              "type-end": '//tei:term[@type="type-end"]//text()',
              "time-year": '//tei:term[@type="time-year"]//text()',
              "subgenre-edit": '//tei:term[@type="subgenre-edit"][1]//text()',
              "keywords-cert": '///tei:keywords/@cert',
              "form": '//tei:term[@type="form"]//text()',
              "author-period": '//tei:term[@type="author-period"]//text()',
              }

    # Mode is selected: obligatory, optional or beta
    if mode =="obl":
        labels=labels_obl
    elif mode =="opt-obl":
        labels=labels_obl+labels_opt
    elif mode =="beta-opt-obl":
        labels=labels_obl+labels_opt+labels_beta
            
    namespaces = {'tei':'http://www.tei-c.org/ns/1.0'}
    idnos = []
    
    ## Get list of file idnos and create empty dataframe
    for file in glob.glob(wdir + inpath):
        idno_file = os.path.basename(file)[0:6]
        idnos.append(idno_file)
    metadata = pd.DataFrame(columns=labels, index=idnos)
    #print(metadata)

    ## For each file, get the results of each xpath
    for file in glob.glob(wdir + inpath):
        #print(file)
        xml = etree.parse(file)
        ## Before starting, verify that file idno and header idno are identical.
        idno_file = os.path.basename(file)[0:6]
        idno_header = xml.xpath(xpaths["idno"], namespaces=namespaces)[0]
        if idno_file != idno_header: 
            print("Error: "+ idno_file+ " = "+idno_header)
        for label in labels:
            xpath = xpaths[label]
            result = xml.xpath(xpath, namespaces=namespaces)
            ## Check whether something was found; if not, let the result be "n.av."
            if len(result) == 1: 
                result = result[0]
            else: 
                result = "n.av."
            ## Write the result to the corresponding cell in the dataframe
            metadata.loc[idno_file,label] = result
                
    ## Add decade column based on pub_year
    metadata["decade"] = metadata["year"].map(lambda x: str(x)[:-1]+"0s")
    
    ## Check result and write CSV file to disk.
    #print(metadata.head())
    metadata=metadata.sort("idno",ascending=True)  
    metadatafile=metadatafile+"_"+mode+".csv"
    metadata.to_csv(wdir+metadatafile, sep=",", encoding="utf-8")
    print("Done. Number of documents and metadata columns:", metadata.shape)


def from_TEIP4(teiFolder, metadataFile, labels):
    """
    Extracts metadata from the TEI P4 teiHeader and writes it to CSV.
    """
    
    ## Dictionary of all relevant xpaths with their labels
    xpaths = {
              "idno-cligs": '//idno[@type="cligs"]//text()',
              "author-name": '//author//text()', 
              "title-full": '//title//text()',
              "year-ref":'//date//text()',
              "year-doc":'//docDate/@value',
              "subgenre": '//genre//text()',
              "inspiration": '//inspiration//text()',
              "structure": '//structure//text()',
              "formal-type": '//type//text()',
              "idno-tc": '//idno[@type="tc"]//text()'
              }
            
#    namespaces = {'tei':'http://www.tei-c.org/ns/1.0'}
    idnos = []
    
    ## Get list of file idnos and create empty dataframe
    teiPath = teiFolder + "*.xml"
    for file in glob.glob(teiPath):
        idno_file, ext = os.path.basename(file).split(".")
        idnos.append(idno_file)
    metadata = pd.DataFrame(columns=labels, index=idnos)
    #print(metadata)

    ## For each file, get the results of each xpath
    for file in glob.glob(teiPath):
        idno_file, ext = os.path.basename(file).split(".")
        print(idno_file) 
        #parser = etree.XMLParser(encoding="utf-8")
        #xml = etree.parse(file, parser)
        xml = etree.parse(file)
        for label in labels:
            xpath = xpaths[label]
            result = xml.xpath(xpath)
            #print(result)
            ## Check whether something was found; if not, let the result be "n.av."
            if len(result) != 0: 
                result = result[0]
            else: 
                result = "n.av."
            ## Write the result to the corresponding cell in the dataframe
            metadata.loc[idno_file,label] = result
                
    ## Add decade column based on pub_year
    #metadata["decade"] = metadata["year"].map(lambda x: str(x)[:-1]+"0s")
    
    ## Check result and write CSV file to disk.
    print(metadata.head())
    #metadata = metadata.sort("idno",ascending=True)  
    metadata.to_csv(metadataFile, sep=",")
    print("Done. Number of documents and metadata columns:", metadata.shape)
    
    
def main(teiFolder, txtFolder, metadataFile, mode):
    from_TEIP5(txtFolder, metadataFile, mode) #The last value choose between the three modes: only obligatory, only optional (the normal mode) and beta
    from_TEIP4(teiFolder, metadataFile) 
    
if __name__ == "__main__":
    import sys
    from_TEIP5(int(sys.argv[1]))
    from_TEIP4(int(sys.argv[1]))
