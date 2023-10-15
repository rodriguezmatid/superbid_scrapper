import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import gspread

gc = gspread.service_account('credentials.json')

# Open a sheet from a spreadsheet in one go
sheet = gc.open("Remates").sheet1

def extract_price_from_url(URL):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    # Inicializa el WebDriver sin especificar la ruta del ejecutable
    browser = webdriver.Chrome(options=chrome_options)

    browser.get(URL)

    try:
        precio_div = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "offer-bid-panel")))
        
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        precio_div_bs4 = soup.find("span", {"class": "lance-atual"})

        if precio_div_bs4:
            precio_raw = precio_div_bs4.text.strip()
            precio_match = re.search(r'(\d+[\d.,]*)', precio_raw)
            
            if precio_match:
                return precio_match.group(1)
        return None
    except Exception as e:
        return None
    finally:
        browser.quit()

def convert_to_float(number_str):
    # Remover puntos y reemplazar comas por puntos
    clean_number = number_str.replace('.', '').replace(',', '.')
    return float(clean_number)

for row_number in range(2, 127):
    link = sheet.cell(row_number, 9).value
    patente = sheet.cell(row_number, 7).value
    print(f"Procesando URL en fila {row_number}: {patente}")  # Agregar esta línea
    if link:
        price = extract_price_from_url(link)
        if price:
            float_price = convert_to_float(price)
            sheet.update_cell(row_number, 10, float_price)