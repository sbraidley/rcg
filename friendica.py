#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
friendica.py

A python 3 module to access the Friendica API.

See https://github.com/friendica/friendica/wiki/Friendica-API for the
documentation of the friendica API.

Author: Tobias Diekershoff

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of the <organization> nor the  names of its
      contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Tobias Diekershoff BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import json
from urllib.request import urlopen, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener, ProxyHandler, HTTPCookieProcessor, Request
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from xml.dom import minidom

_debug_ = False
__name__ = 'friendica.py'
__version_major__   = 0
__version_minor__   = 3
__version_release__ = 1
__version_string__  = "%d.%d-%d" % (__version_major__, __version_minor__, __version_release__)
__full_version__ = __name__ + ' ' + __version_string__

class poco:
    """
    class to access the POCO information for an account
    """
    def __init__ (self, server, user, directory = "", useHTTPS = True, 
            timeout = 10, pocopath = "", proxy = ""):
        """
        parameters
        *  server (string)      name of the server that should be requested
        *  directory (string)   friendica can be installed into a subdirectory
                                of the server. if done so specify the directory
        *  user (string)        for which user should the POCO information
                                be fetched
        *  pocopath (string)    alternatively to calculate the path for the
                                POCO request you can pass it as a parameter
        *  useHTTPS (boolean)   use HTTPS (true) or not (false) default is yes
        *  timeout (integer)    timeout for the network requests
                                default is to wait 10 second
        *  proxy (string)       proxy to be used for the connection
        """
        self.server = server
        self.directory = directory
        self.user = user
        self.useHTTPS = useHTTPS
        self.timeout = timeout
        self.proxy = proxy
        self.raw = None
        if len(pocopath):
            self.pocopath = pocopath
        else:
            self.pocopath = self.server+'/'+directory
            if len(directory):
                if not (directory[-1]=='/'):
                    self.pocopath = self.pocopath+'/'
            self.pocopath = self.pocopath + 'poco'
    def protocol (self):
        if self.useHTTPS:
            return 'https://'
        else:
            return 'http://'
    def getPoco (self):
        """
        get the POCO file from the selected user@server
        returns a JSON list of the POCO information or None
        also saves the information to self.raw and fills self.total and
        self.contacts on success
        """
        try:
            url = self.protocol()+self.pocopath+'/'+self.user
            if not self.proxy:
                self.opener = build_opener()
            else:
                self.proxy_handler = ProxyHandler( {'http': self.proxy,
                    'https':self.proxy } )
                self.opener = build_opener(self.proxy_handler) 
            req = Request( url )
            data = urlopen(req, timeout=self.timeout).readall().decode('utf-8')
            self.raw = json.loads(data)
            self.totalResults = int(self.raw['totalResults'])
            self.contacts = self.raw['entry']
        except:
            self.raw = None
        return self.raw
    def getContact(self, cid):
        """
        returns contact identified by cid (integer)
        """
        return self.contacts[cid]

def yesno(b):
    """
    returns yes if b it true, no if b is false
    """
    if b:
        return "yes"
    else:
        return "no"

class friendica:
    """
    class to access the API of friendica
    """
    def __init__ (self, server, directory = "", username = None,
            password = None, proxy = "", timeout = 10, apipath = None,
            useHTTPS = True, source=__name__):
        """
        parameters
        *  server (string)        name of the server the account is located on
        *  directory (string)     if the friendica instance is located in a
                                  subdirectory, specify it here
        *  apipath (string)       alternatively to calculate the API path from
                                  server name and installation directory you
                                  can specify the path here
        *  username (string)      account name => username@servername
        *  password (string)      the password for the account
        *  proxy (string)         this proxy will be used for connections
                                  to the server
        *  timeout (integer)      seconds to wait for the response during
                                  network requests, default is 10 seconds
        *  useHTTPS (boolean)     use HTTPS (true) or not (false) default is
                                  to use HTTPS and will fallback to HTTP if
                                  that does not work
        *  source (string)        this string will be used as source string,
                                  e.g. client name, when publishing things
        """
        self.server = server
        self.directory = directory
        if (apipath == None):
            self.apipath = self.server+'/'+directory
            if len(directory):
                if not (directory[-1]=='/'):
                    self.apipath = self.apipath+'/'
            self.apipath = self.apipath+'api'
        else:
            self.apipath = apipath
        self.username = username
        self.password = password
        self.proxy = proxy
        self.timeout = timeout
        self.useHTTPS = useHTTPS
        self.source = source
        self.cj = CookieJar()
        self.pwd_mgr = HTTPPasswordMgrWithDefaultRealm()
        self.pwd_mgr.add_password(None, self.protocol()+self.apipath,
                self.username, self.password)
        self.handler = HTTPBasicAuthHandler(self.pwd_mgr)
        if not self.proxy:
            self.opener = build_opener(self.handler,
                    HTTPCookieProcessor(self.cj))
        else:
            self.proxy_handler = ProxyHandler( {'http': proxy,
                'https':proxy } )
            self.opener = build_opener(self.proxy_handler,
                    self.handler, HTTPCookieProcessor(self.cj)) 
    def protocol (self):
        if self.useHTTPS:
            return 'https://'
        else:
            return 'http://'
    def api (self, call, params, method='GET'):
        """
        calls the API and returns the result

        parameters
        *  call (string)          the command passed over to the API
        *  params (dict)          dictionary of parameter key - value pairs
                                  (strings) that will be passed as parameters
                                  for the API call. the parameter "source" will
                                  be added automatically
        """
        install_opener(self.opener)
        params = urlencode(params)
        try:
            url = self.protocol()+self.apipath+call
            if _debug_:
                print('URL: %s' % url)
                print('PARAMS: %s' % params)
            headers = {"Content-type":
                    "application/x-www-form-urlencoded;charset=utf-8"}
            if (method == 'POST'):
                req = Request( url )
                if _debug_:
                    print(str(req))
                ret = urlopen(req, params.encode('utf-8'),
                        timeout=self.timeout).readall().decode('utf-8')
            else:
                req = Request( url +'?'+ params )
                if _debug_:
                    print(url+'?'+params)
                ret = urlopen(req, timeout=self.timeout).readall().decode('utf-8')
            if _debug_:
                print('Result: %s' % ret)
            res = json.loads(ret )
        except:
            res = None
        return res
    def statuses_update (self, status, title="", media="", contact_allow="",
            contact_deny="", group_allow="", group_deny=None,
            longitude="", latitude="", in_reply_to_id="",
            category="", location="", coord="", mailcc="",
            post_to_connector=""):
        """
        send a new message to update the users timeline

        parameters
        *  status (string)       the message that should be posted, plain text
        *  title (string)         the title of the posting
        *  media ()               Image data to attach to the posting
        *  contact_allow (string) comma seperated list of contact IDs
                                  (integers) of contacts that are allowed to
                                  see the posting
        *  contact_deny (string)  see contact_allow, but listed contacts are
                                  denied to see the posting
        *  group_allow (string)   see contact_allow, but for contact groups
        *  group_deny (string)    see contact_deny, but for contact groups
        *  longitude (float)      position of the posting: Longitude
        *  latitude (float)       position of the posting: Latitude
        *  in_reply_to_id (integer) id of the posting this is a reply to
                                  otherwise set in the ACL like 
        *  category (string)      comma seperated list of categories
        *  location (string)      name of the location the post is made from
        *  coord (string)         long/lat coordinates of location
        *  mailcc (string)        comma seperated list of email adresses the
                                  entry should be posted to as well
        *  post_to_connector (string) list of connectors this posting should
                                  be passed to, works only for top-level
                                  postings and only if the posting is public
                                  e.g.: pumpio_enable

                                  FIXME currently not supported
        Setting ACL parameters via the API will override the default settings
        of the user made in the Settings of the friendica account.
        """
        call = '/statuses/update.json'
        params = {'status':status, 'source':self.source}
        if group_deny:
            params['group_deny[]'] = group_deny.split(',')
        if group_allow:
            params['group_allow[]'] = group_allow.split(',')
        if contact_deny:
            params['contact_deny[]'] = contact_deny.split(',')
        if contact_allow:
            params['contact_allow[]'] = contact_allow.split(',')
        if title:
            params['title'] = title
        if media:
            params['media'] = media
        if longitude:
            params['long'] = longitude
        if latitude:
            params['lat'] = latitude
        if in_reply_to_id:
            params['in_reply_to_id'] = in_reply_to_id
        if category:
            params['category'] = cytegory
        if location:
            params['location'] = location
        if coord:
            params['coord'] = coord
        if mailcc:
            params['mailcc'] = mailcc
        # FIXME the post_to_connector string must be parsed and the single post
        # to connectors activated one by one
        return self.api(call, params)
    def post (self, message, title="", media="", contact_allow="",
            contact_deny="", group_allow="", group_deny=None,
            longitude="", latitude="", in_reply_to_id="",
            category="", location="", coord="", mailcc="",
            post_to_connector=""):
        """
        Shortcut to statuses/update
        """
        return self.statuses_update (message, title, media, contact_allow,
                contact_deny, group_allow, group_deny, longitude, latitude,
                in_reply_to_id, category, location, coord, mailcc,
                post_to_connector)
    def new_event (self, event_summary, event_start, event_description=None,
            event_finish=None, event_location=None, event_adjust=False):
        """
        API call: none, uses statuses/update to post a new event
        parameters
        *  event_summary (string)  a short summary of the events
        *  event_start (string, timestamp) the starting time of the event,
                                   format  needs to be YYYY-MM-DD HH:MM:SS
        *  event_description (string) a longer description of the event
        *  event_finish (string, timestap) the finish time for the event
                                   format  needs to be YYYY-MM-DD HH:MM:SS
        *  event_location (string) the location for the event
        *  event_adjust (boolean)  shall the start/finish time be adjusted to
                                   the timezone of the visitors setting by
                                   friendica

        Wrapper function fir statuses/update with the syntax for a new event
        applied to ease posting of new events.
        """
        status = "[event-summary]%s[/event-summary][event-start]%s[/event-start]" % (event_summary, event_start)
        if event_description:
            status = status + '[event-description]%s[/event-description]' % event_description
        if event_finish:
            status = status + '[event-finish]%s[/event-finish]' % event_finish
        if event_location:
            status = status + '[event-location]%s[/event-location]' % event_location
        if event_adjust:
            status = status + '[event-adjust]1[/event-adjust]'
        return self.statuses_update( status = status )
    def account_verify_credentials (self, skip_status=False):
        """
        API call: account/verify_credentials
        parameters
        *  skip_status (boolean)  default False
                                  controls if the status field should be shown
        """
        call = '/account/verify_credentials.json'
        params = {}
        if skip_status:
            params['skip_status'] = yesno(skip_status)
        return self.api(call, params)
    def statuses_home_timeline (self, count=20, page=None, since_id=None,
            max_id=None, exclude_replies=False, conversation_id=None):
        """
        API call: statuses/home_timeline
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  exclude_replies (integer) don't show replies (default: no)
        *  conversation_id (integer) Shows all statuses of a given conversation.
        """
        call = '/statuses/home_timeline.json'
        params = {}
        if count:
            params['count'] = count
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        if exclude_replies:
            params['exclude_replies'] = exclude_replies
        if conversation_id:
            params['conversation_id'] = conversation_id
        return self.api(call, params)
    def statuses_friends_timeline (self, count=20, page=None, since_id=None,
            max_id=None, exclude_replies=False, conversation_id=None):
        """
        API call: statuses/friends_timeline
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  exclude_replies (integer) don't show replies (default: no)
        *  conversation_id (integer) Shows all statuses of a given conversation.
        """
        call = '/statuses/friends_timeline.json'
        params = {}
        if count:
            params['count'] = count
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        if exclude_replies:
            params['exclude_replies'] = exclude_replies
        if conversation_id:
            params['conversation_id'] = conversation_id
        return self.api(call, params)
    def statuses_public_timeline (self, count=20, page=None, since_id=None,
            max_id=None, exclude_replies=False, conversation_id=None):
        """
        API call: statuses/public_timeline
        parameters
        *  count: (integer)       Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  exclude_replies (integer) don't show replies (default: no)
        *  conversation_id (integer) Shows all statuses of a given conversation.
        """
        call = '/statuses/public_timeline.json'
        params = {}
        if count:
            params['count'] = count
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        if exclude_replies:
            params['exclude_replies'] = exclude_replies
        if conversation_id:
            params['conversation_id'] = conversation_id
        return self.api(call, params)
    def statuses_show(self, tid, conversation=0):
        """
        API call: statuses/show
        parameters
        *  tid (integer)         id of the status
        *  conversation (integer) if set to 0 the full conversation of the
                                 status will be returned
        """
        call = '/statuses/show.json'
        params = {'id':tid}
        if conversation:
            params['conversation'] = 1
        return self.api(call, params)
    def users_show(self, user_id=None, screen_name=None):
        """
        API call: users/show
        parameters
        *  user_id (integer)      id of the user
        *  screen_name (string)   screen name (nick) of the user
                                  see API documentation about uniqueness of the
                                  screen names and the search order for users
        
        You have to set one of the parameters in order to get a result. If none
        is set an exception is raised.
        """
        if not (user_id or screen_name):
            raise Exception('either screen_name or user_id has to be set')
        call = '/users/show'
        params = {}
        if user_id:
            params['user_id'] = user_id
        if screen_name:
            params['screen_name'] = screen_name
        return self.api(call, params)
    def statuses_retweet (self, tid):
        """
        API call: statuses/retweet
        parameters
        *  tid (integer)          the id of the status to be repeated/shared
        """
        call = '/statuses/retweet.json'
        params = { 'id':tid }
        return self.api(call, params)
    def statuses_destroy (self, tid):
        """
        API call: statuses/destroy
        parameters
        *  tid (integer)          the id of the status to be destroyed
        """
        call = '/statuses/destroy.json'
        params = { 'id':tid }
        return self.api( call, params )
    def statuses_mentions (self, count=20, page=None, since_id=None,
            max_id=None):
        """
        API call: statuses/mentions
        parameters
        *  count (integer)        the number of mentioned returned
        *  page (integer)         the page of the mentions list
        *  since_id (integer)     the minimal id
        *  max_id (integer)       the maximal id
        """
        call = '/statuses/mentions.json'
        params = { 'count':count }
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def statuses_replies (self, count=20, page=None, since_id=None,
            max_id=None):
        """
        API call: statuses/replies
        parameters
        *  count (integer)        the number of mentioned returned
        *  page (integer)         the page of the mentions list
        *  since_id (integer)     the minimal id
        *  max_id (integer)       the maximal id
        """
        call = '/statuses/replies.json'
        params = { 'count':count }
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def statuses_user_timeline (self, user_id=None, screen_name=None, count=20,
            page=None, since_id=None, max_id=None, exclude_replies=False,
            conversation_id=None):
        """
        API call: statuses/user_timeline
        parameters
        *  user_id (integer)      id of the user 
        *  screen_name (string)   screen name
                                  see the API documentation for information
                                  about the uniqueness and search order of this
                                  value
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  exclude_replies (boolean) don't show replies (default: no)
        *  conversation_id (integer) Shows all statuses of a given conversation.
        """
        if not (user_id or screen_name):
            raise Exception ('either user_id or screen_name has to be specified')
        call = '/statuses/user_timeline.json'
        params = {}
        if user_id:
            params['user_id'] = user_id
        if screen_name:
            params['screen_name'] = screen_name
        if count:
            params['count'] = count
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        if exclude_replies:
            params['exclude_replies'] = yesno(exclude_replies)
        if conversation_id:
            params['conversation_id'] = conversation_id
        return self.api( call, params)
    def favorites (self, count=20, page=None, since_id=None, max_id=None):
        """
        API call: favorited
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        """
        call = '/favorites.json'
        params = { 'count':count }
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def account_rate_limit_status (self):
        """
        API call: account/rate_limit_status
        parameters
        *  none
        """
        call = '/account/rate_limit_status.json'
        params = {}
        return self.api( call, params )
    def help_test (self):
        """
        API call: help/test
        parameters
        *  none
        """
        call = '/help/test.json'
        params = {}
        return self.api( call, params )
    def statuses_friends (self):
        """
        API call: statuses/friends
        parameters
        *  none

        Friendica doesn't allow showing friends of other users.
        """
        call = '/statuses/friends.json'
        params = {}
        return self.api( call, params )
    def statuses_followers (self):
        """
        API call: statuses/followers
        parameters
        *  none

        Friendica doesn't allow showing followers of other users.
        """
        call = '/statuses/followers.json'
        params = {}
        return self.api( call, params )
    def statusnet_config (self):
        """
        API call: statusnet/config
        parameters
        *  none
        """
        call = '/statusnet/config.json'
        params = {}
        return self.api( call, params )
    def statusnet_version (self):
        """
        API call: statusnet/version
        parameters
        *  none
        """
        call = '/statusnet/version.json'
        params = {}
        return self.api( call, params )
    def friends_ids (self, stringify_ids=False):
        """
        API call: friends/ids
        parameters
        *  stringify_ids (boolean) Should the id numbers be sent as text (true)
                                  or number (false)? (default:  no)
        """
        call = '/friends/ids.json'
        params = {}
        if stringify_ids:
            params['stringify_ids'] = yesno(stringify_ids)
        return self.api( call, params )
    def followers_ids (self, stringify_ids=False):
        """
        API call: followers/ids
        parameters
        *  stringify_ids (boolean) Should the id numbers be sent as text (true)
                                  or number (false)? (default:  no)
        """
        call = '/followers/ids.json'
        params = {}
        if stringify_ids:
            params['stringify_ids'] = yesno(stringify_ids)
        return self.api( call, params )
    def direct_messages_new (self, text, user_id=None, screen_name=None,
            replyto=None, title=None):
        """
        API call: direct_messages/new
        parameters
        *  user_id (integer)      id of the user 
        *  screen_name (string)   screen name
        *  text (string)          The message
        *  replyto (integer)      ID of the replied direct message
        *  title (string)         Title of the direct message
        """
        if not (user_id or screen_name):
            raise Exception ('either user_id or screen_name have to be specified')
        call = '/direct_messages/new.json'
        params = { 'text':text }
        if user_id:
            params['user_id']=user_id
        if screen_name:
            params['screen_name'] = screen_name
        if title:
            params['title'] = title
        if replyto:
            params['replyto'] = replyto
        return self.api( call, params )
    def direct_messages_conversation (self, count=20, page=None,
            since_id=None, max_id=None, getText=None, uri=None):
        """
        API call: direct_messages/conversation
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  getText (string)       Defines the format of the status field. Can
                                  be "html" or "plain"
        *  uri (string)           URI of the conversation
        """
        call = '/direct_messages/conversation.json'
        params = { 'count':count }
        if getText in ['html','plain']:
            params['getText'] = getText
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        if uri:
            params['uri'] = uri
        return self.api (call, params)
    def direct_messages_all (self, count=20, page=None, since_id=None,
            max_id=None, getText=None):
        """
        API call: direct_messages/all
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id
        *  getText (string)       Defines the format of the status field. Can
                                  be "html" or "plain"
        """
        call = '/direct_messages/all.json'
        params = { 'count':count }
        if getText in ['html','plain']:
            params['getText'] = getText
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def direct_messages_send (self, count=20, page=None, since_id=None,
            max_id=None, getText=None):
        """
        API call: direct_messages/send
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (iteger)        maximum id
        *  getText (string)       Defines the format of the status field. Can
                                  be "html" or "plain"
        """
        call = '/direct_messages/send.json'
        params = { 'count':count }
        if getText in ['html','plain']:
            params['getText'] = getText
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def direct_messages (self, count=20, page=None, since_id=None, max_id=None,
            getText=None):
        """
        API call: direct_messages
        parameters
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (iteger)        maximum id
        *  getText (string)       Defines the format of the status field. Can
                                  be "html" or "plain"
        """
        call = '/direct_messages.json'
        params = { 'count':count }
        if getText in ['html','plain']:
            params['getText'] = getText
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call, params )
    def oauth_request_token (self, oauth_callback=None):
        """
        API call: oauth/request_token
        parameters
        *  oauth_callback (string)
        """
        call = '/oauth/request_token.json'
        params = {}
        if oauth_callback:
            params['oauth_callback'] = oauth_callback
        return self.api( call, params )
    def oauth_access_token (self, oauth_verifier=None):
        """
        API call: oauth/access_token
        parameters
        *  oauth_verifier (string)
        """
        call = '/oauth/access_token.json'
        params = {}
        if oauth_callback:
            params['oauth_verifier'] = oauth_verifier
        return self.api( call, params )
    def conversation_show(self, tid, count=20, page=None, since_id=None,
            max_id=None):
        """
        API call: conversation/show
        parameters
        *  tid (integer)          id of the post
        *  count (integer)        Items per page (default: 20)
        *  page (integer)         page number
        *  since_id (integer)     minimal id
        *  max_id (integer)       maximum id

        Unofficial Twitter command. It shows all direct answers (excluding the
        original post) to a given id.
        """
        call = '/conversation/show.json'
        params = { 'id':tid, 'count':count }
        if page:
            params['page'] = page
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        return self.api( call,params )
    def ping(self):
        """
        ping the server to get new notifications about
          + intro                 new introductions
          + mail                  new private mails
          + net                   new postings to the network
          + home                  new portings to the personal wall
          + register              new registrations (ony displayed to the
                                  admin of a node)
          + notif                 rich content notifications
          + sysmsgs               system messages (dictionary)
            + notice
            + info
          + events                all events generated by the user
          + events-today          all events generated by the user that are
                                  haüüening today
          + all-events            all events from all the contacts and the user
          + all-events-today      all events from all the contacts and the user
                                  that are happening today
          + birthdays             birthdays of the contacts over the next days
          + birthdays-today       birthdays of the contacts happening today

        return value is a dictionary holding the above information
        """
        pingres = {}
        install_opener(self.opener)
        res = urlopen(self.protocol()+self.apipath[:-4]+'/ping').read().decode('utf-8')
        aping = minidom.parseString(res)
        try:
            pingres['intro'] = int(aping.getElementsByTagName("intro")[0].childNodes[0].data)
        except:
            pingres['intro'] = 0
        try:
            pingres['mail'] = int(aping.getElementsByTagName("mail")[0].childNodes[0].data)
        except:
            pingres['mail'] = 0
        try:
            pingres['net'] = int(aping.getElementsByTagName("net")[0].childNodes[0].data)
        except:
            pingres['net'] = 0
        try:
            pingres['home'] = int(aping.getElementsByTagName("home")[0].childNodes[0].data)
        except:
            pingres['home'] = 0
        try:
            pingres['register'] = int(aping.getElementsByTagName("register")[0].childNodes[0].data)
        except:
            pingres['register'] = 0
        try:
            pingres['events'] = int(aping.getElementsByTagName("events")[0].childNodes[0].data)
        except:
            pingres['events'] = 0
        try:
            pingres['all_events'] = int(aping.getElementsByTagName("all-events")[0].childNodes[0].data)
        except:
            pingres['all_events'] = 0
        try:
            pingres['birthdays'] = int(aping.getElementsByTagName("birthdays")[0].childNodes[0].data)
        except:
            pingres['birthdays'] = 0
        try:
            pingres['events_today'] = int(aping.getElementsByTagName("events-today")[0].childNodes[0].data)
        except:
            pingres['events_today'] = 0
        try:
            pingres['all_events_today'] = int(aping.getElementsByTagName("all-events-today")[0].childNodes[0].data)
        except:
            pingres['all_events_today'] = 0
        try:
            pingres['birthdays_today'] = int(aping.getElementsByTagName("birthdays-today")[0].childNodes[0].data)
        except:
            pingres['birthdays_today'] = 0
        nodes = []
        try:
            notif = aping.getElementsByTagName('notif')[0].childNodes
            for node in notif[:-1]:
                nodes.append( {
                        "url":node.attributes['url'].value,
                        "photo":node.attributes['photo'].value,
                        "href":node.attributes['href'].value,
                        "date":node.attributes['date'].value,
                        "name":node.attributes['name'].value,
                        "data":node.firstChild.data.replace('{0}',node.attributes['name'].value)
                    } )
        except:
            pass
        pingres['notif'] = nodes
        sys_notices = []
        sys_info = []
        try:
            sysmsgs = aping.getElementsByTagName('sysmsgs')[0]
            notices = sysmsgs.getElementsByTagName('notice')
            info = sysmsgs.getElementsByTagName('info')
            for i in notices:
                sys_notices.append(i.firstChild.data)
            for i in info:
                sys_info.append(i.firstChild.data)
        except:
            pass
        pingres['sysmsgs'] = {'notice':sys_notices, 'info':sys_info}
        return pingres
