import io
import os
import re
import pandas as pd
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def extract_from_datasource2(path_to_file):
    """
    INPUT: a path to the file
    OUTPUT: A list with elements related to a pdf check image
    check_details[1] = bank account #
    check_details[0] = amount $
    check_details[2] = routing #
    check_details[3] = check #
    """
    pdf_converted = convert_pdf_to_txt(path_to_file)
    
    if len(re.findall("\n\n\d+\...\n\n\d+\n\n\d+\n\n\d+\n\n\w+.\n\n\d+",pdf_converted)) <1:
        return ["0","0","0","0"]
    else:
        check_details = re.sub('[^0-9|.]',' ',re.findall("\n\n\d+\...\n\n\d+\n\n\d+\n\n\d+\n\n\w+.\n\n\d+",pdf_converted)[0].strip().replace("\n"," ")).split()
        #check_details = extract_hsbc("\n\n\d+\...\n\n\d+\n\n\d+\n\n\d+\n\n\w+.\n\n\d+",pdf_converted)
        final_list = [check_details[1], check_details[0], check_details[2], check_details[3]]

        account_flag = red_flag_pdf(final_list)
        final_list.append(account_flag)

        return final_list

def extract_datasource1(name, pdf_converted):
    """
    INPUT:
    OUTPUT:
    """
    if len(re.findall(name,pdf_converted)) < 1:
        return 0
    else:
        return re.sub('[^0-9]','', re.findall(name ,pdf_converted)[0].strip())

def datasource1(path_to_file):
    """
    INPUT: A path to a file
    OUTPUT: A list with elements related to a pdf check image
    ba_num = bank account #
    amt = amount $
    rt_num = routing #
    check_num = check #
    """
    
    pdf_converted = convert_pdf_to_txt(path_to_file).replace(",","")
    
    ba_num = extract_datasource1("Account number\n\d+",pdf_converted)
    rt_num = extract_datasource1("Cheque RT number\n\n\d+",pdf_converted)        
    check_num = extract_datasource1("\n\nSequence number\n\n\d+",pdf_converted)
    amt = extract_datasource1("\n\nAmount\n(\d+|\n\d+)",pdf_converted)
    
    final_list = [ba_num,amt,rt_num,check_num]
    
    account_flag = red_flag_pdf(final_list)
    final_list.append(account_flag)
    
    return final_list

def red_flag_pdf(list_of_check_details):
    """
    INPUT:
    OUTPUT:
    """
    if len(set(list_of_check_details)) == 1 or len(set(list_of_check_details))<=2 and 0 in set(list_of_check_details):
        return "1"
    else:
        return "0"

def make_dataframe(list_of_values):
    """
    INPUT:
    OUTPUT:
    """
    df = pd.DataFrame(list_of_values, columns=("account_number","amount","routing_number","check_number","red_flag"))
    return df


def accts_more_than_one(df):
    """
    PURPOSE: To determine if a given account number has more than one routing number 
    INPUT:A dataframe
    OUTPUT: A list
    """
    
    unusual_accnts = []
    for i in range(len(df)):
        acct_num = df.iloc[i].account_number
        accnt_dims = (df[df['account_number']== acct_num].shape)
        row , col = accnt_dims
        if row > 1:
            unusual_accnts.append(acct_num)

    return unusual_accnts


def route_more_than_one(df):
    """
    PURPOSE: To determine if a given routing number has more than one 
    INPUT:A dataframe
    OUTPUT: A list
    """
    unusual_routes = []
    for i in range(len(df)):
        route_num = df.iloc[i].routing_number
        route_dims = (df[df['routing_number']== route_num].shape)
        row , col = route_dims
        if row > 1:
            unusual_accnts.append(route_num)

    return unusual_routes
    
            
df_data = []

# arr = os.listdir('./folder2')
# for file in arr:
#     new_path = 'C:\\Users\\me\\Desktop\\folder2\\'+file
#     results = extract_from_datasource2(new_path)
#     df_data.append((results[0],results[1],results[2],results[3]))

arr = os.listdir('../folder')
for file in arr:
    new_path = 'C:\\Users\\me\\Desktop\\folder\\'+file    
    method_1 = hsbc(new_path)
    method_2 = extract_from_remitco(new_path)
    if len(set(method_1)) > len(set(method_2)):
        df_data.append(method_1)
    else:
        df_data.append(method_2)

df = make_dataframe(df_data)
# print (accts_more_than_one(df))
# print (route_more_than_one(df))
