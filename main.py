from bs4 import BeautifulSoup
import requests
import re

available = "&available=true" # , "false"
stock_status = "&stock_status=stock" #, "new"
sort = "&sort=price" #, "-price", "-date", ""
page = "&page=1"


search_term = input("Search what?")
search_term = search_term.replace(" ", "%20")


url = f"https://torob.com/search/?query={search_term}"

sorted_url = f"https://torob.com/search/?query={search_term}{page}{stock_status}{available}{sort}"


# print(sorted_url)

# git config --global user.email "arashpoorazam88@gmail.com"
# git config --global user.name "Your Name"