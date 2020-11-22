"""Buscar Movimento falimentar do Valor Econômico
"""

# Third part imports
from sqlite3 import Error
from datetime import datetime, date

# Own Imports
from base.excel import ExcelStuffs
from base.crawling import Robo
from base.bd import BancoDados
from base.regexstr import tratamento_texto
from base.email import Email
from base.comandos import update_progress


def movimento_existente(data: str):
    tarefas = 5
    update_progress(0, tarefas, "Alocando objetos                                       ")
    email = Email()
    excel = ExcelStuffs()
    update_progress(1, tarefas, "checando planilhas                                     ")
    excel.checar_plan()
    update_progress(2, tarefas, "Coletando dados das planilhas                          ")
    dados = excel.coletando_dados()
    update_progress(3, tarefas, "coletando informações do banco                         ")
    movimento = email.coletar_movimento_bd(data)
    update_progress(4, tarefas, "Criando HTML                                           ")
    html_email = email.montar_html(movimento, dados)
    update_progress(5, tarefas, "Enviando E-mail                                        ")
    email.enviar_email(html_email, dados, data)


def movimento_diario():
    """Função principal do sistema
    """
    tarefas = 12
    update_progress(0, tarefas, "Alocando objetos                                          ")
    email = Email()
    bd = BancoDados()
    excel = ExcelStuffs()
    robo = Robo()
    update_progress(1, tarefas, "Checando planilhas                                        ")
    excel.checar_plan()
    update_progress(2, tarefas, "Acessando Banco de dados                                  ")
    bd.criar_banco()
    update_progress(3, tarefas, "Coletando dados das planilhas                              ")
    dados = excel.coletando_dados()
    update_progress(4, tarefas, "Checando versões compatíveis - Chrome e Chromedriver     ")
    driver = robo.abre_driver()  # abre o driver
    robo.checa_versao(driver)
    update_progress(5, tarefas, "Logando no valor                                         ")
    robo.login_no_valor(dados['senha valor'], dados['loginvalor'], driver)
    update_progress(6, tarefas, "Acessando movimento                                      ")
    robo.acessando_movimento(driver)
    update_progress(7, tarefas, "procurando datas                                         ")
    data_movimento = robo.procurando_movimento(driver)

    if data_movimento == date.today().strftime('%d/%m/%Y'):
        update_progress(8, tarefas, "Coletando informações                                    ")
        lista_movimento = robo.coletando_informações(driver)
        update_progress(9, tarefas, "Tratando textos do movimento                             ")
        lista_movimento = tratamento_texto(lista_movimento, data_movimento, bd=bd)
        update_progress(10, tarefas, "Lançando dados no banco                                 ")

        # conecta banco
        try:
            conn = bd.create_connection()
            cursor = conn.cursor()
        except Error as err:
            print(err)

        if len(cursor.execute(
                    f"SELECT id_pedido FROM table_empresas WHERE data = \'{lista_movimento[1]['Data do pedido']}\'"
                            ).fetchall()) <= 0:

            for i in lista_movimento:
                # for z, n in i.items():
                #     print(z, ": ", n)
                # print('-=-'*30, '\n')

                cursor.execute(f"""INSERT INTO table_empresas (categoria, administrador_jud, vara_pedido, uf_pedido,
                        razao_social, situacao, natureza, logradouro, complemento, bairro, CEP, municipio, estado,
                        atividade_principal, situacao_especial, data, setor, cnpj, capital_social) VALUES
                        (\'{i["Categoria do pedido"]}\', \"{i['Administrador judicial']}\", \"{i['Vara do pedido']}\",
                        \"{i['Uf do pedido']}\", \"{i['Razão social']}\", \"{i['Situação']}\", \"{i['Natureza']}\",
                        \"{i['Logradouro']}\",\"{i['Complemento']}\", \"{i['Bairro']}\", \"{i['CEP']}\",
                        \"{i['Municipio']}\", \"{i['Estado']}\", \"{i['Atividade Principal']}\",
                        \"{i['Situação especial']}\", \"{i['Data do pedido']}\", \"{i['Setor']}\", \"{i['CNPJ']}\",
                        \"{i['capital social']}\");""")
            conn.commit()
            conn.close()
            print(f'\nRegistro do dia {lista_movimento[1]["Data do pedido"]} salvo no banco')
            data_movimento = datetime.strptime(data_movimento, '%d/%m/%Y').strftime("%Y/%m/%d")
            update_progress(11, tarefas, "Criando e-mail                                                ")
            movimento = email.coletar_movimento_bd(data_movimento)
            html_email = email.montar_html(movimento, dados)
            update_progress(12, tarefas, "Enviando E-mail                                               ")
            email.enviar_email(html_email, dados, data_movimento)

        else:
            print('\nRegistro existente')
    else:
        print("\nMovimento de hoje inexistente!")

    try:
        del lista_movimento
    except UnboundLocalError:
        pass

    try:
        del driver
    except UnboundLocalError:
        pass

    try:
        del cursor
    except UnboundLocalError:
        pass

    try:
        del html_email
    except UnboundLocalError:
        pass

    try:
        del dados
    except UnboundLocalError:
        pass

    try:
        del robo
    except UnboundLocalError:
        pass

    try:
        del excel
    except UnboundLocalError:
        pass

    try:
        del bd
    except UnboundLocalError:
        pass


# def movimento_continuo():
#     ExcelStuffs.checar_plan()
#     BancoDados.criar_banco()
#     dados = ExcelStuffs.coletando_dados()
#     driver = Robo.checa_versao()
#     Robo.login_no_valor(dados['senha valor'], dados['loginvalor'])
#     driver.get("https://www.valor.com.br/busca/Movimento%2Bfalimentar")
#     Robo.acessando_movimento()

#     wb = load_workbook("./links movimento.xlsx", read_only=True)
#     for i in range(2, 200):
#         if wb['Planilha1']["A{}".format(i)].value is None:
#             break
#         else:
#             link_valor = wb['Planilha1']["A{}".format(i)].value

#         # data_movimento = Robo.procurando_movimento(tipo=False,
#         #                  movimento_link=f'https://valor.globo.com/empresas/noticia/{d}/movimento-falimentar.ghtml')
#         data_movimento = Robo.procurando_movimento(tipo=False,
#                          movimento_link=link_valor)
#         # conecta banco
#         try:
#             conn = BancoDados.create_connection()
#             cursor = conn.cursor()
#         except Error as err:
#             print(err)
#         if data_movimento is None:
#             continue
#         if len(cursor.execute(
#                 f"""SELECT id_pedido FROM table_empresas WHERE data = \'{datetime.strptime(
#                                                     data_movimento, '%d/%m/%Y').strftime("%Y/%m/%d")}\'"""
#                 ).fetchall()) > 0:
#             print(f"Registro {data_movimento} existente")
#             continue

#         lista_movimento = Robo.coletando_informações()
#         lista_movimento = tratamento_texto(lista_movimento, data_movimento)

#         try:
#             if len(cursor.execute(
#                 f"""SELECT id_pedido FROM table_empresas WHERE data = \'{lista_movimento[1]['Data do pedido']}\'"""
#                 ).fetchall()) <= 0:

#                 for i in lista_movimento:
#                     # for z, n in i.items():
#                     #     print(z, ": ", n)
#                     # print('-=-'*30, '\n')
#                     try:
#                         cursor.execute(
#                               f"""INSERT INTO table_empresas (categoria, administrador_jud, vara_pedido, uf_pedido,
#                         razao_social, situacao, natureza, logradouro, complemento, bairro, CEP, municipio, estado,
#                         atividade_principal, situacao_especial, data, setor, cnpj, capital_social) VALUES
#                         (\'{i["Categoria do pedido"]}\', \"{i['Administrador judicial']}\", \"{i['Vara do pedido']}\",
#                         \"{i['Uf do pedido']}\", \"{i['Razão social']}\", \"{i['Situação']}\", \"{i['Natureza']}\",
#                         \"{i['Logradouro']}\",\"{i['Complemento']}\", \"{i['Bairro']}\", \"{i['CEP']}\",
#                         \"{i['Municipio']}\", \"{i['Estado']}\", \"{i['Atividade Principal']}\",
#                         \"{i['Situação especial']}\", \"{i['Data do pedido']}\", \"{i['Setor']}\", \"{i['CNPJ']}\",
#                         \"{i['capital social']}\");""")

#                     except Error as e:
#                         print(e)
#                         input("Um erro ocorreu: ")

#                 conn.commit()
#                 conn.close()
#                 print("movimento do dia ", data_movimento, " lançado!")
#             else:
#                 print("dia ",data_movimento,' já registrado!')

#             del lista_movimento

#         except IndexError:
#             print(data_movimento,": Feriado forense ou sem movimento falimentar!!!")

#     wb.close()

if __name__ == "__main__":
    # movimento_existente("2020/03/06")
    movimento_diario()