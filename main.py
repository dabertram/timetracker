import kivy
kivy.require('1.0.5')

__version__ = "0.1"

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty

import threading

#http://kivy.org/planet/page/3/
class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    label_wid = ObjectProperty()
    info = StringProperty()

    def do_action(self, string):
        self.label_wid.text = self.label_wid.text + string

        self.info = 'New info text'

    def get_issues(self):
        print "Redmine-Trello"

        try:

            configManager = ConfigManager.ConfigManager(False)
            configManager.loadConfigurationFromFiles()

            configuration = configManager.redmineTrelloConfiguration

            trelloManager = TrelloManager()
            trelloManager.connect_trello(configuration)

            redmineManager = RedmineManager()
            redmineManager.connect_redmine(configuration)

            for issue in redmineManager.get_issues():
                self.do_action( "\n" + str(issue.description))

            #redmineManager.redmine_first_steps()

            #unlinkedCards = trelloManager.get_unlinked_cards(configuration["trello_projectname"])
            #for card in unlinkedCards:
                #redmineManager.create_issue_from_card(card)

                #redmineManager.create_all_issues_from_card(card)

            # for card in TrelloManager().get_unlinked_cards("Redmine-Trello-Workflow"):
            #     RedmineManager().create_issue_from_unlinked_card(card)
            #
            #trelloManager.get_linked_cards(configuration["trello_projectname"])

            print "TODO:"
            print " - export all relevant trello fields (planned time, due date, assigned, ..)"
            print " - update already existing issues with plausible new values from trello"
            print " - update trello checklist items from redmine issue status"
            print " - move trello card to 'in progress board', when at least 1 subtask has status in progress"
            print " - move trello card to 'review board', when all subtasks reach 'resolved' or any higher status"
            print
            print "## need to think about:"
            print " - mark issues when card is moved to another board via trello"
            print " - generate/create/export gantt to trello (where ever in there)"
            print
            print " - update trello from updated issues"
            print " - create trello board that reflects anything that is going on with trackers like: bug, problem, whatever else.."
            print " - export features from redmine that trello misses (time-tracking, gantt-stuff if needed, ...)"
            print " - map more high-level structures (versions, milestones, ..)"

            print
            print
            print
            print "Redmine-Trello FINISHED"

        except trello.Unauthorized as error:
            print
            print
            print "Redmine-Trello CRASHED because of expired token:", error
            print
            print
            # raise
        ## disabled this catch-all to have better debuggable output in console
        except Exception as e:
            print
            print e
            print
            print "Redmine-Trello CRASHED!"
            # re-raise exception to get clickable links to calls in console
            # raise

        print "if token expired, delete config-files and restart to generate new tokens"


class ControllerApp(App, threading.Thread):

    controller = None

    def __init__(self):
        super(ControllerApp, self).__init__()



    def build(self):
        self.controller = Controller(info='Hello world')
        self.controller.get_issues()
        return self.controller


   def on_pause(self):
      # Here you can save data if needed
      return True


   def on_resume(self):
      # Here you can check if any data needs replacing (usually nothing)
      pass


from RedmineManager import RedmineManager
from TrelloManager import TrelloManager
import trello
import ConfigManager

if __name__ == '__main__':


###################### main ######################

    gui = ControllerApp()
    gui.run()


