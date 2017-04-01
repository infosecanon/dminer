# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

# Global requirements for the actual module installation
$module_requirements_install_script = <<SCRIPT
# Update all repositories
apt-get update

# Install pip2, virtualenvwrapper
apt-get install python-pip virtualenvwrapper -y

SCRIPT

$module_environment_install_script = <<SCRIPT

# Configure environment variables and load them
echo "Configuring environment variables"
echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
echo "PATH=$PATH:~/" >> ~/.bashrc
echo "workon dminer" >> ~/.bashrc
source ~/.bashrc

# Download, unpack, and set in path the geckodriver
echo "Downloading and installing geckodriver to users home directory"
cd ~/Downloads
wget -nv https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz
tar -xvf geckodriver-v0.14.0-linux64.tar.gz
mv geckodriver ~/geckodriver

SCRIPT

$dev_module_install_script = <<SCRIPT
# Create virtualenv for dminer
echo "Creating virtualenv for dminer"
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
mkvirtualenv dminer

# Install the dminer in develop mode, and install all necessary dependencies
cd /vagrant
pip install -r dev-requirements.txt
python setup.py develop

SCRIPT

$prod_module_install_script = <<SCRIPT
# Create virtualenv for dminer
echo "Creating virtualenv for dminer"
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
mkvirtualenv dminer

# Install the dminer in develop mode, and install all necessary dependencies
cd /vagrant
pip install -r requirements.txt
python setup.py install

SCRIPT

$services_install_script = <<SCRIPT
# Add GPG Key for elasticsearch:
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -

# Update all repositories
apt-get update

# Install NGINX, wget, java
apt-get install nginx wget default-jre htop -y

# Download and install Elasticsearh deb
echo "Downloading Elasticsearch"
wget -nv https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.3.0.deb
echo "Installing and starting Elasticsearch service"
dpkg -i elasticsearch-5.3.0.deb
rm elasticsearch-5.3.0.deb
systemctl enable elasticsearch.service
systemctl start elasticsearch

# Download and install Kibana deb
echo "Downloading Kibana"
wget -nv https://artifacts.elastic.co/downloads/kibana/kibana-5.3.0-amd64.deb
echo "Installing and starting Kibana service"
dpkg -i kibana-5.3.0-amd64.deb
rm kibana-5.3.0-amd64.deb
systemctl enable kibana.service
systemctl start kibana

SCRIPT


Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 8192
    vb.cpus = 4
    vb.gui = true
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
  end
  
  config.vm.define :dev do |dev|
    dev.vm.box = "boxcutter/ubuntu1604-desktop"
    dev.vm.provision :shell, inline: $services_install_script
    dev.vm.provision :shell, inline: $module_requirements_install_script
    dev.vm.provision :shell, inline: $module_environment_install_script, privileged: false
    dev.vm.provision :shell, inline: $dev_module_install_script, privileged: false
  end
  
end
