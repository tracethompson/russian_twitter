import sys
import csv
import urllib2

filteredUserNames = []
activeUsers = 0
bannedUsers = 0
nonUsers = 0

# this reads the csv with containing id/usernames and creates a filtered list with just the usernames
with open('./tmp/data.csv', 'rb') as csvfile:
  datareader = csv.reader(csvfile, delimiter=' ', quotechar='|')
  for row in datareader:
      # create the list, split the id and username, grab username
      username = ', '.join(row).split(',')[1]
      # check for blank lines
      if username != '':
        filteredUserNames.append(username)

# this class determins if a url is redirected based on header status code
class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

opener = urllib2.build_opener(NoRedirectHandler())
urllib2.install_opener(opener)

# change this file name to any file name that you want to write to
with open('./tmp/banned-users.csv', 'wb') as csvfile:
  filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  for user in filteredUserNames:
    # create the basic url with the username
    url = 'https://twitter.com/%s' % user
    print 'pinging %s' % url
    try:
      # request the resource
      request = urllib2.Request(url)
      response = urllib2.urlopen(request)
      # this will catch redirects which happen when a user is banned
      if response.code in (300, 301, 302, 303, 307):
        bannedUsers += 1
        # this filewriter.writerow is what appends lines to the csv document
        filewriter.writerow([user])
      # if the request does not error or redirect we know it's an active account
      else:
        activeUsers += 1
    # this catches any errors (404 etc..)
    except urllib2.HTTPError, e:
      nonUsers += 1

with open('./tmp/totals.csv', 'wb') as csvfile:
  filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  totalUsers = len(filteredUserNames)
  filewriter.writerow(['total users', totalUsers])
  filewriter.writerow(['total active users', activeUsers])
  filewriter.writerow(['total banned users', bannedUsers])
  filewriter.writerow(['total users that 404', nonUsers])