#Criado por Duan Nunes Alves da Silva
#Twitter @duanpsycho
#HTML Parser
from bs4 import BeautifulSoup
#Request para HTML
import urllib.request
#Recompile
import re
#Conexao postgreSQL
import psycopg2

#Metodos
def abrirConexaoCloud():
    try:
        #Conexao postgreSQL
        conn = psycopg2.connect(host='SERVIDOR,
                                port='PORTA',
                                user='USUARIO',
                                password='SENHA',
                                database='BASE')
        cur = conn.cursor()
        status = 'Ok'
    except:
        print("Nao foi possivel conectar")
        conn = []
        cur = []
        status = 'nOk'
    return conn, cur, status

# Fecha conexao se ela foi aberta com status ok
def fechaConexao(conn, cur, status):
    if status == 'Ok':
        conn.commit()
        conn.close()
        cur.close()
        return True
    elif status == 'nOk':
        conn.rollback()
        conn.close()
        cur.close()
        return False

# Verifica existencia da tabela, se negativo, cria, se positivo, dropa e cria novamente
def criaBase(nome_tabela, conn, cur):
    try:
        cur.execute("select count(1) from pg_tables where tablename = lower('{0}')".format(nome_tabela))
        x = cur.fetchone()
        if 1 in x:
            cur.execute("TRUNCATE TABLE {0}".format(nome_tabela))
            conn.commit()
            return True
        else:
            cur.execute("CREATE TABLE {0} (link text)".format(nome_tabela))
            conn.commit()
            return True
    except:
        print("Nao eh possivel criar a base de dados")
        return False

# Insere informações no DB
def insere(nome_tabela, dados):
        try:
            cur.execute("INSERT INTO {0} (link) VALUES ('{1}')".format(nome_tabela, dados))
            return True
        except:
            print("Erro durante a insercao")
            return False

# Consulta DB para retornar os links inseridos
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
        for x in (BSoup.findAll('a', attrs={'href': re.compile("^http://")}) or BSoup.findAll('a', attrs={'href': re.compile("^https://")})):
            next_link = x.get('href')
            #Verifica se o link atual não está na lista
            if next_link not in lista_links:
                lista_links.append(next_link)
                valid = insere(nome_tabela, next_link)
                if valid == True:
                    lista_links.append(webCrawler(next_link, lista_links, nome_tabela))
                else:
                    break
    except:
        valid = insere(nome_tabela, "Pagina nao acessivel ou nao existe")

######## Inicio ########

# Inicializa variaveis
lista_links = []
tabela = "guardaLinks"

# URL de verificação
url = input("Ex: http://www.google.com.br \n Digite a página web: \n ")

# String de Conexão
conn, cur, status = abrirConexaoCloud()

# Verifica se conexao foi realizada com Sucesso
if status == 'Ok':
    # Verifica se a tabela existe
    valid = criaBase(tabela, conn, cur)

    if valid == True:
        # Inicia o Crawler
        webCrawler(url, lista_links, tabela)

        # Retorna os dados
        links = leituraDados(tabela)

        # Valida retorno do select
        if len(links) == 0:
            print("Nao foi encontrado nenhum link na pagina informada")
        else:
            for x in range(len(links)):
                print(x, " - ", links[x])
        # Fecha Conexao
        fechaConexao(conn, cur, status)
else:
    # Fecha Conexao
    fechaConexao(conn, cur, status)

# fim do If
print("Fim")
