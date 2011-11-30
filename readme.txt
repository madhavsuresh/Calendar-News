# SYSTEM DOCUMENTATION
Meeting Messenger lives ontop of Google App Engine. 
1. A Python backend scans a user's Google Calendar, extracting person and company names from events. 
2. These names are fed into a query system.
3. This query system loads results into an HTML page using Python templating.

# GOOGLE CALENDAR
madhav: talk about auth a little

# QUERY SYSTEM
Person and entity names are queried through several sources.

Company names are queried through the Yahoo! Finance API, where we retrieve
	- News
	- Stock price
	- Blogs
If we can't find this information, we attempt to retrieve the company's twitter (search the company name on Bing and perform a regex search for "twitter.com" on resulting URLs).

Person names are searched using the LinkedIn API. We use the company name to help resolve name ambiguity. 

# FRONT END
Python templates dynamically load data from the backend. A sidebar lists all events with search results; the main page displays the results of our queries and a textbox in which the user can enter notes. The front end is written in HTML5 with some Javascript and is fully up to web standards. 