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
    """Função dedicada a fazer o login, lidando com a tela intermediária e a tela da UFSC."""
    try:
        print("\n[Login] Verificando se há tela intermediária do Moodle...")
        try:
            botao_continuar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Continuar')]"))
            )
            botao_continuar.click()
            print("[Login] Botão 'Continuar' clicado. Indo para a tela da UFSC...")
        except Exception:
            pass # Sem tela intermediária, apenas segue

        print("[Login] Aguardando a página de login da UFSC...")
        campo_usuario = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "password").send_keys(SENHA)
        campo_usuario.send_keys(USUARIO)
        
        driver.find_element(By.NAME, "submit").click()
        print("[Login] Credenciais enviadas! Aguardando o sistema processar...")
        time.sleep(5) 
        
    except Exception as e:
        print(f"[Login] Erro crítico na etapa de login: {e}")
        input("Faça o login manualmente no navegador e aperte ENTER aqui para o bot continuar...")


def iniciar_bot():
    if not USUARIO or not SENHA or not URL_PRESENCA:
        print("Erro: Verifique seu arquivo .env")
        return

    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico)
    
    # Primeiro acesso e login inicial
    driver.get(URL_PRESENCA)
    realizar_login(driver)

    print("\nIniciando o monitoramento da presença...")
    
    while True:
        try:
            driver.get(URL_PRESENCA)
            time.sleep(3) # Pausa rápida para garantir carregamento do DOM
            
            # --- VERIFICAÇÃO DE SESSÃO EXPIRADA ---
            # Se encontrar o campo 'username' ou o botão 'Continuar', significa que fomos deslogados
            deslogado = driver.find_elements(By.ID, "username") or driver.find_elements(By.XPATH, "//button[@type='submit' and contains(text(), 'Continuar')]")
            
            if deslogado:
                print("\n[!] Sessão expirada ou redirecionamento detectado! Refazendo o login...")
                realizar_login(driver)
                continue # Pula o resto do loop e recomeça lá de cima (dá o get(URL) novamente)
            
            # --- BUSCA A PRESENÇA ---
            links = driver.find_elements(By.PARTIAL_LINK_TEXT, "presença")
            
            if len(links) > 0:
                print("\n[!] Presença detectada! Tentando marcar automaticamente...")
                links[0].click() 
                
                try:
                    # Espera rádio button e clica
                    opcao = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//label[contains(., '2 presenças') or contains(., 'Presente')]/preceding-sibling::input[@type='radio']"))
                    )
                    opcao.click()
                    print("Opção selecionada.")
                    
                    # Clica em salvar
                    driver.find_element(By.ID, "id_submitbutton").click()
                    print("SUCESSO: Presença anotada automaticamente!")
                    
                    for _ in range(3):
                        winsound.Beep(2500, 600)
                        time.sleep(0.2)
                    
                except Exception as e_automacao:
                    print(f"Erro ao preencher: {e_automacao}")
                    winsound.Beep(1000, 3000)
                
                break # Encerra o script pois o trabalho acabou
                
            else:
                espera = 60 + random.randint(1, 10)
                print(f"Ainda fechado. Próxima checagem em {espera}s...")
                time.sleep(espera)
                
        except Exception as e:
            print(f"Erro de conexão durante o loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    iniciar_bot()