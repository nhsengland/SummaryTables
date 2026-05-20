import requests 
from selenium import webdriver
from bs4 import BeautifulSoup

def get_population_data(FYEAR):
    url='https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland'

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

    req = requests.get(url,headers)

    soup = BeautifulSoup(req.content,'html.parser')
    xls_code = soup.find_all('a',{'class':"btn btn--primary btn--thick"},href=True)

    fyear = str(FYEAR)

    for file in xls_code:
        if fyear in file['href'] and file['href'][-3:]=='xls':
            publication_url = 'https://www.ons.gov.uk'+file['href']

            r = requests.get(publication_url)

            with open("population.xls",'wb') as f:
                f.write(r.content)
            break
        else:
            continue

