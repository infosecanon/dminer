# Configure environment variables and load them
echo "Configuring environment variables"
echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
echo "PATH=$PATH:~/" >> ~/.bashrc
echo "export DISPLAY=:0.0" >> ~/.bashrc
echo "workon dminer" >> ~/.bashrc
source ~/.bashrc

# Download, unpack, and set in path the geckodriver
echo "Downloading and installing geckodriver to users home directory"
cd ~/Downloads
wget -nv https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz
tar -xvf geckodriver-v0.16.1-linux64.tar.gz
mv geckodriver ~/geckodriver
