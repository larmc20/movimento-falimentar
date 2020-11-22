# -*- coding: utf-8 -*-
"""Módulo de funções de tratamento de texto com Regex
"""
# Third part imports
import re
import os
import datetime
import requests
import json


def busca_cnpj(cnpj: str):
    try:
        if "." in cnpj or "/" in cnpj or "-" in cnpj:
            cnpj = cnpj.replace('.', '').replace('-', '').replace('/', '')

        url = "https://api.consultasdeveiculos.com/empresas/informacoes"
        payload = f'auth_token=66AD9A7E-F701-4433-955A-232C9D1DA4A3&cnpj={cnpj}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.text.encode('utf8')
        response = json.loads(response)
        return response
    except:
        busca_cnpj()


def tratamento_texto(lista_movimento: list, data: str, bd: object):
    empresas = []
    conn2 = bd.create_connection(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                                 'cidades_estados.db'))
    cursor2 = conn2.cursor()

    for frases in lista_movimento:
        if 0 < len(frases) < 100:
            if ("Falências" in frases or "Extrajudiciais" in frases or "Judiciais" in frases or "Homologações" in frases
                or "Concordatas" in frases or "Concordata" in frases or "Judicial" in frases or "Desistência" in frases
                or "Reformas de" in frases or 'Falência' in frases or "Processos" in frases):
                categoria = frases

        elif "Requerida:" in frases or "Requerido:" in frases or "Empresa:" in frases:
            # empresa
            empresa = re.findall(r':\s(.*?)\s-', frases)
            if len(empresa) > 1:
                empresa = empresa[0]

            # Admin Jud
            if len(re.findall(r'Judicial:\s(.*?)\-', frases)) == 0:
                adm = ""
            else:
                adm = re.findall(r'Judicial:\s(.*?)\-', frases)[0]
                if ',' in adm:
                    adm = re.findall(r',\s(.*)', adm)[0]
                    if 'Representad' in adm:
                        try:
                            adm = re.findall(r'Representad\w.Pel\w\s(.*)', adm)[0]
                        except IndexError:
                            adm = ""
            # Vara
            vara = re.findall(r'd\w\s(.*?)\/', frases)
            maior_city = ""

            cidade = cursor2.execute("SELECT nome FROM Cidades")

            try:
                for city in cidade:
                    if city[0] in vara[len(vara)-1] and len(city[0]) > len(maior_city):
                        maior_city = city[0]
                if len(maior_city) < 2:
                    maior_city = vara[len(vara)-1]
            except IndexError:
                maior_city = ""

            # UF
            try:
                uf = re.findall(r'\/(.[A-Z])', frases)
            except IndexError:
                uf = [""]

            # CNPJ
            try:
                cnpj = re.findall(r'CNPJ:\s(.*?)\s', frases)[0]
            except IndexError:
                cnpj = ""

            if len(cnpj) > 3:
                busca = busca_cnpj(cnpj)

            try:
                if "não encontrado" in busca["msg"]:
                    print("cnpj: ", cnpj, " não encontrado")
                    pedido = {"Categoria do pedido": categoria,
                              "Data do pedido": datetime.datetime.strptime(data, '%d/%m/%Y').strftime("%Y/%m/%d"),
                              "Vara do pedido": maior_city,
                              "Uf do pedido": uf[0],
                              "Administrador judicial": adm,
                              "CNPJ": cnpj,
                              "Razão social": empresa.strip(),
                              "Nome fantasia": "",
                              "Situação": "",
                              "Natureza": "",
                              "Logradouro": "",
                              "Bairro": "",
                              "CEP": "",
                              "Municipio": "",
                              "Estado": "",
                              "Complemento": "",
                              "Atividade Principal": "",
                              "Setor": "",
                              "Situação especial": "",
                              "capital social": 0}
            except KeyError:
                pedido = {
                        "Categoria do pedido": categoria,
                        "Data do pedido": datetime.datetime.strptime(data, '%d/%m/%Y').strftime("%Y/%m/%d"),
                        "Vara do pedido": maior_city,
                        "Uf do pedido": uf[0],
                        "Administrador judicial": adm,
                        "CNPJ": cnpj,
                        "Razão social": empresa,
                        "Nome fantasia": busca["result"]["nome_fantasia"],
                        "Situação": busca["result"]["situacao_nome"],
                        "Natureza": busca["result"]["natureza_juridica_nome"],
                        "Logradouro": busca["result"]["endereco"]["tipo_logradouro"] + " " +
                        busca["result"]["endereco"]["logradouro"] + " " +
                        busca["result"]["endereco"]["numero"],
                        "Bairro": busca["result"]["endereco"]["bairro"],
                        "CEP": busca["result"]["endereco"]["cep"],
                        "Municipio": busca["result"]["endereco"]["municipio"],
                        "Estado": busca["result"]["endereco"]["uf"],
                        "Complemento": busca["result"]["endereco"]["complemento"],
                        "Atividade Principal": busca["result"]["atividade_principal"],
                        "Setor": "",
                        "Situação especial": busca["result"]["situacao_especial"],
                        "capital social": busca["result"]["capital_social"]
                        }
            except UnboundLocalError:
                pedido = {
                        "Categoria do pedido": categoria,
                        "Data do pedido": datetime.datetime.strptime(data, '%d/%m/%Y').strftime("%Y/%m/%d"),
                        "Vara do pedido": maior_city,
                        "Uf do pedido": uf[0],
                        "Administrador judicial": adm,
                        "CNPJ": cnpj,
                        "Razão social": empresa.strip(),
                        "Nome fantasia": "",
                        "Situação": "",
                        "Natureza": "",
                        "Logradouro": "",
                        "Bairro": "",
                        "CEP": "",
                        "Municipio": "",
                        "Estado": "",
                        "Complemento": "",
                        "Atividade Principal": "",
                        "Setor": "",
                        "Situação especial": "",
                        "capital social": 0
                        }

            if len(pedido["Razão social"]) < 2:
                if isinstance(empresa, list):
                    try:
                        pedido["Razão social"] = empresa[0].strip()
                    except IndexError:
                        pedido["Razão social"] = empresa
            # Checando setor
            if len(str(pedido["Atividade Principal"])) > 0:
                try:
                    pedido["Setor"] = cursor2.execute(
                        f'SELECT def FROM cnaes WHERE cod_cnae = {str(pedido["Atividade Principal"]).strip()[0:2]};'
                                                    ).fetchall()[0][0][1:]
                except IndexError:
                    print("Não consta na lista do CNAE")
                    pedido["Setor"] = ""

            # Adicionando o pedido à lista das empresas
            empresas.append(pedido)
        else:
            pass

    conn2.close()
    return empresas