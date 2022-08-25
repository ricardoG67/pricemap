import datetime
from pytz import timezone
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename='log_precios.txt',
    filemode='a',
    level=logging.INFO)

###################################
##### GET CURRENTLY TIME
###################################
def get_time(today = True):    
    ## now = datetime.datetime.now()
    est = timezone('EST')
        
    ## select date
    if today == True:
        now = datetime.datetime.now(est)
    
    ## 7 days ago
    else:
        now = datetime.datetime.now(est) - datetime.timedelta(days=6)
        
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    hour = '{:02d}'.format(now.hour)
    minute = '{:02d}'.format(now.minute)
    second = "{:02d}".format(now.second)

    ## join the values 
    current_date = '{}-{}-{}'.format(year, month, day)
    current_time = "{}:{}".format(hour, "00")

    return current_date, current_time

###################################
##### GET PRICES FROM RETAILERS
###################################    
def get_price_retail(uri, retail, sku):

    # FALTA IMPLEMENTAR TARJETA
    
    ###################################
    # PLAZA VEA
    ###################################
    if retail == "plaza_vea":
        try:
            ## define URl by SKU
            #definir si se cambia
            search_url = "https://www.plazavea.com.pe/Busca/?PS=20&cc=24&sm=0&PageNumber=1&O=OrderByScoreDESC&fq=alternateIds_RefId%3A" + sku

            #get the content of the image
            page = requests.get(search_url).content

            ## get the soup
            soup = BeautifulSoup(page,'lxml') ##html.parser
            
            ##########################
            ## get the price of the product
            price_html = soup.find("div", {"class":"Showcase__salePrice"})
            
            if (price_html) is None:
                logging.error(f"El scraping de precio plaza vea {sku} no aparece en el url: {uri}") 

            if price_html is not None:
                price = price_html.text

                #PRICE == PRICE ONLINE
                price = float(price.replace("S/","").replace("\n","").strip())
            else:
                price = None
            ########################
            ## price en tienda (presencial)
            
            #Si no encuentra es none
            price_tienda = soup.find("div", {"class":"Showcase__oldPrice Showcase__oldPrice"})
            
            if price_tienda is not None:
                price_tienda = price_tienda.text
                price_tienda = float(price_tienda.replace("S/","").replace("\n","").strip())

            ########################
            #FALTA TARJETA OH
            #SE DEBE INTEGRAR CON SELENIUM PARA TARJETA CON HTML: Showcase__ohPrice
            
            price_tarjeta = None

        except:
            price = None
            logging.error(f"PLAZA VEA Se coloco precio none en {sku} con url: {uri}")
            price_tienda = None
            price_tarjeta = None

    ###################################
    # WONG
    ###################################
    if retail == "wong":
        try:
            # define the URI/ES EL URL
            product_uri = uri

            # get the content of the image
            page = requests.get(product_uri).content

            # get the soup
            soup = BeautifulSoup(page, 'lxml')  # html.parser

            ##################
            # get the price of the product
            price_temp = soup.find('strong', {"class": "skuBestPrice"})
                            
            if price_temp is not None:
                price_temp = price_temp.text

                price = float(price_temp.replace("S/.", ""))
            else:
                price = None
                logging.error(f"El scraping de precio wong {sku} no aparece en el url: {uri}")

            ###############
            price_temp_tienda = soup.find('strong', {'class': 'skuListPrice'})

            if price_temp_tienda is not None:
                price_temp_tienda = price_temp_tienda.text

                price_tienda = float(price_temp_tienda.replace("S/. ", ""))
                if price_tienda == 0:
                    price_tienda = None
            else:
                price_tienda = None       
            
            ############### FALTA TARJETA CENCOSUD
            
            price_tarjeta = None
            
        except:
            price = None
            logging.error(f"WONG Se coloco precio none en {sku} con url: {uri}")
            price_tienda = None
            price_tarjeta = None

    ###################################
    # METRO
    ###################################
    if retail == "metro":
        try:
            # define the URI
            product_uri = uri

            # get the content of the image
            page = requests.get(product_uri).content

            # get the soup
            soup = BeautifulSoup(page, 'lxml')  # html.parser

            # get the price of the product
            price_temp = soup.find('strong', {"class": "skuBestPrice"})
            
            if (price_temp) is not None:
                price_temp = price_temp.text
                price = float(price_temp.replace("S/.", "")) 
                
            else:
                price = None
                logging.error(f"El scraping de precio metro {sku} no aparece en el url: {uri}")

            ###############
            price_temp_tienda = soup.find('strong', {'class': 'skuListPrice'})

            if price_temp_tienda is not None:
                price_temp_tienda = price_temp_tienda.text

                price_tienda = float(price_temp_tienda.replace("S/. ", ""))
                if price_tienda == 0:
                    price_tienda = None

            else:
                price_tienda = None
                    
            ############
            #FALTA INCORPORAR TARJETA CENCOSUD
            price_tarjeta = None
        except:
            price = None
            price_tienda = None
            price_tarjeta = None
            logging.error(f"METRO Se coloco precio none en {sku} con url: {uri}")

    ###################################
    # VIVANDA
    ###################################
    if retail == "vivanda":
        try:
            # get the content of the url
            page = requests.get(uri).content

            # get the soup
            soup = BeautifulSoup(page, 'lxml')  # html.parser

            # get price (Deberia ser asi, sin embargo, no se puede recoger el codigo fuente de vivanda)
            #price_integer = soup.find("span",{"class":"vivanda-product-price-1-x-currencyInteger vivanda-product-price-1-x-currencyInteger--shelfPrimarySellingPrice"}).text
            #price_decimal = soup.find("span",{"class":"vivanda-product-price-1-x-currencyFraction vivanda-product-price-1-x-currencyFraction--shelfPrimarySellingPrice"}).text
            #price = float(price_integer +"."+ price_decimal)

            ##############
            # get price (Vivanda guarda el precio en la etiqueta Meta)
            metas = soup.find_all("meta")
            for i in metas:
                try:
                    temp = i.get("content")
                    if (type(float(temp)) == float) and ("product:price:amount" in str(i)):
                        price = float(i.get("content"))
                except:
                    price = None
                    logging.error(f"VIVANDA Se coloco precio none en {sku} con url: {uri}")
                    
            #############
            price_tienda = soup.find_all("script")
            price_tienda[7] # --> "ListPrice":21.9
            
            price_tienda = re.findall(r'\"ListPrice\"\:[\w.]+',str(price_tienda[7]))
            
            if len(price_tienda) != 0:
                price_tienda = price_tienda[0][12:]
            else:
                price_tienda = None
                
            ############
            #listo, no tiene tarjeta
            
            price_tarjeta = None
            
        except:
            price = None
            price_tienda = None
            price_tarjeta = None
            logging.error(f"VIVANDA Se coloco precio none en {sku} con url: {uri}")

    ###################################
    # TOTTUS
    ###################################

    if retail == "tottus":
        try:
            # get the content of the url
            page = requests.get(uri).content

            # get the soup
            soup = BeautifulSoup(page, 'lxml')  # html.parser

            #######################
            # get price
            #Cuando solo hay 1 precio es una clase, cuando hay más de 1, es otra clase
            price_temp = soup.find('span', {"class": "list price medium cmrPrice"})
            if price_temp is not None:
                price_temp = price_temp.text.split("UN")[0].strip()
                price_temp = price_temp.replace("s/ ","").replace(" ","").replace("KG", "")
                if len(price_temp)!= 0:
                    price = float(price_temp)

            price_temp = soup.find('span', {"class": "list price medium currentPrice"})
            if price_temp is not None:
                price_temp = price_temp.text.split("UN")[0].strip()
                price_temp = price_temp.replace("s/ ","").replace(" ","").replace("KG", "")
                if len(price_temp)!= 0:
                    price = float(price_temp)

            else:
                price = None
            #######################
            price_tienda = soup.find('span', {"class": "list price medium small regularPrice"})
            if price_tienda is not None:
                price_tienda = (price_tienda.text).replace("P. Reg.: s/", "").split("UN")[0].replace("KG","")

            price_tienda = soup.find('span', {"class": "regularPrice"})
            if price_tienda is not None:
                price_tienda = (price_tienda.text).replace("P. Reg.: s/", "").split("UN")[0].replace("KG","")
                
            ######################
            #TARJETA CMR
            price_tarjeta = soup.find('span', {"class": "cmr price medium cmrPrice"})
            if price_tarjeta is not None:
                price_tarjeta = price_tarjeta.text.split("UN")[0].strip()
                price_tarjeta = price_tarjeta.replace("s/ ","")
                price_tarjeta = str(float(price_tarjeta)) + " CMR"
            
        except:
            price = None
            price_tienda = None
            price_tarjeta = None
            logging.error(f"TOTTUS Se coloco precio none en {sku} con url: {uri}")

    current_date, current_time = get_time()

    return sku, price, price_tienda, price_tarjeta, retail, current_date, current_time

