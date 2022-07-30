from playsound import playsound
import cv2
from pyzbar.pyzbar import decode
import os
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import requests
import cv2
import numpy as np
import imutils

class Produto:

    def __init__(self, nome: float, preco, code, url: str):
        self.nome = nome
        self.preco = preco
        self.code = code
        self.url = url


class Supermercado:

    def __init__(self, nome: str):
        self.nome = nome
        self.lista_produtos = []

    def AdicionarProduto(self, nome_produto: str, preco: float, code: str, url: str):
        produto = Produto(nome_produto, preco, [code], url)
        self.lista_produtos.append(produto)

    def PesquisarProduto(self, code: str):
        
        for produto in self.lista_produtos:

            for codigo_produto in produto.code:

                if(code == codigo_produto):
                    return produto

        return False

class SuperKoch(Supermercado):

    def __init__(self):
        self.nome = "Super Koch"
        self.driver = None
        super().__init__(self.nome)

    def AbrirMercado(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://www.superkoch.com.br')
        sleep(2)
        element = driver.find_element(By.ID, 'stores')
        select = Select(element)
        select.select_by_value('website_lj47')
        driver.find_element(By.XPATH, '//*[@id="storeModal"]/div/div[3]/button').click()
        self.driver = driver

    def AdicionarProduto(self, urls):
        nome_produto = ""
        code = ""
        preco = 0.0

        self.AbrirMercado()
        for url in urls:
            self.driver.get(url)
            element = self.driver.find_element(By.XPATH, '//*[@id="product-attribute-specs-table"]/tbody/tr[2]/td')
            code = element.text.split("; ")
            element = self.driver.find_element(By.XPATH, '//*[@id="maincontent"]/div[2]/div/div[1]/div[2]')
            element = self.driver.find_elements(By.CLASS_NAME, 'price')[0]
            has_old_price = len(self.driver.find_elements(By.CLASS_NAME, 'old-price')) > 0
            if(has_old_price):
                element = self.driver.find_elements(By.CLASS_NAME, 'price')[1]

            preco = float(element.text.split('R$')[1].replace(',', '.'))
            element = self.driver.find_element(By.XPATH, '//*[@id="maincontent"]/div[2]/div/div[1]/div[1]/h1/span')
            nome_produto = element.text
            produto = Produto(nome_produto, preco, code, url)
            self.lista_produtos.append(produto)
        
        self.FecharMercado()

    def FecharMercado(self):
        self.driver.close()
        self.driver = None

class FortAtacadista(Supermercado):

    def __init__(self):
        self.nome = "Fort Atacadista"
        self.driver = None
        super().__init__(self.nome)

    def AbrirMercado(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://www.deliveryfort.com.br')
        self.driver = driver

    def AdicionarProduto(self, produtos: Produto):
        nome_produto = ""
        preco = 0.0

        self.AbrirMercado()
        for produto in produtos:
            self.driver.get(produto.url)
            nome_produto = self.driver.find_element(By.XPATH, '//*[@id="product-info"]/div/div/div[2]/div[1]/h1/div').text
            preco = float(self.driver.find_element(By.XPATH, '//*[@id="product-info"]/div/div/div[2]/div[4]/div/div/p[1]/em[1]').text.split('R$ ')[1].replace(',', '.'))
            produto = Produto(nome_produto, preco, produto.code, produto.url)
            self.lista_produtos.append(produto)
        
        self.FecharMercado()

    def FecharMercado(self):
        self.driver.close()
        self.driver = None

class Cliente:

    def __init__(self, nome):
        self.nome = nome
        self.produtos = []
    
    def AdicionarProduto(self, super_mercado: Supermercado, code):
        produto = super_mercado.PesquisarProduto(code)

        if(produto == False):
            print(f"Produto {code} inválido não adicionado no cliente {self.nome}!")
            return

        self.produtos.append(produto)

    def GetPrecoTotalDoCarrinho(self):
        preco = 0
        for produto in self.produtos:
            preco += produto.preco 
        
        return preco

def BarcodeReader(image):
     
    img = cv2.imread(image)
    detectedBarcodes = decode(img)

    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
        return False
    else:
        for barcode in detectedBarcodes:     
            if barcode.data != "":
                playsound('coin.wav')
                print(barcode.data)
                print(barcode.type)
                return barcode

            return False

def VerificarProduto(superMercado: Supermercado):
    webcam = cv2.VideoCapture(0)
    fotos_tiradas = 0
    if webcam.isOpened():

        validacao, frame = webcam.read()
        produto_checado = False
        while validacao:
            validacao, frame = webcam.read()
            cv2.imshow("Video da Webcam", frame)
            key = cv2.waitKey(5)

            key_esc = 27
            key_space = 32
            key_tab = 9

            if key == key_esc:
                break
                
            if produto_checado == False and key == key_space:
                fotos_tiradas += 1
                cv2.imwrite(f"Barcode{fotos_tiradas}.png", frame)
                barcode = BarcodeReader(f"./Barcode{fotos_tiradas}.png")

                if(barcode == False):
                    continue

                produto_checado = True
                code = str(barcode.data).split("b")[1].replace("'", "")
                produto = superMercado.PesquisarProduto(code)
                if(produto == False):
                    print(f"{superMercado.nome}: O produto não está registrado!")
                else:
                    print(f"{superMercado.nome}: João comprou o produto {produto.nome} e pagou R$ {produto.preco}")
            else:
                if key == key_tab:
                    produto_checado = False

                
    webcam.release()
    cv2.destroyAllWindows()

    for i in range(1, fotos_tiradas + 1):
        os.remove(r"C:\Users\joaov\OneDrive\Documentos\Projetos\Python\ReadBarCode\Barcode" + str(i) + ".png")

def VerificarMobile():

    url = "http://192.168.0.11:8080/shot.jpg"
    fotos_tiradas = 0
    produto_checado = False
    while True:
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)
        img = imutils.resize(img, width=600, height=800)
        cv2.imshow("Android_cam", img)

        key = cv2.waitKey(5)
        key_esc = 27
        key_space = 32
        key_tab = 9

        if key == key_esc:
            break
        
        if produto_checado == False and key == key_space:
            fotos_tiradas += 1
            cv2.imwrite(f"Barcode{fotos_tiradas}.png", img)
            barcode = BarcodeReader(f"./Barcode{fotos_tiradas}.png")

            if(barcode == False):
                continue

            produto_checado = True
            code = str(barcode.data).split("b")[1].replace("'", "")
            produto = super_koch.PesquisarProduto(code)
            if(produto == False):
                print(f"{super_koch.nome}: O produto não está registrado!")
            else:
                print(f"{super_koch.nome}: João comprou o produto {produto.nome} e pagou R$ {produto.preco}")
        else:
            if key == key_tab:
                produto_checado = False



    cv2.destroyAllWindows()
    for i in range(1, fotos_tiradas + 1):
        os.remove(r"C:\Users\joaov\OneDrive\Documentos\Projetos\Python\ReadBarCode\Barcode" + str(i) + ".png")

 
super_koch = SuperKoch()
super_koch.AdicionarProduto([
    'https://www.superkoch.com.br/pao-wickbold-grao-sabor-500g-frutas-7184',
    'https://www.superkoch.com.br/bisc-club-social-orig-pc-144g-15390',
    'https://www.superkoch.com.br/biscoito-trakinas-mais-chocolate-pacote-126g-41714',
    'https://www.superkoch.com.br/cafe-melitta-cx-500g-tradicional-4965',
    'https://www.superkoch.com.br/catalog/product/view/id/91385/s/bisc-trakinas-rech-pc-126g-meio-choc-lte-b-41713/category/2/',
    'https://www.superkoch.com.br/catalog/product/view/id/61538/s/pao-wickbold-400g-chia-macadamia-7154/category/2/',
    'https://www.superkoch.com.br/oleo-soja-soya-pet-900ml-945',
    'https://www.superkoch.com.br/ovos-lindsay-verm-cx-c-30-41226',
    'https://www.superkoch.com.br/bisc-club-social-pc-288g-original-15391'
])

if __name__ == "__main__":
    VerificarProduto(super_koch)


# fort_atacadista = FortAtacadista()
# fort_atacadista.AdicionarProduto([
#     Produto('', 0.0, ['7622210592729'], 'https://www.deliveryfort.com.br/biscoito-recheado-trakinas-mais-chocolate-126g/p?idsku=2280043'),
# ])



# giassi = Supermercado("Supermercado Giassi")
# giassi.AdicionarProduto('Biscoito Recheio Chocolate Trakinas +Recheio Pacote 126g', 2.58, '7622210592729', 'https://www.giassi.com.br/biscoito_recheio_chocolate_trakinas_recheio_pacote_126g_868264/p')
# giassi.AdicionarProduto('Biscoito Recheio Chocolate e Morango Trakinas Meio a Meio Pacote 126g', 2.58, '7622210592637', 'https://www.giassi.com.br/biscoito_recheio_chocolate_e_morango_trakinas_meio_a_meio_pacote_126g_868230/p')
# giassi.AdicionarProduto('Biscoito Recheio Chocolate Branco e Preto Trakinas Meio a Meio Pacote 126g', 2.58, '7622210592637', 'https://www.giassi.com.br/biscoito_recheio_chocolate_e_morango_trakinas_meio_a_meio_pacote_126g_868230/p')


# joao = Cliente("João")
# joao.AdicionarProduto(super_koch, "7622210592729")
# # joao.AdicionarProduto(super_koch, "7622210592668")
# # joao.AdicionarProduto(super_koch, "7896066303680")

# precoTotal = joao.GetPrecoTotalDoCarrinho()
# print(f"Preço total é de {precoTotal}")