# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.


Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 8192
    vb.cpus = 4
    vb.gui = true
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
  end
  
  config.vm.define :dev do |dev|
    dev.vm.network "forwarded_port", guest: 5601, host: 8080, host_ip: "127.0.0.1"
    dev.vm.box = "boxcutter/ubuntu1604-desktop"
    dev.vm.provision :shell, path: "build/vagrant/services_install_script.sh"
    dev.vm.provision :shell, path: "build/vagrant/module_requirements_install_script.sh"
    dev.vm.provision :shell, path: "build/vagrant/module_environment_install_script.sh", privileged: false
    dev.vm.provision :shell, path: "build/vagrant/dev_module_install_script.sh", privileged: false
    dev.vm.provision :shell, path: "build/utility/download_regressive_data.sh", privileged: false
  end
  
end
