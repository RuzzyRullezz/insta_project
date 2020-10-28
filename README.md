# INSTALL GUIDE

**1. INSTALL PACKAGES AND LIBS**
```bash
sudo apt-get install -y software-properties-common make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
sudo apt-get install -y python-dev pkg-config
sudo apt-get install -y \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
sudo apt-get install ffmpeg
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update 
sudo apt-get install -y google-chrome-stable chromium-browser nginx
```
**2. INSTALL SUPERVISOR**
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py
sudo apt-get install pip
sudo pip install supervisor
sudo bash -c "echo_supervisord_conf > /etc/supervisord.conf"
sudo bash -c "cat <<'EOF' >>/etc/supervisord.conf
[include]
files = /var/www/insta_project/misc/supervisor/*.conf
[supervisord]
environment=AIRFLOW_HOME="/var/www/insta_project/misc/airflow",PYTHON_PATH="/home/$USER/.pyenv/versions/insta_project/bin/python"
EOF"
```
**3. INSTALL PYENV**
```bash
curl https://pyenv.run | bash
cat <<'EOF' >>~/.bashrc
export PATH="/home/$USER/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
```
**4. INSTALL PYTHON 3.7.2**
```bash
pyenv install 3.7.2
pyenv virtualenv 3.7.2 insta_project
```
**5. SETUP PROJECT**
```bash
sudo mkdir -p /var/www/insta_project
sudo chown -R $USER /var/www/insta_project
cd /var/www/insta_project
pyenv local insta_project
# Add id_rsa.pub to github deploys keys
git init
git remote add origin git@github.com:RuzzyRullezz/insta_project.git
git remote -v
git pull
git checkout master
pip install pip --upgrade
export SLUGIFY_USES_TEXT_UNIDECODE=yes
pip install -r requirements.txt
cd /usr/bin
sudo ln -s /home/$USER/.pyenv/versions/insta_project/bin/gunicorn
sudo ln -s /home/rus/.pyenv/versions/insta_project/bin/airflow
cd ~
```
**6. INSTALL RABBITMQ**
```bash
sudo apt-key adv --keyserver "hkps.pool.sks-keyservers.net" --recv-keys "0x6B73A36E6026DFCA"
sudo apt-get install apt-transport-https
sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list <<EOF
deb https://dl.bintray.com/rabbitmq-erlang/debian bionic erlang-21.x
deb https://dl.bintray.com/rabbitmq/debian bionic main
EOF
sudo apt-get update -y
sudo apt-get install rabbitmq-server -y --fix-missing
```
**7. MAKE AIRFLOW RMQ VHOST**
```bash
sudo rabbitmqctl add_vhost airflow
sudo rabbitmqctl set_permissions -p my_vhost guest ".*" ".*" ".*"
```
**8. INSTALL POSTGRES**
```bash
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
RELEASE=$(lsb_release -cs)
echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-11
```
**9. CREATE DATABASE**
```bash
sudo -u postgres psql -c "CREATE ROLE insta_project WITH PASSWORD 'insta_project' LOGIN;"
sudo -u postgres psql -c "CREATE DATABASE insta_project WITH OWNER insta_project;"
sudo -u postgres psql -c "CREATE ROLE airflow WITH PASSWORD 'airflow' LOGIN;"
sudo -u postgres psql -c "CREATE DATABASE airflow WITH OWNER airflow;"
```
**11. MAKE MIGRATIONS**
```bash
cd /var/www/insta_project/
python manage.py migrate
```
**12. INIT AIRFLOW DB**
```bash
airflow initdb
airflow create_user -r Admin -u rus -e sova@ruzzy.pro -f R -l G -p ******
```
**13. ADD ACCOUNTS DATA**
```bash
sudo -u postgres psql --dbname=insta_project -c "INSERT INTO account(username, password, email, email_password) VALUES (...);"
```
**14. INSTALL REDIS**
```bash
sudo apt-get install redis-server -y
sudo systemctl enable redis-server.service
```
**15. SET ENV**
```bash
export AIRFLOW_HOME="/var/www/insta_project/misc/airflow"
cat <<'EOF' >>~/.bashrc
export AIRFLOW_HOME="/var/www/insta_project/misc/airflow"
EOF
```
**16. START SUPERVISOR**
```bash
sudo supervisord
```