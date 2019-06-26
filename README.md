# github_hunting
A commandline python tool to search and parse external github for keywords that are provided in a newline seperated list

Three switches are required:

-e [github email address]

-p [github password]

-l [filename of the local file with newline seperated list of search terms in the same working directory as the script]

Example:

python3 githunt.py -e test@test.com -p ThisIsABadPassword123 -l search_these_keywords.txt
