import pandas as pd
import csv
import datetime as dt
import models as md

with open('PETR4_Options.csv', 'r', encoding='utf-8-sig') as theFile:
    reader = csv.reader(theFile)

    petr4_options = []
    for line in reader:
        serie = line[0]
        estilo = line[1]
        preco_exercicio = line[2]
        vencimento = dt.datetime.strptime(line[3], '%d/%m/%Y').date()
        petr4_options.append(md.PETR4(serie=serie,type=estilo,strike=preco_exercicio,due_date=vencimento))
        
    md.session.add_all(petr4_options)
    md.session.commit()

#