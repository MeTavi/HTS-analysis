


def dbConnect(db_name):
    
    import pyodbc as pyo
    import os  

    cnxn = pyo.connect('DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};'.format(os.path.join(os.getcwd(),db_name)))
    cursor = cnxn.cursor();tabs = cursor.tables();tablelist = []
    for i in tabs:
        if i.table_name.startswith("MSys"):
            pass
        else:
            tablelist.append(i.table_name)
    return cnxn, cursor