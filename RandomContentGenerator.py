# MSc Cyber Security - DMU 2016
# Extending Our Cyber-Range CYRAN with Social Engineering Capabilities
#
# Random content generator for social networks for use as part
# of a cyber range setup, to add social engineering abilities.
# Setup to post to Friendica and Pump.io
#
# This script is to be run on the system running the target
# social network for it to work.
#
# Build date: 8/9/2016 17:27
#
# Sam Braidley
# P12189936
#!/usr/bin/env python3
import random
import friendica
import os
import sys

try:
    sys.argv[1]
except IndexError:
    print('Invalid parameters, include the social network you wish to post to ./RandomContentGenerator.py (friendica|pumpio)')
    sys.exit(2)

if sys.argv[1] == "friendica":
    print('Setting social media platform to Friendica')
    social_network = 'friendica'
    userServerFile = open("settings/friendica_ip.txt", "r")
    userServer = userServerFile.readline()
elif sys.argv[1] == "pumpio":
    print('Setting social media platform to Pump.io')
    social_network = 'pumpio'
else:
    print('RandomContentGenerator.py SocialNetworkName')
    sys.exit(2)

PATH_TEMPLATE = 'lists/default_{}s.txt'
    
def post_to_friendica(userMessage):
    "This function posts passed content to Friendica based on the configuration file friendica_settings.txt"
    tempUsername, tempPassword = get_friendica_login_details()
    #userServerFile = open("settings/friendica_ip.txt", "r")
    #userServer = userServerFile.readline()
    # make a new instance of friendica
    f = friendica.friendica (server = userServer, username = tempUsername, password = tempPassword, useHTTPS=False)
    # check that we are logged in
    f.account_verify_credentials()
    # post something with the default settings
    f.statuses_update( status = userMessage )
    print ('Message Posted!')
    print (userServer)
    return
    
def client_post_to_friendica(post):
    treated_post = post.split("CLIENT,")[1]
    cl_username, cl_password, cl_message = treated_post.split(',')
    #userServerFile = open("settings/friendica_ip.txt", "r")
    #userServer = userServerFile.readline()
    # make a new instance of friendica
    f = friendica.friendica (server = userServer, username = cl_username, password = cl_password, useHTTPS=False)
    # check that we are logged in
    f.account_verify_credentials()
    # post something with the default settings
    f.statuses_update( status = cl_message )
    print (userServer)
    print ('Client Message Posted!')
    
    
def post_to_pumpio(message):
    "This function posts passed content to Pump.io"
    username = get_post_io_username()
    os.system("cd /srv/pump.io/bin; ./pump-post-note -u " + username + " -n " + '"{}"'.format(message))
    print("Pump.io Message Posted!")
    
def client_post_to_pumpio(post):
    #Drops unneeded CLIENT tag and password
    cl_username = post.split(',')[1]
    cl_message = post.split(',')[3]
    os.system("cd /srv/pump.io/bin; ./pump-post-note -u " + cl_username + " -n " + '"{}"'.format(cl_message))
    print("Client Pump.io Message Posted!")
    

def get_post_io_username():
    "This function chooses a random Pump.io username to post to based on the list found in pumpio_accounts.txt"
    userAccountFile = open("settings/pumpio_accounts.txt", "r")
    PumpIOAccounts = userAccountFile.read().splitlines()
    UsernameToReturn = random.choice(PumpIOAccounts)
    userAccountFile.close()
    return UsernameToReturn    


def get_friendica_login_details():
    "This function retrieves a random set of Friendica login details based on the list found in friendica_accounts.txt"
    userAccountFile = open("settings/friendica_accounts.txt", "r")
    FriendicaAccounts = userAccountFile.read().splitlines()
    LoginToReturn = random.choice(FriendicaAccounts)
    username, password = LoginToReturn.split(',')
    userAccountFile.close()
    return username, password
    
def file_length(file_name):
    "This function returns the length of a given file"
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def main():
    "The main function of the script itself."
    replacer = StringReplacer(PATH_TEMPLATE)
    
    client_settings_file = open("settings/client_settings.txt", "r")
    maximum_posts = int(client_settings_file.readline().rstrip())
    
    number_of_client_posts = file_length("lists/client_posts.txt")
    print("Number of client posts")
    print(number_of_client_posts)
    
    number_of_random_posts = (maximum_posts - number_of_client_posts)
    print("Number of random posts")
    print(number_of_random_posts)
    
    
    client_posts_file = open("lists/client_posts.txt", "r")
    client_posts = client_posts_file.read().split('\n')
    
    selected_posts = []
    postCounter = 0
    while postCounter < number_of_random_posts:
        text_file = open("lists/default_posts.txt", "r")
        default_posts = text_file.read().splitlines()
        selected_post = random.choice(default_posts)
        post_to_append = replacer.process(selected_post)
        selected_posts.append(post_to_append)
       # print(postCounter)
        postCounter += 1

    #Removes the need to shuffle the list as ordering information is lost
    posts_to_send = list(set(selected_posts + client_posts))
   # print(posts_to_send)
    
    
    postCounter = 0
    while postCounter < len(posts_to_send):
        if social_network == "friendica":
            if posts_to_send[postCounter].count("CLIENT,") == 1:
                client_post_to_friendica(posts_to_send[postCounter])
                postCounter +=1
            else:
                post_to_friendica(posts_to_send[postCounter])
                postCounter +=1
        elif social_network == "pumpio":
            if posts_to_send[postCounter].count("CLIENT,") == 1:
                client_post_to_pumpio(posts_to_send[postCounter])
                postCounter +=1
            else:
                post_to_pumpio(posts_to_send[postCounter])
                postCounter +=1
        else:
            print("Incorrect social network setting. Please re-run with valid social network.")
            sys.exit(2)


class StringReplacer:

    """StringReplacer(path_template) -> StringReplacer instance"""

    def __init__(self, path_template):
        """Initialize the instance attribute of the class."""
        self.path_template = path_template
        self.cache = {}

    def process(self, text):
        """Automatically discover text keys and replace them at random."""
        keys = self.load_keys(text)
        result = self.replace_keys(text, keys)
        return result

    def load_keys(self, text):
        """Discover what replacements can be made in a string."""
        keys = {}
        while True:
            try:
                text.format(**keys)
            except KeyError as error:
                key = error.args[0]
                self.load_to_cache(key)
                keys[key] = ''
            else:
                return keys

    def load_to_cache(self, key):
        """Warm up the cache as needed in preparation for replacements."""
        if key not in self.cache:
            with open(self.path_template.format(key)) as file:
                unique = set(filter(None, map(str.strip, file)))
            self.cache[key] = tuple(unique)

    def replace_keys(self, text, keys):
        """Build a dictionary of random replacements and run formatting."""
        for key in keys:
            keys[key] = random.choice(self.cache[key])
        new_string = text.format(**keys)
        return new_string

if __name__ == '__main__':
    main()
