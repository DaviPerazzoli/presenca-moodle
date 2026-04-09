import time
import random
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import winsound

load_dotenv()

USUARIO = os.getenv("MOODLE_USUARIO")
SENHA = os.getenv("MOODLE_SENHA")
URL_PRESENCA = os.getenv("MOODLE_URL")

def realizar_login(driver):
    try:
        print("\n[Login] Verificando tela inicial...")
        try:
            botao_continuar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar')]"))
            )
            botao_continuar.click()
        except:
            pass

        campo_usuario = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "password").send_keys(SENHA)
        campo_usuario.send_keys(USUARIO) # type: ignore
        driver.find_element(By.NAME, "submit").click()
        time.sleep(5) 
    except Exception as e:
        print(f"[Login] Erro: {e}")
        input("Faça login manualmente e aperte ENTER aqui...")

def iniciar_bot():
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico) # type: ignore
    driver.get(URL_PRESENCA)
    realizar_login(driver)

    print("\nMonitorando presença...")
    
    while True:
        try:
            driver.get(URL_PRESENCA)
            time.sleep(2)
            
            # Detecção de deslogado
            if driver.find_elements(By.ID, "username"):
                realizar_login(driver)
                continue

            links = driver.find_elements(By.PARTIAL_LINK_TEXT, "presença")
            
            if len(links) > 0:
                print("\n[!] PRESENÇA DETECTADA!")
                # TOCA O SOM IMEDIATAMENTE AO DETECTAR
                for _ in range(5):
                    winsound.Beep(2500, 500)
                
                print("Tentando marcar automaticamente...")
                links[0].click() 
                
                try:
                    # 1. Seleciona o Radio Button (Usando o ID que você passou)
                    # NOTA: Se esse ID mudar na próxima aula, usaremos o seletor por NOME abaixo
                    wait = WebDriverWait(driver, 10)
                    try:
                        radio = wait.until(EC.element_to_be_clickable((By.ID, "id_status_247837")))
                    except:
                        # Se o ID mudou, tenta pelo nome 'status' e pega a primeira opção (geralmente 'Presente')
                        radio = wait.until(EC.element_to_be_clickable((By.NAME, "status")))
                    
                    radio.click()
                    print("Opção selecionada.")
                    
                    # 2. Clica no botão Salvar (Usando o ID que você passou)
                    botao_salvar = driver.find_element(By.ID, "id_submitbutton")
                    botao_salvar.click()
                    
                    print("SUCESSO TOTAL: Presença enviada!")
                    winsound.Beep(3000, 1000) # Som de vitória
                    
                except Exception as e_automacao:
                    print(f"Erro na automação: {e_automacao}")
                    print("CORRA! A página está aberta, mas o bot falhou em clicar. MARQUE MANUALMENTE!")
                    for _ in range(10): winsound.Beep(1000, 200) # Alerta de erro
                
                # MANTÉM O NAVEGADOR ABERTO PARA VOCÊ CONFERIR
                input("\nPresença processada. Confira o navegador e aperte ENTER para fechar o script...")
                break 
                
            else:
                espera = 60 + random.randint(1, 5)
                print(f"Ainda fechado. Próxima checagem em {espera}s...")
                time.sleep(espera)
                
        except Exception as e:
            print(f"Erro no loop: {e}")
            for _ in range(3): winsound.Beep(1000, 200)
            time.sleep(10)

if __name__ == "__main__":
    iniciar_bot()