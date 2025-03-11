from bs4 import BeautifulSoup
import requests
import csv


available = "&available=true" # , "false"
stock_status = "&stock_status=stock" #, "new"
sort = "&sort=price" #, "-price", "-date", ""
page = "&page=1"


# dynamic url 
search_term = input("Search what? ")
search_term = search_term.replace(" ", "%20")
url = f"https://torob.com/search/?query={search_term}{page}{stock_status}{available}{sort}"


# get the html text
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
names = soup.find_all("h2", class_="ProductCard_desktop_product-name__JwqeK")


# respond, should be 200
print(response)
print(url)

# save the found items name and price and saves it into dectionary
items_found = {} 
for name in names:
    # find the parents name
    parent = name.parent
    link = parent.parent['href']
    print(f"https://torob.com/{link}")
    print("")
    # find the price from the parent
    price = parent.find("div", class_="ProductCard_desktop_product-price-text__y20OV").string.split(" ")[0]
    # save both of them in a dictionary
    items_found[name.string] = int(price.replace("٫", ""))


# Save items_found to a CSV file
with open(f"Z_{search_term}_items_found.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Item Name', 'Price'])
    for item_name, price in items_found.items():
        writer.writerow([item_name, price])  