===========================================================
GUIA DE MANUTENÇÃO - LENITA APP
===========================================================

1. ATUALIZAR O CÓDIGO (APÓS ALTERAÇÕES LOCAIS):
-----------------------------------------------
# Entre na pasta do projeto
cd /root/lenita_frete

# Se usar Git:
git pull origin main

# Se mudou os Models, rode as migrações:
python3 manage.py makemigrations
python3 manage.py migrate

2. COMANDOS DO SERVIDOR (GUNICORN):
-----------------------------------
# Verificar se o serviço está rodando:
systemctl status gunicorn

# Reiniciar o Gunicorn (Obrigatório após mudar código .py):
systemctl restart gunicorn

# Ver logs de erro em tempo real:
journalctl -u gunicorn -f

3. COMANDOS DO SERVIDOR WEB (NGINX):
------------------------------------
# Testar configurações (antes de reiniciar):
nginx -t

# Reiniciar Nginx (necessário se mudar DNS ou arquivos de site-enabled):
systemctl restart nginx

4. ACESSO AO BANCO MYSQL:
-------------------------
# Acesso rápido via terminal:
mysql -u [seu_usuario] -p [nome_do_banco]

# Dica: Na Hostinger, o phpMyAdmin é mais prático para ver as tabelas de frete.

5. ARQUIVOS EXCEL:
------------------
Localização: /root/lenita_frete/tab_bases/
Lembrar de manter os nomes dos arquivos idênticos aos do código.
===========================================================