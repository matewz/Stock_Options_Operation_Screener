from sqlalchemy.sql.sqltypes import Date, DateTime, Float
from urllib.parse import quote_plus

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import credential as secret

# Código baseado na criação de Nato RSC. 
# Disponivel em: https://github.com/natorsc/databases-with-python/blob/master/mssql-server-sqlalchemy/models.py


my_secret = secret.Credential()
# String de conexão Windows Server.
parametros = (
    # Driver que será utilizado na conexão
    'DRIVER={ODBC Driver 17 for SQL Server};'
    # IP ou nome do servidor\Versão do SQL.
    'SERVER=.\SQLEXPRESS;'
    # Porta
    'PORT=1433;'
    # Banco que será utilizado.
    'DATABASE=' + my_secret.DataBase + ';'
    # Nome de usuário.
    'UID=' + my_secret.Login + ';'
    # Senha.
    'PWD=' + my_secret.Password)


# Convertendo a string para um padrão de URI HTML.
url_db = quote_plus(parametros)
# Conexão.
# Para debug utilizar echo=True
engine = create_engine('mssql+pyodbc:///?odbc_connect=%s' % url_db, echo=False)

# Criando uma classe "Session" já configurada.
# Session é instanciado posteriormente para interação com a tabela.
#Session = sessionmaker(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()


class PETR4(Base):
    """Cada classe representa uma tabela do banco"""
    # Nome da tabela, se a variável não for
    # declarada será utilizado o nome da classe.
    __tablename__ = 'PETR4_Options_List'
    stock_name = 'PETR4'
    # Colunas da tabela.
    # Série	Estilo	Preço de Exercício	Vencimento
    id = Column(Integer, primary_key=True)
    option_name = Column('option_name', String(10))
    type = Column('type', String(2))
    strike = Column('strike', Float())
    due_date = Column('due_date', Date)

    def __init__(self, serie, type, strike,due_date):
        """Construtor.
        Tabela de Opções do Ativo.
        :param option: (str).
        :param type: (str).
        :param strike: (float).
        :param due_date: (date).
        """
        self.option_name = serie
        self.type = type
        self.strike = strike
        self.due_date = due_date


class PETR4_OPTIONS(Base):
    """Cada classe representa uma tabela do banco"""
    # Nome da tabela, se a variável não for
    # declarada será utilizado o nome da classe.
    __tablename__ = 'PETR4_Options_Data'

    # Colunas da tabela.
    # Série	Estilo	Preço de Exercício	Vencimento
    id = Column(Integer, primary_key=True)
    stock_price = Column('stock_price', String(10))
    option_name = Column('option_name', String(10))
    strike = Column('strike', Float)
    deal_type_zone = Column('deal_type_zone', String(5))
    due_date = Column('due_date', Date)
    days_to_due_date = Column('days_to_due_date', Integer)
    timestamp_option = Column('timestamp_option', DateTime)
    updated_at = Column('updated_at', DateTime)
    last_tick = Column('last_tick', Float)
    bid = Column('bid', Float)
    ask = Column('ask', Float)

    def __init__(self, stock_price, option, strike,deal_type_zone,due_date,days_to_due_date,timestamp_option,updated_at,last_tick,bid,ask):
        """Construtor.
        Tabela de Opções do Ativo.
        :param stock_price: (str).
        :param option: (str).
        :param strike: (float).
        :param deal_type_zone: (str).
        :param due_date: (date).
        :param days_to_due_date: (str).
        :param timestamp_option: (datetime).
        :param updated_at: (datetime).
        :param last_tick: (float).
        :param bid: (float).
        :param ask: (float).
        """
        self.stock_price = stock_price
        self.option_name = option
        self.strike = strike
        self.deal_type_zone = deal_type_zone
        self.due_date = due_date
        self.days_to_due_date = days_to_due_date
        self.timestamp_option = timestamp_option
        self.updated_at = updated_at
        self.last_tick = last_tick
        self.bid = bid
        self.ask = ask



def init_db():
    Base.metadata.create_all(engine)

#if __name__ == "__main__":
    # Verificando se o driver do MS SQL Server está instalado. ODBC Driver 17 for SQL Server
#    print([x for x in pyodbc.drivers() if x.startswith('ODBC Driver 17 for SQL Server')])

    # Removendo todas as tabelas do banco.
    # Base.metadata.drop_all(engine)

    # Criando todas as tabelas.
    #Base.metadata.create_all(engine)