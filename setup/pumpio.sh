#!/bin/bash
# Pump.io installation bash script
# Sam Braidley | DMU 2016

# Initialise system
sudo apt-get update

# Install basic essentials
sudo apt-get install --yes build-essential curl git python-software-properties

# Install latest nodejs
echo "Installing NodeJS..."
sudo apt-get install --yes nodejs-legacy

# Install npm
echo "Installing npm..."
sudo apt-get install --yes npm
    
# Install pump.io & its dependencies
echo "Installing Pump.io and dependencies..."
git clone https://github.com/e14n/pump.io.git
sudo apt-get install --yes graphicsmagick screen
cd pump.io; npm install; cd ..

# Set pump.io uploads folder
echo "\tSetting pump.io uploads folder to /srv/pump.io/uploads/"
mkdir pump.io/uploads

# Install redis
echo "Setting up Redis..."
sudo apt-get --yes install redis-server
cd pump.io; npm install databank-redis; cd ..    

# Move pump.io files and folders to appropriate locations
echo "Moving Pump.io to /srv/ and pump.io.json to /etc/"
sudo mv pump.io.json /etc/pump.io.json
sudo mv pump.io /srv/

# Start pump.io
echo "Starting pump.io..."
sudo screen -S pumpserver -L -dm bash -c "cd /srv/pump.io; npm start"

echo "Installation now complete, please ensure you follow the instructions to register the cli application and add users before running the random content generation script"
