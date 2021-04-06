'''
Este website é igual uma livraria ou uma loja de livros
'http://books.toscrape.com/'
Eu passo por todas as páginas no site, pego as urls da cada livros
e pego as informações da cada livro:
Título, categoria, preço e quantidade no estoque
Depois eu salvo no MySQL.
Estou dando um intervalo de 1 segundo para a url de cada livro,
se você quiser remover fique a vontade.

Aviso: coloque a sua senha para fazer a conexão com o banco de dados
e confira se o database exista também, ou crie um.
'''

import requests
import time
from bs4 import BeautifulSoup
from mysql.connector import connect, Error
import re

connection = connect(host= '127.0.0.1', port= 3306, user= 'root',
                password= 'COLOQUE SUA SENHA', database= 'web_scraping',
                charset='utf8')

cursor = connection.cursor(buffered=True)

cursor.execute('''
CREATE TABLE IF NOT EXISTS livraria(
id INT AUTO_INCREMENT PRIMARY KEY,
title VARCHAR(1000) NULL,
category VARCHAR(100) NULL,
price DECIMAL(6,2) NULL,
inStock INT NULL)
''')
connection.commit()

def insertBookIfNotExists(bookTitle, bookCategory, bookCost, booksInStock):
    '''
    Confiro se o livro já existe no banco de dados,
    se não, eu o adiciono.
    '''
    cursor.execute('''SELECT * FROM livraria
    WHERE title = %(bookTitle)s AND category = %(bookCategory)s''',
    {'bookTitle': bookTitle, 'bookCategory': bookCategory})

    if cursor.rowcount == 0:
        cursor.execute('''
        INSERT INTO livraria
        (title, category, price, inStock)
        VALUES (%s, %s, %s, %s)''',
        (bookTitle, bookCategory, bookCost, booksInStock))
        connection.commit()

def getBeautifulSoupFromHTML(url):
    try:
        page = requests.get(url,headers={'User-Agent': 'Mozilla/5'})
    except requests.exceptions.RequestException as e:
        print(e.message)
        raise SystemExit(e)

    return BeautifulSoup(page.text, 'html.parser')

# coleto as informações do Livro e mando salvar no banco de dados
def getBookInfo(bookUrl):
    print(bookUrl)
    print('-'*40)

    bs = getBeautifulSoupFromHTML(bookUrl)
    book = bs.find('article', {'class': 'product_page'})

    # Título do Livro
    bookTitle = book.h1.get_text()

    # Categoria do Livro
    bookCategory = bs.find('ul', {'class': 'breadcrumb'}).find_all('li')[2].get_text().strip()

    # Preço do Livro
    costRegex = re.compile(r'(\d+)\.(\d{2})')
    bookPrice = costRegex.search(book.find('p', {'class': 'price_color'}).get_text()).group()

    # Quantos desse Livro tem no estoque
    findNumberRegex = re.compile(r'\d+')
    numberOfbooks = findNumberRegex.search(book.find('p', {'class': 'instock availability'}).get_text()).group()

    insertBookIfNotExists(bookTitle, bookCategory, bookPrice, numberOfbooks)

# Pego o endereço de cada Livro na página
def getAllBookFromPage(url):
    bs = getBeautifulSoupFromHTML(url)
    for link in bs.find_all('div', {'class': 'image_container'}):

        #Aqui eu reconstruo o url, porque nesse website os urls não estão uniformemente formatados
        bookUrlRegex = re.compile(r'[^/]+/index\.html$')
        bookUrl = 'http://books.toscrape.com/catalogue/{}'.format(bookUrlRegex.search(link.a['href']).group())
        getBookInfo(bookUrl)
        time.sleep(1)


def getPages(pageUrl):
    '''
    Depois de coletar as informações de cada livro nesta página,
    movo para próxima página, até que não existam mais páginas.
    '''
    getAllBookFromPage(pageUrl)

    bs = getBeautifulSoupFromHTML(pageUrl)
    nextPageLink = bs.find('li', {'class': 'next'})
    if nextPageLink != None:
        nextPageUrl = bs.find('li', {'class': 'next'}).a['href']

        #Aqui eu reconstruo o url, porque nesse website os urls não estão uniformemente formatados
        findPageRegex = re.compile(r'page.+(html$)')
        nextPage = 'http://books.toscrape.com/catalogue/{}'.format(findPageRegex.search(nextPageUrl).group())
        print('NEW PAGE')
        print(nextPage)
        print('-'*40)
        getPages(nextPage)


getPages('http://books.toscrape.com/')

cursor.execute('SELECT * FROM livraria LIMIT 10')
for row in cursor.fetchall():
    print(row)

cursor.execute('SELECT COUNT(id) FROM livraria')
print(cursor.fetchone())

cursor.close()
connection.close()
