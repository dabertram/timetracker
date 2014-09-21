# install https://github.com/pttp/python-redmine.git
##
import redmine
from redmine.resultsets import ResourceSet
import trello
import TrelloManager


# http://python-redmine.readthedocs.org/
###################### redmine config ######################

projectname_config = ""
redmine_url = ""
api_key = ""

###################### redmine functions ######################


# alternative approach
# use rest api directly to set custom fields. can only use pre-defined custom fields? look for rest examples..
#
#

# #!/usr/bin/python
# import httplib
# import sys
# import json
#
# def openissue(data):
#
#     mykey = "dsds....adsadasdasdasdsadsadsadasdasdasdasda"
#     jsondata = json.dumps(data)
#     # Log into Redmine
#     conn = httplib.HTTPSConnection("oursite.internal.com")
#
#     headers = { "Content-Type" : "application/json",
#                 "X-Redmine-API-Key" : mykey
#               }
#     conn.request("POST", "/redmine/issues.json", jsondata, headers)
#
#     response = conn.getresponse()
#
# data = {
#    "issue": {
#       "project_id":"testproject",
#       "tracker":"Bug",
#       "subject": "test",
#       "custom_fields": [ {"id":7,"value":"2013-01-01"}]
#    }
# }
#
# openissue(data)


#################################################################



class RedmineManager:

    redmine = None

    open_issues = {}
    assigned_issues = {}

    def __init__(self):
        self.project_name = None
        self.configuration = None

    def connect_redmine(self, configuration):
        self.project_name = configuration["redmine_projectname"]
        self.configuration = configuration
        self.redmine = redmine.Redmine(configuration["redmine_url"],
                                       key=configuration["redmine_api_key"],
                                       raise_attr_exception=False)

    def __del__(self):
        self.redmine = None


    def is_checklistItem_in_issues(self, checklistItem):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])

        issueID = "(" + checklistItem["name"] + ")"  # + "{" + card + "}"

        exists = False
        for issue in issues:
            description = issue.description
            subject = issue.subject
            print subject, subject.__class__

            if description.endswith(issueID):
                print "issue for this checklistItem already exists!"
                exists = True
                break

        return exists

    def is_checklist_in_issues(self, checklist):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])

        assert isinstance(checklist, trello.Checklist)

        card = checklist.trello_card
        # print card, card.__class__
        # assert isinstance(card, trello.Card)
        # card.fetch()

        issueID = "[" + checklist.id + "]"  # + "{" + card + "}"
        issueName = checklist.name

        # exists = False
        # for issue in issues:
        #     checklistID = issue.custom_fields["trello_checklistID"]
        #     subject = issue.subject
        #     print subject, subject.__class__
        #
        #     if checklistID == checklist.id:
        #         print "issue for this checklist already exists!"
        #         exists = True
        #         break

        exists = False
        for issue in issues:
            description = issue.description
            subject = issue.subject
            print subject, subject.__class__

            if description.endswith(issueID):
                print "issue for this checklist already exists!"
                exists = True
                break

        return exists

    def is_card_in_issues(self, card):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])

        issueID = "{" + card.id + "}"
        issueName = card.name


        exists = False
        for issue in issues:
            description = issue.description
            subject = issue.subject

            print subject, subject.__class__

            if isinstance(description, unicode):
                if description.endswith(issueID):
                    print "issue for this card already exists!"
                    exists = True
                    break

        print "exists:", exists

        return exists


    def create_all_issues_from_card(self, card):
        self.create_issue_from_card(card)
        assert isinstance(card, trello.Card)
        # card.fetch()
        print dir(card)
        for checklist in card.checklists:
            self.create_issue_from_checklist(checklist, card)
            self.create_issues_from_checklistItems(checklist, card)

    def create_issue_from_card(self, card):
        assert isinstance(card, trello.Card)

        if not self.is_card_in_issues(card):

            issueID = "{" + card.id + "}"
            issueName = card.name

            description = issueID
            print "new issue name"
            print issueName, issueID

            # check existing issues for card id
            ## if not found -> create issue
            issue = self.redmine.issue.new()
            issue.subject = issueName
            issue.project_id = self.project_name
            issue.description = description
            # issue.custom_fields = [{"trello_cardID": card.id}]
            issue.save()

    def create_issue_from_checklist(self, checklist, card):
        assert isinstance(checklist, trello.Checklist)

        if not self.is_checklist_in_issues(checklist):

            issueID = "[" + checklist.id + "]"      # + "{" + card + "}"
            issueName = checklist.name + " [" + card.name + "]"

            description = issueID
            print "new issue name"
            print issueName, issueID

            # check existing issues for card id
            ## if not found -> create issue
            issue = self.redmine.issue.new()
            issue.subject = issueName
            issue.project_id = self.project_name
            issue.description = description
            parent_issue = self.get_issue_from_cardID(card.id)
            issue.parent_issue_id = parent_issue.id
            # issue.custom_fields = [{"trello_checklistID": checklist.id}]

            issue.save()

            # relation = self.redmine.issue_relation.new()
            #
            # relation.issue_id = issue.id
            # relation.issue_to_id = parent_issue.id
            # relation.relation_type = 'follows'
            # relation.delay = 0
            # relation.save()

            print "parent_issue.children:", parent_issue.children

    def create_issues_from_checklistItems(self,  checklist, card):
        assert isinstance(checklist, trello.Checklist)

        for item in checklist.items:

            if not self.is_checklistItem_in_issues(item):

                issueID = "(" + item["name"] + ")"      # + "{" + card + "}"
                issueName = item["name"] + " (" + checklist.name + ")"

                description = issueID
                print "new issue name"
                print issueName, issueID

                # check existing issues for card id
                ## if not found -> create issue
                issue = self.redmine.issue.new()
                issue.subject = issueName
                issue.project_id = self.project_name
                issue.description = description
                parent_issue = self.get_issue_from_checklistID(checklist.id)
                issue.parent_issue_id = parent_issue.id
                # issue.custom_fields = [{"trello_checklistID": checklist.id}]

        # from example:
        #custom_fields=[{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}])

                issue.save()


                print "parent_issue.children:", parent_issue.children


    def get_issue_from_cardID(self, cardID):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])

        issueID = None
        for issue in issues:
            assert isinstance(issue.description, unicode)
            find_issueID = "{" + cardID + "}"
            if issue.description.endswith(find_issueID):
                print "found issue for parent issue:", issue, dir(issue)
                return issue

    def get_issue_from_checklistID(self, cardID):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])

        issueID = None
        for issue in issues:
            assert isinstance(issue.description, unicode)
            find_issueID = "[" + cardID + "]"
            if issue.description.endswith(find_issueID):
                print "found issue for parent issue:", issue, dir(issue)
                return issue

    def get_issues(self):
        issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])
        return issues


# ################### OLD ##########################
# # first try out functions ##### just use as templates
#     def print_resource_set(self, resourceset):
#         for entry in resourceset:
#             if isinstance(entry, ResourceSet):
#                 print "2 extracting value.."
#                 self.print_resource_set(entry)
#             else:
#                 print " ++ ", entry
#
#     def sort_issues(self, issues):
#         print "sorting issues into open and assigned:"
#
#         self.open_issues = {}
#         self.assigned_issues = {}
#
#         for issue in issues:
#             if issue.assigned_to_id:
#                 self.assigned_issues[issue.subject] = issue
#             else:
#                 self.open_issues[issue.subject] = issue
#         print "finished sorting issues."
#
#
#     def print_issue(self, issue):
#         print " issue: ", issue.subject
#         for attribute in dir(issue):
#             if attribute == "time_entries":
#                 self.print_time_entries(issue[attribute])
#             elif attribute == "children":
#                 print " skipped: ", attribute, "..because it was crashing.. why?"
#             elif isinstance(issue[attribute], ResourceSet):
#                 print "1 extracting value..", attribute
#                 self.print_resource_set(issue[attribute])
#             else:
#                 print "   - ", attribute, ":", issue[attribute]
#
#     def print_time_entries(self, time_entries):
#         print "    time_entries:"
#         for time_entry in time_entries:
#             print "    -- entry: "
#             for attribute in dir(time_entry):
#                 try:
#                     print "    --- ", attribute, ":", time_entry[attribute]
#                 except Exception as e:
#                     print
#                     print "!!", e
#                     print
#
#     def redmine_first_steps(self):
#
#         print ""
#         print "##################### Hello from RedmineManager ######################"
#         print
#
#
#         project = self.redmine.project.get(self.configuration["redmine_projectname"])
#         print "loaded project:", project.name, "from:", self.configuration["redmine_url"], "object:", project
#
#         print "loading project issues.."
#         issues = self.redmine.issue.filter(project_id=self.configuration["redmine_projectname"])
#         print "loaded issues:", issues
#
#         self.sort_issues(issues)
#
#         print
#         print "listing all open issues:", self.open_issues
#         for issue in self.open_issues.values():
#             self.print_issue(issue)
#
#         print
#         print "listing all assigned issues:", self.assigned_issues
#         for issue in self.assigned_issues.values():
#             self.print_issue(issue)