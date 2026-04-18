<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Version-1.0-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Type-Banner%20Grabber-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Termux-Compatible-black?style=for-the-badge&logo=android"/>
</p>

<h1 align="center">🚩 ShadowBanner</h1>
<p align="center"><b>Banner Grabber & Service Detection for Ethical Hackers</b></p>

---

## 📖 Sobre

**ShadowBanner** é uma ferramenta de banner grabbing desenvolvida para **pentesting ético** e identificação de serviços expostos.

Criada por **Mr Joker**, deteta versões de serviços em portas comuns — informação essencial para identificar vulnerabilidades conhecidas (CVEs).

Compatível com **Linux** e **Termux** (Android).

---

## ⚡ Funcionalidades

- 🚩 Banner grabbing em 14 portas comuns
- 🌐 Extração de headers HTTP/HTTPS (Server, X-Powered-By, título da página)
- ⚡ Multi-threading (scan paralelo e rápido)
- 🎨 Interface CLI colorida e organizada
- 📊 Barra de progresso em tempo real
- 📁 Exportação em `.txt` e `.json`
- 🔀 Aceita host único ou ficheiro com lista de hosts
- 🔒 Suporte a SSL/TLS (HTTPS, certificados self-signed)
- 📱 Compatível com Termux (Android)

---

## 🎯 Portas Monitorizadas

| Porta | Serviço | Porta | Serviço |
|-------|---------|-------|---------|
| 21 | FTP | 443 | HTTPS |
| 22 | SSH | 3306 | MySQL |
| 23 | Telnet | 5432 | PostgreSQL |
| 25 | SMTP | 6379 | Redis |
| 80 | HTTP | 8080 | HTTP-Alt |
| 110 | POP3 | 8443 | HTTPS-Alt |
| 143 | IMAP | 27017 | MongoDB |

---

## 🔗 Pipeline de Integração

```
ShadowSub   →  encontra subdomínios
     ↓
ShadowProbe →  verifica quais estão ativos
     ↓
ShadowScan  →  analisa portas abertas
     ↓
ShadowBanner → identifica versões e serviços  ← aqui
```

---

## ⚙️ Instalação

### Linux

```bash
git clone https://github.com/mrjoker-web/ShadowBanner.git
cd ShadowBanner
pip install requests colorama urllib3
```

### Termux (Android)

```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/mrjoker-web/ShadowBanner.git
cd ShadowBanner
pip install requests colorama urllib3
```

---

## ▶️ Como usar

Host único:

```bash
python shadowbanner.py -t example.com
```

Lista de hosts:

```bash
python shadowbanner.py -l hosts.txt
```

Com threads personalizadas e nome de output:

```bash
python shadowbanner.py -l hosts.txt --threads 20 -o resultados
```

---

## 📄 Input (lista de hosts)

Ficheiro `hosts.txt` (um host por linha):

```
example.com
192.168.1.1
admin.example.com
```

---

## 📸 Exemplo de Output

```
═══════════════════════════════════════════════════════
  Target: example.com  (93.184.216.34)
  Time:   2026-04-11 21:00:00
───────────────────────────────────────────────────────

  [+] Porta 22 — SSH
      Banner             SSH-2.0-OpenSSH_8.2p1 Ubuntu

  [+] Porta 80 — HTTP
      Server             Apache/2.4.52 (Ubuntu)
      Status-Code        200
      Page-Title         Example Domain

  [+] Porta 443 — HTTPS
      Server             nginx/1.18.0
      X-Powered-By       PHP/8.1.0
      Status-Code        200

═══════════════════════════════════════════════════════

═══════════════════════════════════════════════════════
  [✓] Scan concluído!
  Hosts scaneados : 1
  Banners obtidos : 3
  Output TXT      : shadow_banners.txt
  Output JSON     : shadow_banners.json
═══════════════════════════════════════════════════════
```

---

## 📁 Ficheiros de Output

| Ficheiro | Formato | Uso |
|---|---|---|
| `shadow_banners.txt` | Texto simples | Leitura rápida |
| `shadow_banners.json` | JSON estruturado | Automação e integração |

---

## 📌 Roadmap

- [ ] Detecção automática de CVEs por versão
- [ ] Exportação em CSV
- [ ] Integração direta com ShadowScan

---

## ⚠️ Disclaimer

> Esta ferramenta foi desenvolvida **apenas para fins educacionais e testes em sistemas autorizados**.  
> O uso indevido é da **inteira responsabilidade do utilizador**.  
> Nunca uses esta ferramenta em sistemas sem autorização explícita.

---

## 👨‍💻 Autor

**Mr Joker**  
🔗 [github.com/mrjoker-web](https://github.com/mrjoker-web)  
🔒 Cybersecurity Enthusiast | Pentesting Tools Developer
