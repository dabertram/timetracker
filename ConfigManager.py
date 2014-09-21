import json
import TrelloManager
import os

home = os.path.expanduser("~")
ConfigFileString = os.path.join(home, "RedmineTrelloConfiguration2.cfg")
DefaultAPIKeyFileString = os.path.join(home, "RedmineTrelloAPIKeyFile2.cfg")


# this class is reading and writing config-files for the API-Keys.
# - these files can be put apart from the source code, so they (and the keys) will not end up in git repository
class ConfigManager:
    """ A python singleton """

    class __impl:
        """ Implementation of the singleton interface """

    # storage for the instance reference
    __instance = None

    def __init__(self, reset_=False):
        """ Create singleton instance """
        # Check whether we already have an instance
        if ConfigManager.__instance is None:
            # Create and remember instance
            ConfigManager.__instance = ConfigManager.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_ConfigManager__instance'] = ConfigManager.__instance

        # this is the dict that holds redmine & trello keys, + user mapping
        self.redmineTrelloConfiguration = None

        if reset_:
            print "creating a new config file"
            self.createConfigFile()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def __del__(self):
        return





    def createConfigFile(self):

        print "creating config file"

        print "experimental!! do NOT use on any productive management system. you have been warned."
        print "experimental!! do NOT use on any productive management system. you have been warned."
        print "experimental!! do NOT use on any productive management system. you have been warned."

        print "enter location for API-Key file [", DefaultAPIKeyFileString, "] : "
        APIFileString = raw_input()
        if APIFileString == "":
            APIFileString = DefaultAPIKeyFileString
        configuration = {"APIKeyFile": APIFileString}

        try:
            with open(ConfigFileString, mode='w') as configfile:
                json.dump(configuration, configfile, indent=2)
        except OSError as e:
            print e.__class__
            print "cannot write file.. exiting!"
            exit()
        print "created config file:", ConfigFileString
        # print ""
        # print "---"
        # print configuration
        # print "---"



    # returns dict with all API keys for Redmine and Trello + user mapping
    def loadConfigurationFromFiles(self):
        if self.redmineTrelloConfiguration is None:
            try:
                APIKeyFile_string = ""
                with open(ConfigFileString, mode='r') as configfile:
                    APIKeyFile_json = json.load(configfile)
                    APIKeyFile_string = APIKeyFile_json["APIKeyFile"]
                print "loaded location of 'real' configuration file:", APIKeyFile_string

                # now load dictionairy that contains API Keys etc..
                self.loadAPIKeys(APIKeyFile_string)

            except IOError as e:
                # identify Exception by it's class name
                print e.__class__
                print e

                self.createConfigFile()
                self.loadConfigurationFromFiles()




    def loadAPIKeys(self, APIKeyFile_string):
        try:
            with open(APIKeyFile_string, mode='r') as APIKeys:
                self.redmineTrelloConfiguration = json.load(APIKeys)

                print "loaded APIKey-File file:", APIKeyFile_string
                # print ""
                # print "---"
                print self.redmineTrelloConfiguration
                # print "---"

        except IOError as e:
            print e.__class__
            print e

            self.createAPIFile(APIKeyFile_string)


    def createAPIFile(self, file_string):
        APIKeys = {}

        print "Enter your redmine projectname:"
        APIKeys["redmine_projectname"] = raw_input()

        print "enter redmine username: "
        APIKeys["redmine_name"] = raw_input()

        print "Enter your redmine api key (from redmine web-interface) :"
        APIKeys["redmine_api_key"] = raw_input()
        print "Enter your redmine url :"
        APIKeys["redmine_url"] = raw_input()


        print "Enter your trello projectname:"
        APIKeys["trello_projectname"] = raw_input()

        print "enter trello username: "
        APIKeys["trello_name"] = raw_input()

        print "Trello API Token Generation:"
        print """log in to your trello account and go to:   https://trello.com/1/appKey/generate"""
        print "enter trello api key: "
        APIKeys["trello_api_key"] = raw_input()

        print "enter trello api secret: "
        APIKeys["trello_api_secret"] = raw_input()

        APIKeys["token_expiration"] = "never"
        print "token expiration is set to:", APIKeys["token_expiration"]

        # generate tokens
        result = TrelloManager.TrelloManager().get_oauth_token_and_secret(APIKeys["trello_api_key"],
                                                                                          APIKeys["trello_api_secret"],
                                                                                          APIKeys["token_expiration"])
        APIKeys["oauth_token"] = result["oauth_token"]
        APIKeys["oauth_token_secret"] = result["oauth_token_secret"]
        self.redmineTrelloConfiguration = APIKeys

        try:
            with open(file_string, mode='w') as APIKeyFile:
                json.dump(APIKeys, APIKeyFile, indent=2)

        except OSError as e:
            print e.__class__
            print "cannot write APIKey-File.. exiting!"
            exit()
        print "created APIKey-File file:", file_string
        # print ""
        # print "---"
        # print APIKeys
        # print "---"

        # exit(1)




