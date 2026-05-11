# Telegram Media Archiver

Bot em Python para monitorar um canal do Telegram, baixar automaticamente toda mídia nova e enviar para qualquer destino suportado pelo `rclone` como Google Drive, Dropbox, OneDrive, S3, R2 ou WebDAV.

## Arquitetura

- `Telethon` para escutar mensagens novas e opcionalmente fazer backfill de histórico.
- `sqlite` para evitar upload duplicado por `(chat_id, message_id)`.
- `rclone` para envio do arquivo a um remote configurado.
- `systemd` e `rsync/ssh` para deploy simples em VPS.

## Requisitos

- Python 3.11+
- `rclone` instalado e configurado no servidor
- Credenciais do Telegram em `https://my.telegram.org`
- A conta/sessão precisa ter acesso ao canal monitorado

## Configuração local

1. Crie o ambiente e instale dependências:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

2. Copie `.env.example` para `.env` e ajuste os valores:

```env
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_SESSION_NAME=media_archiver
TELEGRAM_CHANNEL=@meu_canal
RCLONE_REMOTE=backup:telegram-media
```

3. Teste localmente:

```bash
python -m tg_media_archiver.cli
```

Na primeira execução o Telethon pode pedir login e código da conta.

## Deploy para VPS via SSH

1. Crie o diretório de app na VPS:

```bash
ssh user@host 'mkdir -p /opt/telegram-media-archiver'
```

2. Sincronize os arquivos:

```bash
rsync -av --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '.env' \
  ./ user@host:/opt/telegram-media-archiver/
```

3. Na VPS, instale dependências:

```bash
ssh user@host 'cd /opt/telegram-media-archiver && python3 -m venv .venv && . .venv/bin/activate && pip install -e .'
```

4. Copie o `.env` para a VPS e configure o `rclone`:

```bash
scp .env user@host:/opt/telegram-media-archiver/.env
ssh user@host 'rclone config'
```

5. Instale o serviço `systemd`:

```bash
ssh user@host 'sudo cp /opt/telegram-media-archiver/deploy/telegram-media-archiver.service /etc/systemd/system/'
ssh user@host 'sudo systemctl daemon-reload && sudo systemctl enable --now telegram-media-archiver'
```

## GitHub

O repositório local já está pronto para versionamento. Quando você criar um repo vazio no GitHub, conecte assim:

```bash
git remote add origin git@github.com:SEU_USUARIO/telegram-media-archiver.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

## Limitações

- Bot comum da Bot API não é suficiente para todos os cenários de captura em canais; aqui a base usa `Telethon` com sessão de usuário.
- Arquivos muito grandes dependem do limite da conta, rede e espaço temporário.
- Se você quiser apagar o arquivo local após upload, isso pode ser adicionado como próxima etapa.
