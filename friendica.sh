#!/bin/bash
# Friendica installation bash script
# Sam Braidley | DMU 2016

read -p "Are you running this as root? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
	# Initialise system
	sudo apt-get update

	# Upgrade system to latest updates
	sudo apt-get --yes upgrade

	#Install MySQL Server
	sudo apt-get install --yes mysql-server 

	# Install essentials
	sudo apt-get install --yes php5-curl php5-cli php5-gd libapache2-mod-php5 mcrypt python3 unzip php5-mysql php5-mcrypt

	# Remove index.html from /var/www/html
	sudo rm /var/www/html/index.html

	# Enabled rewrite
	sudo a2enmod rewrite

	# Restart apache2
	sudo service apache2 restart

	# Copy config 
	sudo cp 000-default.conf /etc/apache2/sites-enabled/000-default.conf

	# Restart apache2
	sudo service apache2 restart

	# Change directory to /var/www/html
	cd /var/www/html

	# Get the latest build of Friendica
	sudo wget https://github.com/friendica/friendica/archive/master.zip

	# Unzip 
	unzip master.zip

	# Change directory to now extracted Friendica build
	cd friendica-master

	# Move all contents up one directory
	sudo mv * ..

	# Move back up one directory
	cd ..

	# Remove now empty directory
	sudo rm -rf friendica-master

	# Change ownership of files 
	sudo chown www-data:www-data -R *

	# Ensure we are in /var/www/html
	cd /var/www/html

	# Download .htaccess file from Github
	sudo wget https://raw.githubusercontent.com/friendica/friendica/master/.htaccess

	# php5enmod
	sudo php5enmod mcrypt

	# Restart apache2
	sudo service apache2 restart
	 
	# End of automated setup, user interacton required
	echo "Automated installation nearly complete.."
	echo "MySQL is about to open, login with the password you created during setup and create a friendica database then exit MySQL"
	echo "Use the command: 'create databases friendica;'' to create the database and the command: 'exit' to quit."

	mysql --password

	echo "Now the installation is nearly finished, open your web browser and visit your computers IP address in order to finish the installation process."
fi
if [[ $REPLY =~ ^[Nn]$ ]]
then
	echo "Run the command 'sudo su -u' and re-run this script."
fi

