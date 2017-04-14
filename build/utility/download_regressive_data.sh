cd ~/

# We need to be under the dminer python environment for the requests module
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
workon dminer

# Make the directories needed to store the data
mkdir data
mkdir data/alphabay
mkdir data/dreammarket


cd ~/data/alphabay
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJMC1NRGZSYmNycGs" "alphabay_02_14_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJdjNfZFJtMTgxZ0E" "alphabay_02_27_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJQVZJSWdzTU9ScFU" "alphabay_03_13_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJYW5zZVVkVzRkSEU" "alphabay_03_20_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJdkcxNnBYdTJCaWc" "alphabay_03_28_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJZUlGaWlwN1Q5eTQ" "alphabay_03_06_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJNC16bUx6dFM4MzA" "alphabay_04_10_17.tar.gz"

ls *.tar.gz | xargs -i tar xf {}

cd ~/data/dreammarket
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJSDRxUkMwMGRDWGs" "dreammarket_02_14_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJMDloZkpzVHFQblk" "dreammarket_02_27_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJLUNtS0ZrbV9ZY2M" "dreammarket_03_13_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJWTE5ZWdUNV9nbEE" "dreammarket_03_20_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJek9kSl9zRk92Zkk" "dreammarket_03_28_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJNTd6ZHRRWURWT1k" "dreammarket_03_06_17.tar.gz"
python /vagrant/build/utility/gdrive_download.py "0B5HYvRxs7XZJdWNEZ3ctbUIxWEU" "dreammarket_04_10_17.tar.gz"

ls *.tar.gz | xargs -i tar xf {}
