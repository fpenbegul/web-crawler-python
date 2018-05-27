#Criado por Duan Nunes Alves da Silva
#Twitter @duanpsycho
#HTML Parser
from bs4 import BeautifulSoup
#Request para HTML
import urllib.request
#Conexoes ao Cloud
import psycopg2
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
        cur = conn.cursor()
        status = 'Ok'
    except:
        print("Nao foi possivel conectar ao IBM Cloud")
        conn = []
        cur = []
        status = 'nOk'
    return conn, cur, status

#Fecha conexao se a conexao foi aberta com status ok
def fechaConexao(status):
    if status == 'Ok':
       conn.commit()
       conn.close()
       cur.close()

#Verifica existencia da tabela, se negativo, cria, se positivo, dropa e cria novamente
def criaBase(nome_tabela):
    cur.execute("SELECT 1 FROM information_schema.tables where table_name = lower('{0}')".format(nome_tabela))
    x = cur.fetchone()
    if 1 in x:
       cur.execute("TRUNCATE TABLE {0}".format(nome_tabela))
    else:
       cur.execute("CREATE TABLE {0} (link text)".format(nome_tabela))
    conn.commit()

#Insere informações no DB
def insere(dados, nome_tabela):
    cur.execute("INSERT INTO {0} (link) VALUES ('{1}')".format(nome_tabela, dados))

#Consulta DB para retornar os links inseridos
def leituraDados(tabela):
      cur.execute("SELECT * FROM {0}".format(tabela))
      y = []
      for x in cur:
          y.append(x[0])
      return y

#Abre a URL informada, recebe uma lista de Links e o nome da tabela
def webCrawler(url, lista_links, nome_tabela):
    try:
        pagina = urllib.request.urlopen(url)
        #Realiza o parser no HTML da pagina solicitada
        BSoup = BeautifulSoup(pagina, "html.parser", from_encoding="iso-8859-1")
        #Varre o HTML da pagina para identificar outros links existentes
        for x in BSoup.findAll('a', attrs={'href': re.compile("^http://")}):
            next_link = x.get('href')
            if next_link not in lista_links:
                lista_links.append(next_link)
                print(next_link)
                insere(next_link, nome_tabela)
                lista_links.append(webCrawler(next_link, lista_links, nome_tabela))
    except:
        insere("Pagina nao acessivel", nome_tabela)

######## Inicio ########

#Inicializa variaveis
saida = []
tabela = "guardaLinks"

#URL de verificação
url = input("Ex: http://www.google.com.br \n Digite a página web: \n ")

#String de Conexão
conn, cur, status = abrirConexaoCloud()

#Verifica se conexao foi realizada com Sucesso
if status == 'Ok':
    #Verifica se a tabela existe
    criaBase(tabela)

    #Inicia o Crawler
    webCrawler(url, saida, tabela)

    #Retorna os dados
    links = leituraDados(tabela)

    #Valida retorno do select
    if len(links) == 0:
        print("Nao foi encontrado nenhum link na pagina informada")
    else:
        for x in range(len(links)):
            print(x, " - ", links[x])
    # Fecha Conexao
    fechaConexao(status)
#fim do If

print("Fim")
