"""Aba para manipular Selenium
"""
# Third pard imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import os
import time
import platform
import datetime
from bs4 import BeautifulSoup

# Own imports
import base.comandos as comandos


class Robo:

    login_valor = '''https://login.globo.com/provisionamento/6668?url=&tam=WIDGET'''
    movimento_url = "https://www.valor.com.br/busca/Movimento%2Bfalimentar"

    # Path do driver
    driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'chromedriver')

    def abre_driver(self):
        driver = webdriver.Chrome(self.driver_path)
        return driver

    def login_no_valor(self, senha: str, login: str, driver: object, login_url: str = login_valor,
                        movimento_url: str = movimento_url):

        """Função que faz o login no Valor.com

        Args:
            senha (str): Senha da conta do Valor.com
            login (str): Login do Valor.com
            login_url (str, optional): Url da tela de login do 'Valor.com'. Defaults to login_valor.
            movimento_url (str, optional): Url do movimento falimentar do dia. Defaults to movimento_url.
            driver_path (str): Path to driver.

        Returns:
            Object: Retorna a instância do ChromeDriver em utilização
        """
        driver.get(login_url)
        time.sleep(2)
        driver.set_window_size(1000, 1000)
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="login"]').send_keys(login)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(senha)
        driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').click()
        time.sleep(2)

    def acessando_movimento(self, driver: object, movimento_url: str = movimento_url):
        """Função que identifica o botão de acesso simultâneo

        Args:
            driver (object, optional): Defaults to driver.
        """

        try:
            time.sleep(2)
            botao = driver.find_element_by_id('device-desktop')
            botao.click()
            time.sleep(4)
            driver.get(movimento_url)
        except ElementClickInterceptedException:
            Robo.acessando_movimento()        
        except NoSuchElementException:
            driver.get(movimento_url)

    def checa_versao(self, driver: object):
        """Função que checa se a versão do driver é compatível com a do Chrome.

        Args:
            driver (object, optional): Defaults to driver.
        """
        # comandos.clear_screen()
        if platform.system() == 'Linux':
            if not os.path.exists('./chromedriver'):
                print("ChromeDriver não encontrado!")
            else:
                str1 = driver.capabilities['browserVersion']
                str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
                if str1[0:2] != str2[0:2]:
                    input(f"Versão do Chrome: {str1}, versão do ChromeDriver: {str2}. Baixe a versão {str1[0:2]}" +
                          " do Driver no site\nhttps://chromedriver.chromium.org/downloads")
        else:
            if not os.path.exists('.\\chromedriver'):
                print("ChromeDriver não encontrado!")
            else:
                str1 = driver.capabilities['browserVersion']
                str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
                if str1[0:2] != str2[0:2]:
                    input(f"Versão do Chrome: {str1}, versão do ChromeDriver: {str2}. Baixe a versão {str1[0:2]}" +
                          " do Driver no site\nhttps://chromedriver.chromium.org/downloads")


    def procurando_movimento(self, driver: object, tipo: bool = True, movimento_link: str = None):
        """Função que procura o movimento falimento com a data desejada

        Args:
            driver (object, optional): Defaults to driver.
            tipo (Bool, optional): Se True, buscará o movimento do dia, se False,
                                   deve-se inserir o link do movimento.
        Returns:
            data_2 (str): É a data do movimento encontrado
        """
        if tipo is False:
            link_movimento = movimento_link
        else:
            link_movimento = None

        if link_movimento is None:
            Robo.acessando_movimento(self, driver)
            data_1 = driver.find_element_by_css_selector('div.widget--info__text-container > a')
            driver.get(data_1.get_attribute('href'))
        else:
            driver.get(link_movimento)

        try:
            data_2 = str(driver.find_element_by_css_selector('time').get_attribute('innerHTML').strip()[0:10])
        except NoSuchElementException:
            data_2 = None
        
        if 'Acesso Negado' in driver.find_elements_by_css_selector('h1')[0].text:
            input("Resolva o captcha e aperte Enter")

        return data_2

    def coletando_informações(self, driver: object):
        """Função que retorna o texto da página com as infos do movimento.

        Returns:
            movimento (list): lista com as informações do movimento
        """
        movimento = []
        movimento = driver.find_element_by_css_selector('div.mc-article-body').text.split('\n')
        # driver.quit()
        return movimento


if __name__ == "__main__":
    Robo()