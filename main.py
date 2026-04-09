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
import winsound # Para o "beep" no Windows

# Carrega as variáveis de ambiente do arquivo .env na mesma pasta
load_dotenv()

# ================= CONFIGURAÇÕES =================
USUARIO = os.getenv("MOODLE_USUARIO")
SENHA = os.getenv("MOODLE_SENHA")
URL_PRESENCA = os.getenv("MOODLE_URL")
# =================================================

def iniciar_bot():
    # Verifica se as variáveis foram carregadas corretamente
    if not USUARIO or not SENHA or not URL_PRESENCA:
        print("Erro: Verifique se o arquivo .env existe e contém MOODLE_USUARIO, MOODLE_SENHA e MOODLE_URL.")
        return

    print("Iniciando o navegador...")
    
    # Configura e abre o Chrome
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico) # type: ignore
    
    # 1. Acessa a URL da presença (se não estiver logado, o Moodle redireciona para o Login da UFSC)
    driver.get(URL_PRESENCA)
    
    try:
        print("Verificando se há tela intermediária do Moodle...")
        try:
            # Tenta encontrar o botão "Continuar" por até 5 segundos
            # Usamos o texto do botão já que o ID muda sempre
            botao_continuar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Continuar')]"))
            )
            botao_continuar.click()
            print("Botão 'Continuar' clicado. Indo para a tela da UFSC...")
        except Exception:
            # Se não achar o botão em 5 segundos, significa que já caiu direto na tela da UFSC, então só ignora
            print("Sem tela intermediária, seguindo para o login...")

        print("Aguardando a página de login carregar...")
        # Espera o campo de usuário aparecer
        campo_usuario = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username")) 
        )
        campo_senha = driver.find_element(By.ID, "password")
        
        print("Preenchendo credenciais...")
        campo_usuario.send_keys(USUARIO)
        campo_senha.send_keys(SENHA)
        
        # Clica no botão Entrar que você inspecionou
        botao_login = driver.find_element(By.NAME, "submit")
        botao_login.click()
        
        print("Login efetuado! Aguardando o sistema processar...")
        time.sleep(5) 
        
        # GARANTIA: Força a navegação para a página de presença novamente após o login
        print("Garantindo navegação para a página da disciplina...")
        driver.get(URL_PRESENCA)
        time.sleep(3) # Pausa rápida para a página carregar
        
    except Exception as e:
        print(f"Erro na etapa de login: {e}")
        input("Faça o login manualmente, navegue até a página da presença e aperte ENTER aqui para continuar...")

    print("Iniciando o monitoramento da presença...")
    
    # 2. Loop de verificação (mantém a sessão ativa)
    while True:
        try:
            # Recarrega a página de presença
            driver.get(URL_PRESENCA)
            
            # Procura por links que contenham a palavra "presença" (como "Enviar presença" ou "Registrar presença")
            links_presenca = driver.find_elements(By.PARTIAL_LINK_TEXT, "presença")
            
            if len(links_presenca) > 0:
                print("\n[!] A PRESENÇA FOI LIBERADA! [!]")
                # Toca o alarme (Frequência: 2500Hz, Duração: 1000ms). Toca 3 vezes para garantir.
                for _ in range(3):
                    winsound.Beep(2500, 1000)
                    time.sleep(0.5)
                break # Sai do loop
            
            else:
                # Calcula um tempo de espera entre 60 e 75 segundos (Jitter para evitar bloqueio)
                espera = 60 + random.randint(1, 15)
                print(f"Ainda fechado. Atualizando novamente em {espera} segundos...")
                time.sleep(espera)
                
        except Exception as e:
            print(f"Erro ao verificar página: {e}")
            time.sleep(60) # Tenta de novo após 1 minuto caso dê erro de conexão

    print("Monitoramento encerrado.")
    # driver.quit() # Descomente esta linha se quiser que o navegador feche sozinho no final

# Executa a função
if __name__ == "__main__":
    iniciar_bot()