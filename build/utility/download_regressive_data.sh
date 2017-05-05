cd ~/

# We need to be under the dminer python environment for the requests module
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
workon dminer

# Make the directories needed to store the data
mkdir data
mkdir data/alphabay
mkdir data/dreammarket


cd ~/data/alphabay
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJeV9wWDl5SjZqM28" "alphabay_04_17_17.tar.gz"

ls *.tar.gz | xargs -i tar xf {}

cd ~/data/dreammarket
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJWjk4TTYwQ3A1Qnc" "dreammarket_04_17_17.tar.gz"

ls *.tar.gz | xargs -i tar xf {}
