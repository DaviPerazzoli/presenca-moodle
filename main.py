import time
import random
import os
import platform
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

USUARIO = os.getenv("MOODLE_USUARIO")
SENHA = os.getenv("MOODLE_SENHA")
URL_PRESENCA = os.getenv("MOODLE_URL")

def emitir_beep(frequencia, duracao_ms):
    """
    Função multiplataforma para emitir alertas sonoros.
    No Windows usa o winsound. No Linux, tenta usar o 'play' (sox) ou o sino do terminal.
    """
    sistema = platform.system()
    
    if sistema == "Windows":
        # O import é feito aqui dentro (Lazy Import) para não quebrar em outros SOs
        import winsound
        winsound.Beep(frequencia, duracao_ms)
        
    elif sistema == "Linux":
        # Converte milissegundos para segundos
        duracao_seg = duracao_ms / 1000.0
        
        # Tenta usar o comando 'play' do pacote 'sox' para gerar a frequência exata
        # O redirecionamento '2> /dev/null' oculta as mensagens no terminal
        resultado = os.system(f"play -nq -t alsa synth {duracao_seg} sine {frequencia} 2> /dev/null")
        
        # Se o comando falhar (sox não instalado), usa o "Terminal Bell" como plano B
        if resultado != 0:
            print('\a', end='', flush=True)
            
    elif sistema == "Darwin":  # macOS
        print('\a', end='', flush=True)


def lidar_com_erro(mensagem_erro, erro_tecnico=None):
    """
    Função dedicada para segurar qualquer erro fatal. 
    Emite beeps de alerta e pausa o script aguardando intervenção do usuário.
    """
    print(f"\n[!] ALERTA DE ERRO: {mensagem_erro}")
    if erro_tecnico:
        print(f"Detalhe técnico: {erro_tecnico}")
    
    # Emite 3 beeps graves para alertar que algo falhou
    for _ in range(3):
        emitir_beep(1000, 400)
        time.sleep(0.1)
        
    input("\n>> O script foi pausado. Resolva manualmente no navegador se necessário e APERTE ENTER aqui para continuar...")
    print("Retomando execução...\n")


def realizar_login(driver):
    try:
        print("\n[Login] Verificando tela inicial...")
        try:
            botao_continuar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar')]"))
            )
            botao_continuar.click()
        except Exception:
            pass # Ignora se o botão continuar não existir

        campo_usuario = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "password").send_keys(SENHA)
        campo_usuario.send_keys(USUARIO) # type: ignore
        driver.find_element(By.NAME, "submit").click()
        time.sleep(5) 
        
    except Exception as e:
        lidar_com_erro("Falha ao tentar realizar o login automático.", e)


def iniciar_bot():
    if not USUARIO or not SENHA or not URL_PRESENCA:
        print("Erro crítico: Verifique seu arquivo .env. Encerrando.")
        return

    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico) # type: ignore
    
    try:
        driver.get(URL_PRESENCA)
        realizar_login(driver)
    except Exception as e:
        lidar_com_erro("Erro ao abrir o navegador ou carregar a página inicial.", e)

    print("\nMonitorando presença...")
    
    while True:
        try:
            driver.get(URL_PRESENCA)
            time.sleep(2)
            
            # Detecção de deslogado
            if driver.find_elements(By.ID, "username") or driver.find_elements(By.XPATH, "//button[contains(text(), 'Continuar')]"):
                print("\n[!] Sessão caiu. Tentando logar novamente...")
                realizar_login(driver)
                continue

            # Procura por links contendo a palavra "presença"
            links = driver.find_elements(By.PARTIAL_LINK_TEXT, "presença")
            
            if len(links) > 0:
                print("\n[!] PRESENÇA DETECTADA!")
                
                # Toca o som imediatamente ao detectar o botão (5 beeps agudos)
                for _ in range(5):
                    emitir_beep(2500, 500)
                    time.sleep(0.1) # Pausa curta entre os beeps
                
                print("Entrando na página de anotação...")
                links[0].click() 
                
                try:
                    xpath_radio_seguro = "//label[contains(., 'Presente') or contains(., 'presente') or contains(., '2 aulas') or contains(., '2 presenças')]//input[@type='radio']"
                    
                    wait = WebDriverWait(driver, 10)
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_radio_seguro)))
                    radio.click()
                    print("Opção de presença confirmada e selecionada.")
                    
                    botao_salvar = driver.find_element(By.ID, "id_submitbutton")
                    botao_salvar.click()
                    
                    print("\nSUCESSO TOTAL: Presença enviada com sucesso!")
                    emitir_beep(3000, 1500) # Som longo de vitória
                    
                    input("\n>> Presença finalizada. Confira o navegador e aperte ENTER para encerrar o script (ou feche a janela).")
                    break 
                    
                except Exception as e_automacao:
                    print("\nCORRA! A página está aberta, mas o bot falhou em clicar.")
                    lidar_com_erro("Falha ao selecionar o botão de presença ou enviar.", e_automacao)
                    break
                
            else:
                espera = 60 + random.randint(1, 5)
                print(f"[{time.strftime('%H:%M:%S')}] Ainda fechado. Próxima checagem em {espera}s...")
                time.sleep(espera)
                
        except Exception as e:
            lidar_com_erro("Erro inesperado durante o recarregamento da página.", e)


if __name__ == "__main__":
    iniciar_bot()