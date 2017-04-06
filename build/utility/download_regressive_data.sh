cd ~/

# Make the directories needed to store the data
mkdir data
mkdir data/alphabay
mkdir data/dreammarket


cd ~/data/alphabay
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJMC1NRGZSYmNycGs" -O alphabay_02_14_17.tar.gz
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJdjNfZFJtMTgxZ0E" -O alphabay_02_27_17.tar.gz
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJQVZJSWdzTU9ScFU" -O alphabay_03_13_17.tar.gz
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJYW5zZVVkVzRkSEU" -O alphabay_03_20_17.tar.gz
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJdkcxNnBYdTJCaWc" -O alphabay_03_28_17.tar.gz
wget -nv "https://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJZUlGaWlwN1Q5eTQ" -O alphabay_03_06_17.tar.gz

ls *.tar.gz | xargs -i tar xf {}

# cd ~/data/dreammarket
# 
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJSDRxUkMwMGRDWGs" -O dreammarket_02_14_17.tar.gz
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJMDloZkpzVHFQblk" -O dreammarket_02_27_17.tar.gz
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJLUNtS0ZrbV9ZY2M" -O dreammarket_03_13_17.tar.gz
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJWTE5ZWdUNV9nbEE" -O dreammarket_03_20_17.tar.gz
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJek9kSl9zRk92Zkk" -O dreammarket_03_28_17.tar.gz
# wget -nv "http://drive.google.com/uc?export=download&id=0B5HYvRxs7XZJNTd6ZHRRWURWT1k" -O dreammarket_03_06_17.tar.gz
# 
# ls *.tar.gz | xargs -i tar xf {}
