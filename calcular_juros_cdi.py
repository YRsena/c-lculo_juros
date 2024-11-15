import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import pandas as pd
import holidays
from datetime import datetime, timedelta
from bcb import sgs

# Função para obter o CDI de hoje ou de ontem
def obter_cdi():
    hoje = datetime.today().date()
    ontem = hoje - timedelta(days=2)
    
    try:
        # Tentativa de obter o CDI de hoje
        cdi = sgs.get({'cdi': 12}, start=hoje)
        return cdi.iloc[-1]['cdi'] / 100  # Dividir por 100 para transformar em percentual
    except Exception as e:
        # Caso não tenha o CDI de hoje, tenta o CDI de ontem
        cdi_ontem = sgs.get({'cdi': 12}, start=ontem)
        return cdi_ontem.iloc[-1]['cdi'] / 100  # Dividir por 100 para transformar em percentual

# Função para calcular o valor futuro com CDI
def calcular_valor_futuro(valor_investido, cdi_diario, dias):
    return valor_investido * (1 + cdi_diario) ** dias

# Função para calcular os dias úteis entre duas datas
def dias_uteis(ini_data, fim_data, ano):
    todos_os_dias = pd.date_range(start=ini_data, end=fim_data)
    feriados_brasil = holidays.Brazil(years=ano)
    
    dias_uteis = [dia for dia in todos_os_dias if dia.weekday() < 5 and dia not in feriados_brasil]
    return len(dias_uteis)

# Função para calcular os dias totais entre duas datas
def dias_totais(ini_data, fim_data):
    todos_os_dias = pd.date_range(start=ini_data, end=fim_data)
    return len(todos_os_dias)

# Função para calcular a taxa diária e depois calcular a taxa mensal
def calcular_taxa_mensal(pagamento_inicial, pagamento_final, data_inicio, data_fim):
    # Calcular a diferença percentual
    diferenca_percentual = (pagamento_final - pagamento_inicial) / pagamento_inicial
    
    # Calcular a diferença de dias úteis
    dias_uteis_diferenca = dias_uteis(data_inicio, data_fim, data_inicio.year)
    
    # Calcular a taxa diária
    taxa_diaria = diferenca_percentual / dias_uteis_diferenca
    
    # Calcular a taxa mensal (considerando 21 dias úteis por mês)
    taxa_mensal = taxa_diaria * 21
    return taxa_mensal

# Função chamada quando o botão "Calcular" é pressionado
def calcular():
    # Pegando os valores dos campos de entrada
    try:
        valor_investido = float(valor_acumulado_entry.get())
        
        # Obtendo o CDI diário
        cdi_diario = obter_cdi()

        # Convertendo as datas de string para datetime no formato yyyy-mm-dd
        data_inicio = datetime.strptime(calendar_inicio.get_date(), '%Y-%m-%d').date()
        data_fim = datetime.strptime(calendar_fim.get_date(), '%Y-%m-%d').date()

        # Calculando o número de dias úteis entre as datas
        dias_uteis_comprovados = dias_uteis(data_inicio, data_fim, data_inicio.year)
        
        # Calculando os dias totais entre as datas
        dias_totais_comprovados = dias_totais(data_inicio, data_fim)

        # Calculando o valor futuro com e sem o pagamento
        valor_futuro = calcular_valor_futuro(valor_investido, cdi_diario, dias_uteis_comprovados)

        # Pegando os valores de pagamento
        pagamento_com_juros = float(pagamento_com_juros_entry.get())
        pagamento_sem_juros = float(pagamento_sem_juros_entry.get())

        # Cálculo do valor futuro com pagamento de juros
        valor_futuro_com_pagamento_juros = valor_futuro - pagamento_com_juros
        
        # Cálculo do valor futuro considerando o pagamento sem juros
        valor_futuro_pagamento_sem_juros = (valor_investido - pagamento_sem_juros) * (1 + cdi_diario) ** dias_uteis_comprovados

        # Calculando a taxa mensal implícita
        taxa_mensal = calcular_taxa_mensal(pagamento_sem_juros, pagamento_com_juros, data_inicio, data_fim)

        # Exibindo os resultados
        resultado_label.config(text=f"Valor futuro com juros: R$ {valor_futuro:.2f}\n"
                                   f"Valor com pagamento de R$ {pagamento_com_juros} após {dias_uteis_comprovados} dias úteis: R$ {valor_futuro_com_pagamento_juros:.2f}\n"
                                   f"Valor futuro após pagar R$ {pagamento_sem_juros} agora: R$ {valor_futuro_pagamento_sem_juros:.2f}\n"
                                   f"Taxa mensal calculada: {taxa_mensal*100:.2f}%\n"
                                   f"Total de dias entre as datas: {dias_totais_comprovados}\n"
                                   f"Dias úteis entre as datas: {dias_uteis_comprovados}")
    except Exception as e:
        resultado_label.config(text=f"Erro: {str(e)}")  # Convertendo o erro para string para exibir

# Criando a janela principal
root = tk.Tk()
root.title("Calculadora de Rendimento com CDI")

# Adicionando widgets para entrada de dados
ttk.Label(root, text="Valor Acumulado (R$):").grid(row=0, column=0, padx=10, pady=5)
valor_acumulado_entry = ttk.Entry(root)
valor_acumulado_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="Data Início:").grid(row=1, column=0, padx=10, pady=5)
calendar_inicio = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
calendar_inicio.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Data Fim:").grid(row=2, column=0, padx=10, pady=5)
calendar_fim = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
calendar_fim.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Pagamento com Juros (R$):").grid(row=3, column=0, padx=10, pady=5)
pagamento_com_juros_entry = ttk.Entry(root)
pagamento_com_juros_entry.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(root, text="Pagamento sem Juros (R$):").grid(row=4, column=0, padx=10, pady=5)
pagamento_sem_juros_entry = ttk.Entry(root)
pagamento_sem_juros_entry.grid(row=4, column=1, padx=10, pady=5)

# Botão para calcular
calcular_button = ttk.Button(root, text="Calcular", command=calcular)
calcular_button.grid(row=5, column=0, columnspan=2, pady=10)

# Label para mostrar os resultados
resultado_label = ttk.Label(root, text="Resultado será exibido aqui.", justify="left")
resultado_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

# Iniciando a interface gráfica
root.mainloop()
