# Telegram Media Archiver

Bot em Python para monitorar um canal do Telegram, baixar automaticamente toda mídia nova e enviar para qualquer destino suportado pelo `rclone` como Google Drive, Dropbox, OneDrive, S3, R2 ou WebDAV.

## Arquitetura

- `Telethon` para escutar mensagens novas com bot token ou sessão de usuário, e opcionalmente fazer backfill de histórico.
- `sqlite` para evitar upload duplicado por `(chat_id, message_id)`.
- `rclone` para envio do arquivo a um remote configurado.
- `systemd` e `rsync/ssh` para deploy simples em VPS.

## Requisitos

- Python 3.11+
- `rclone` instalado e configurado no servidor
- `API ID` e `API hash` em `https://my.telegram.org`
- Um `bot token` do `@BotFather` ou uma sessão de usuário
- O bot ou a conta precisa ter acesso ao canal monitorado

## Criando o bot

1. Abra `@BotFather` no Telegram.
2. Execute `/newbot`.
3. Defina nome e `username` do bot.
4. Guarde o token gerado.
5. Adicione o bot como administrador do canal que será monitorado.

Se o canal for seu, esse é o caminho mais simples. Se você quiser ler histórico antigo ou monitorar canais onde bot comum não enxerga tudo, use sessão de usuário em vez de bot token.

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
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL=@meu_canal
RCLONE_REMOTE=backup:telegram-media
```

3. Teste localmente:

```bash
python -m tg_media_archiver.cli
```

Se `TELEGRAM_BOT_TOKEN` estiver preenchido, o processo autentica como bot.
Se ele estiver vazio, o Telethon usa sessão de usuário e pode pedir login e código na primeira execução.

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

- Bot comum funciona bem quando ele é administrador do canal e você só precisa capturar mensagens novas.
- Para backfill mais confiável de histórico antigo e alguns cenários de acesso, sessão de usuário continua sendo mais forte.
- Arquivos muito grandes dependem do limite da conta, rede e espaço temporário.
- Se você quiser apagar o arquivo local após upload, isso pode ser adicionado como próxima etapa.
