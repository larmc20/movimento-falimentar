"""Comandos próprios
"""

import platform
import os
import sys
import time


def clear_screen():
    """Função para limpar o prompt.
    """
    if platform.system() == 'Linux':
        os.system('clear')
    else:
        os.system('cls')


def finalizar():
    print('\nMacro finalizada')
    os._exit(1)


def update_progress(tarefa, total_tarefas, mensagem: str = ''):
    """Barra de progresso

    Args:
        progress (float): % do progresso da barra
        mensagem (str, optional): Mensagem da tarefa em execução. Defaults to "Completed...".
    """
    progress = tarefa/total_tarefas
    barLength = 50 # Modify this to change the length of the progress bar
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        mensagem = "error: progress var must be float\r"
    else:    
        if progress < 0:
            progress = 0
            mensagem = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            mensagem = "Done...                                                   \r\n"
    block = int(round(progress*barLength,0))
    text = "\r[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(block/barLength*100), mensagem)
    print(text, end='', flush=True)



if __name__ == "__main__":
    barLength = 50
    tarefas = 10
    for i in range(tarefas + 1):
        if i/tarefas*100 < 20:
            mensagem = "teste 1"
        elif i/tarefas*100 < 30:
            mensagem = "teste 2"
        elif i/tarefas*100 < 50:
            mensagem = "teste 3"
        elif i/tarefas*100 < 70:
            mensagem = "teste 4"
        elif i/tarefas*100 < 90:
            mensagem = "teste 5"
        else:
            mensagem = "Done..."
        update_progress(i,tarefas, mensagem)
        time.sleep(0.31)