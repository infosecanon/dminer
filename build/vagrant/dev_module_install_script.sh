# Create virtualenv for dminer
echo "Creating virtualenv for dminer"
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
mkvirtualenv dminer

# Install the dminer in develop mode, and install all necessary dependencies
cd /vagrant
pip install -r dev-requirements.txt
python setup.py develop
