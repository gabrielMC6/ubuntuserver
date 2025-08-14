# Monitoramento do Nginx com Alerta no Discord

Este projeto é um script simples para monitorar o status do Nginx em um servidor Ubuntu. Caso o Nginx caia, o script envia um alerta para um canal no Discord e tenta reiniciar automaticamente o serviço.

## Funcionalidades
- **Monitoramento do Nginx:** Verifica se o Nginx está ativo.
- **Alerta no Discord:** Envia uma mensagem de alerta caso o Nginx caia.
- **Reinício automático:** Caso o Nginx esteja inativo, o script tenta reiniciar o serviço.

## Requisitos
- Ubuntu Server
- Nginx instalado e configurado
- Acesso ao Discord (para criar um webhook)

## Como Configurar

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Instalar dependências:**
   Certifique-se de que o Python 3 esteja instalado no seu servidor.

   Instale as dependências necessárias com:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

3. **Configurar o Webhook do Discord:**
   - Crie um webhook no seu canal do Discord (Configurações do canal > Integrações > Webhooks > Criar Webhook).
   - Copie o **URL do Webhook**.

4. **Configurar o arquivo `.env`:**
   - Crie o arquivo `/etc/estudio-monitor.env` e adicione a URL do webhook:
     ```bash
     sudo nano /etc/estudio-monitor.env
     ```
   - Adicione as variáveis de configuração:
     ```env
     MON_URL="http://127.0.0.1/healthz"
     MON_TIMEOUT=5
     MON_RETRIES=3
     DISCORD_WEBHOOK_URL="COLE_AQUI_O_SEU_WEBHOOK"
     ```

5. **Configurar o script de monitoramento:**
   - O script principal está em `/opt/estudio-nginx/monitor_nginx.py`.
   - Certifique-se de que o script tenha permissão de execução:
     ```bash
     sudo chmod +x /opt/estudio-nginx/monitor_nginx.py
     ```

6. **Ativar o Timer:**
   - Habilite o timer para executar o monitoramento periodicamente:
     ```bash
     sudo systemctl enable --now estudio-monitor.timer
     ```

7. **Verificar o status do Nginx:**
   - O script automaticamente verifica o status do Nginx a cada minuto e envia alertas no Discord caso o serviço esteja inativo.
   - Para testar, basta parar o Nginx:
     ```bash
     sudo systemctl stop nginx
     ```

## Como Funciona
- O script verifica se o Nginx está ativo. Se ele não estiver, o script envia um alerta no Discord e tenta reiniciar o serviço.
- O Nginx é monitorado periodicamente pelo timer do systemd.

## Logs
- Os logs do script podem ser visualizados com o comando:
  ```bash
  journalctl -u estudio-monitor.service -f
  ```

## Contribuições
Sinta-se à vontade para contribuir com melhorias ou correções. Para isso, faça um fork deste repositório, adicione suas mudanças e envie um pull request.

## Licença
Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
