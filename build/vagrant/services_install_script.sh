# Add GPG Key for elasticsearch:
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -

# Add GPG Key for Torproject
gpg --keyserver keys.gnupg.net --recv A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -

# Add Torproject source
echo "deb http://deb.torproject.org/torproject.org xenial main" >> /etc/apt/sources.list

# Update all repositories
apt-get update

# Install NGINX, wget, java, htop, torproject keyring, tor
apt-get install nginx wget default-jre htop deb.torproject.org-keyring tor -y

# Upgrade Firefox to latest for selenium control
apt-get install --only-upgrade firefox

# Download and install Elasticsearh deb
echo "Downloading Elasticsearch"
wget -nv https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.deb
echo "Installing and starting Elasticsearch service"
dpkg -i elasticsearch-5.2.1.deb
rm elasticsearch-5.2.1.deb
systemctl enable elasticsearch.service
systemctl start elasticsearch

# Download and install Kibana deb
echo "Downloading Kibana"
wget -nv https://artifacts.elastic.co/downloads/kibana/kibana-5.2.1-amd64.deb
echo "Installing and starting Kibana service"
dpkg -i kibana-5.2.1-amd64.deb
rm kibana-5.2.1-amd64.deb
systemctl enable kibana.service
systemctl start kibana
