# -*- coding: utf-8 -*-
"""
Scraping tool for fanfiction metadata (panel data)
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd

#---------------EDIT THIS CODE FOR SCRAPING OTHER FICS------------------------#
#given a start link - the first page of the tag with all the filters you want
page = "https://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=hits&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=T&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=en&commit=Sort+and+Filter&tag_id=Naruto"
NumberOfPages = 5 #how many pages of fics to attempt to scrape
fileName = "naruto.csv" #name of final file

#--------------------Code for scraping AO3 placards----------------------------#
#make a list of all the pages that fit that tag limit list
def getPageList(startLink):
    links = [startLink]
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(startLink,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page)
    olist = soup.find("ol", {"class": "pagination actions"}) #first, title navi
    lis = olist.find_all("li")[0:(NumberOfPages+1)] #get the first 20 pages
    for l in lis:
        try:
            a = l.find("a", href = True)['href'] 
            links.append(("https://archiveofourown.org" + a))
        except: pass
    return links
allPages = getPageList(page)
print(allPages)

#From each of the pages, get all their fics and characteristics
def getFicCharacteristics(thisPage):
    #the columns of things we seek
    name = []
    ratings = []
    warnings = []
    fandom = []
    relationships = []
    characters = []
    freeforms = []
    words = []
    chapters = []
    comments = []
    collections = []
    kudos = []
    bookmarks = []
    
    #open the search results page 
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(thisPage,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page)
    
    #make a list of all the works on the page
    worksOnPage = soup.find_all("li", {"role": "article"})
    
    for w in worksOnPage:
        #get the title
        name.append(w.find("h4", {"class": "heading"}).find("a").string)
        #get the fandom
        fandom.append(w.find("h5", {"class": "fandoms heading"}).find("a").string)
        #get the rating and warnings
        requiredTags = w.find("ul", {"class": "required-tags"}).find_all("li")
        ratings.append(requiredTags[0].find("span", {"class": "text"}).string)
        warnings.append(requiredTags[1].find("span", {"class": "text"}).string)
        
        #get the rest of the tags as a list
        #relationships
        tags = w.find("ul", {"class": "tags commas"})
        try:
            ships = tags.find_all("li", {"class": "relationships"})
            shipString = ""
            for s in ships:
                shipString.extend(", ", s.find("a").string) #comma'd list of relationships
            relationships.append(shipString)
        except:
            relationships.append(".")
        
        #characters
        try:
            chars = tags.find_all("li", {"class": "characters"})
            charString = ""
            for c in chars:
                charString.extend(", ", c.find("a").string) #comma'd list of relationships
            characters.append(charString)
        except:
            characters.append(".")
        
        #freeform tags
        try:
            frees = tags.find_all("li", {"class": "freeforms"})
            freeString = ""
            for f in frees:
                freeString.extend(", ", f.find("a").string) #comma'd list of relationships
            freeforms.append(freeString)
        except:
            freeforms.append(".")
            
        #the statistics
        words.append(w.find("dd", {"class": "words"}).strings)
        try:
            chapters.append(int(w.find("dd", {"class": "chapters"}).find("a").string))
        except:
            chapters.append(1)
        try:
            collections.append(int(w.find("dd", {"class": "collections"}).find("a").string))
        except:
            collections.append(0)
        comments.append(int(w.find("dd", {"class": "comments"}).find("a").string))
        kudos.append(int(w.find("dd", {"class": "kudos"}).find("a").string))
        bookmarks.append(int(w.find("dd", {"class": "bookmarks"}).find("a").string))
        

    #merge together all our lovely columns
    dataDict = {"names": name, "fandoms": fandom, "ratings": ratings, "warnings": warnings,
                "relationships": relationships, "freeforms": freeforms, "words": words,
                "chapters": chapters, "comments": comments, "characters": characters,
                "collections": collections, "kudos": kudos, "bookmarks": bookmarks}
    dataSet = pd.DataFrame.from_dict(dataDict)

    return dataSet

fullSet = getFicCharacteristics(allPages[0])
allPages.pop(0)
if len(allPages) > 0:
    for a in allPages:
        data = getFicCharacteristics(a)
        fullSet = fullSet.append(data, ignore_index=True)
fullSet.to_csv(fileName)
