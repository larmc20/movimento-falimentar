"""Módulo com as funções do banco de dados
"""
import sqlite3
from sqlite3 import Error
import os


class BancoDados:

    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'db.db')

    def create_connection(self, db_file: str = db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print('\n', e)

    def criar_banco(self, db_file: str = db_file):
        """Criar banco de dados
        """

        sql_criar_tabela_empresa = """ CREATE TABLE IF NOT EXISTS table_empresas(
                                        id_pedido integer PRIMARY KEY,
                                        data datetime default CURRENT_DATE,
                                        categoria text NOT NULL,
                                        administrador_jud text,
                                        vara_pedido text NOT NULL,
                                        uf_pedido text NOT NULL,
                                        razao_social text NOT NULL,
                                        cnpj text,
                                        situacao text,
                                        natureza text,
                                        logradouro text,
                                        complemento text,
                                        bairro text,
                                        CEP text,
                                        municipio text,
                                        estado text,
                                        atividade_principal text,
                                        setor text,
                                        situacao_especial text,
                                        capital_social integer
                                    );"""

        # create a database connection
        conn = BancoDados.create_connection(db_file)

        # create tables
        if conn is not None:

            # create empresa table
            BancoDados.create_table(self, conn, sql_criar_tabela_empresa)
        else:
            print('\n', "Error! cannot create the database connection.")

        conn.close()

    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print('\n', e)

    def salvar_banco(self, conn):
        pass
