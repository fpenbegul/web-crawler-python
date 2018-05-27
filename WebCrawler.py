#HTML Parser
from bs4 import BeautifulSoup
#Request para HTML
import urllib.request
#Conexoes ao Cloud
import psycopg2
import ssl
#Recompile
import re

#Metodos
#Abre a conexão IBM Cloud
def abrirConexaoCloud():
    try:
        conn = psycopg2.connect(host='sl-us-south-1-portal.25.dblayer.com',
                                port = 43023,
                                user = 'admin',
                                password = 'KFUQKGVJTVWHXELV',
                                database = 'postgres')
    except:
        print("Nao foi possivel conectar ao IBM Cloud")

    cur = conn.cursor()
    return conn, cur

#Caso o processamento seja efetuado com Sucesso, comita ao final da execução
def fechaConexao(resultado):
    if resultado == 'S':
       conn.commit()
    else:
       conn.rollback()
    cur.close()
    conn.close()

    #Verifica existencia da tabela, se negativo, cria, se positivo, dropa e cria novamente
def criaBase(nome_tabela):
    #Verifica se a tabela já existe
    cur.execute("SELECT 1 FROM information_schema.tables where table_name = lower('{0}')".format(nome_tabela))
    x = cur.fetchone()
    if 1 in x:
       cur.execute("TRUNCATE TABLE {0}".format(nome_tabela))
    else:
       cur.execute("CREATE TABLE " + nome_tabela + " (link text)")
    conn.commit()

    #Insere informações no DB
def insere(dados):
    cur.execute("INSERT INTO guardaLinks (link) VALUES ('{0}')".format(dados))

def leituraDados(tabela):
      cur.execute("SELECT * FROM {0}".format(tabela))
      y = []
      for x in cur:
          y.append(x[0])
      return y

#Abre a URL informada, recebe uma lista de Links
def webCrawler(url, lista_links):
    try:
        pagina = urllib.request.urlopen(url)
        #Realiza o parser no HTML da pagina solicitada
        BSoup = BeautifulSoup(pagina, "html.parser", from_encoding="iso-8859-1")
        #Varre o HTML da pagina para identificar outros links existentes
        for x in BSoup.findAll('a', attrs={'href': re.compile("^http://")}):
            next_link = x.get('href')
            if next_link not in lista_links:
                lista_links.append(next_link)
                insere(next_link)
                lista_links.append(webCrawler(next_link, lista_links))
    except:
        insere("Pagina nao acessivel")

######## Inicio ########

#Inicializa variaveis
lista = []
saida = []
tabela = "guardaLinks"

#URL de verificação
url = input("Digite a página web: ")
#url = 'http://www.google.com.br'

#String de Conexão
conn, cur = abrirConexaoCloud()

#Verifica se a tabela existe
criaBase(tabela)

#Inicia o Crawler
webCrawler(url, saida)

#Retorna os dados
links = leituraDados(tabela)
for x in range(len(links)):
    print(x, " - ", links[x])

resultado = "S"
fechaConexao(resultado)
print("Fim")
