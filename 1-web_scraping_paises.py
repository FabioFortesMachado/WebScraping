'''
Nesse script eu leio as informações dos países deste website
https://scrapethissite.com/pages/simple/
Depois eu salvo no MySQL.

Aviso: coloque a sua senha para fazer a conexão com o banco de dados
e confira se o database exista também, ou crie um
'''

import requests
from bs4 import BeautifulSoup
from mysql.connector import connect, Error
import re

connection = connect(host= '127.0.0.1', port= 3306, user= 'root',
                password= 'COLOQUE SUA SENHA', database= 'web_scraping',
                charset='utf8')

cursor = connection.cursor(buffered=True)

cursor.execute('''
CREATE TABLE IF NOT EXISTS countries(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100) NULL,
capital VARCHAR(100) NULL,
population INT NULL,
area INT NULL)
''')
connection.commit()

def insertCountryIfNotExists(countryName, countryCapital, countryPopulation, countryArea):
    '''
    Confiro se os dados já exitem no banco de dados
    Se não, os adiciono.
    '''
    cursor.execute('SELECT * FROM countries WHERE name = %(countryName)s AND capital = %(countryCapital)s',
        {'countryName': countryName, 'countryCapital': countryCapital})
    if cursor.rowcount == 0:
        cursor.execute('''
        INSERT INTO countries
        (name, capital, population, area)
        VALUES (%s, %s, %s, %s)''', (countryName, countryCapital, countryPopulation, countryArea))
        connection.commit()

def getBeautifulSoupFromHTML(url):
    try:
        page = requests.get(url,headers={'User-Agent': 'Mozilla/5'})
    except requests.exceptions.RequestException as e:
        print(e.message)
        raise SystemExit(e)

    bs = BeautifulSoup(page.text, 'html.parser')
    return bs

bs = getBeautifulSoupFromHTML('https://scrapethissite.com/pages/simple/')

# acesso as informações de cada país
countries = bs.find_all('div', {'class': re.compile(r'country$')})
for country in countries:
    name = country.h3.get_text().strip()
    capital = country.find('span', {'class': 'country-capital'}).get_text()
    population = int(country.find('span', {'class': 'country-population'}).get_text())
    area = int(float(country.find('span', {'class': 'country-area'}).get_text()))
    insertCountryIfNotExists(name, capital, population, area)


cursor.execute('SELECT * FROM countries LIMIT 5')
for row in cursor.fetchall():
    print(row)

cursor.execute('SELECT COUNT(id) FROM countries')
print(cursor.fetchone())

cursor.close()
connection.close()
