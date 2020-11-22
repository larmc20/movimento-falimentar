"""Módulo para enviar e-mail
"""
# Third part imports
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import html
from openpyxl import load_workbook
import re

# Own Imports
from base.bd import BancoDados


class Email:
    """Classe para tratar com objetos de e-mail
    """

    def coletar_movimento_bd(self, data):
        conn = BancoDados.create_connection(self)
        cursor = conn.cursor()
        info = cursor.execute(f"""SELECT categoria, razao_social, cnpj, administrador_jud, vara_pedido, uf_pedido FROM
                              table_empresas WHERE data = \'{data}\'""").fetchall()
        return info

    
    def montar_html(self, lista: list, dados: dict):
        tabela = ""
        categoria = None
        for item in lista:
            if categoria != item[0]:
                categoria = item[0]
                if categoria == "Falências Decretadas" or categoria == "Recuperação Judicial Deferida" or categoria == 'Concordatas Preventivas Convoladas em Falência': 
                    tabela += '<tr class=\'cabecalho\'><td><h3 class=\'cat\'>{}</h3></td><td><h3>Administrador Judicial</h3></td><td><h3>Vara</h3></td><td><h3>UF</h3></td></tr>'.format(categoria)
                else:
                    tabela += '<tr class=\'cabecalho\'><td><h3 class=\'cat\'>{}</h3></td><td><h3></h3></td><td><h3>Vara</h3></td><td><h3>UF</h3></td></tr>'.format(categoria)
            
            if item[2].replace('.', '').replace('-', '').replace('/', '') in dados["clientes"]:
                tabela += f'<tr class=\'empresass_clientes\'><td>{item[1]}</td><td class=\'meio\'>{item[3]}</td><td class=\'meio\'>{item[4]}</td><td>{item[5]}</td></tr>'
            else:
                tabela += f'<tr class=\'empresass\'><td>{item[1]}</td><td class=\'meio\'>{item[3]}</td><td class=\'meio\'>{item[4]}</td><td>{item[5]}</td></tr>'      
        return tabela
        

    def enviar_email(self, html_email: str, dados: dict, data: str):

        message = MIMEMultipart("alternative")
        message["Subject"] = "Movimento Falimentar"
        message["From"] = dados["remetente"]
        message["To"] = ', '.join(dados["emails"])

        # Create the plain-text and HTML version of your message
        html = ("""\
            <html>
                <style>  
                    td {{border-bottom: 1pt solid lightgrey;padding: 4px;}}
                    tr.cabecalho {{background: lightgrey; text-align: center;}}
                    td.meio {{text-align: center;}}
                    table {{Style="Width:90%";border-collapse: collapse; }}
                    h3.cat {{text-align: left;}}
                    tr.empresass_clientes {{background: gold;}}
                </style> 
                <body>
                    <h2>Movimento Falimentar - {0}</h2>
                    <table>
                        {1}
                    </table>
                </body>
            </html>
            """).format(data,html_email)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)

        #PARA GMAIL
        if re.findall(r'\@(.*?)\.',dados["remetente"])[0].lower() == "gmail":
            try: 
                port = 465  # For SSL

                # Create a secure SSL context
                context = ssl.create_default_context()

                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(dados["remetente"], dados["senha email"])
                    server.sendmail(
                        dados["remetente"], dados["emails"], message.as_string()
                    )
            except smtplib.SMTPAuthenticationError:
                print('\n\n UM ERRO ECORREU!!!\n Pode ser duas coisas: \n senha ou nome de usuário incorretos \n ou \n Habilite o Less Secure apps no https://myaccount.google.com/lesssecureapps?pli=1 \n\n ')
            except smtplib.SMTPSenderRefused:
                print('O e-mail foi recusado pelo destinatário')
            except:
                print('Algum erro ocorreu ao enviar o e-mail')


        #Para E-mails OFFICE 365        
        else:
            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                #server.set_debuglevel(1)
                server.starttls(context=context)
                server.login(dados["remetente"], dados["senha email"])
                server.sendmail(
                    dados["remetente"], dados["emails"], message.as_string()
                )




if __name__ == "__main__":

    email = Email()
    print(email.coletar_movimento_bd())