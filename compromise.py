import requests
from bs4 import BeautifulSoup
import csv
import json


def winner_name(soup):
    winner_element = soup.find(
        'div', class_='win text-uppercase text-white p-1 m-1')
    if winner_element:
        name_element = winner_element.find_next('h2', class_='h3')
        name = name_element.text.strip()
        return name
    return "Not found"


def loser_name(soup):
    loser_element = soup.find(
        'div', class_='loss text-uppercase text-white p-1 m-1')
    if loser_element:
        name_element = loser_element.find_next('h2', class_='h3')
        name = name_element.text.strip()
        return name
    return "Not found"


def data_son(soup_son):
    table = soup_son.find('div', class_="content-wrapper text-center")
    table_data = []
    if table is not None:
        headers_row, *data_rows = table.find_all('tr')
        headers = [th.get_text(strip=True)
                   for th in headers_row.find_all('th')]
        table_data.append(headers)
        for row in data_rows:
            cells = row.find_all('td')
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            table_data.append(cell_texts)
    return table_data


def data_grandson(table):
    table_data = []
    data_rows = table.find_all('tr')
    for row in data_rows:
        cells = row.find_all('td')
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        table_data.append(cell_texts)
    return table_data


r = requests.get("https://boxstat.co/punch-stats")
r.encoding = "UTF-8"
soup_father = BeautifulSoup(r.text, "lxml")
tag_list = soup_father.find_all("a", class_="btn btn-primary")

for link in tag_list:
    r2 = requests.get("https://boxstat.co" + link.get('href'))
    r2.encoding = "UTF-8"
    soup_son = BeautifulSoup(r2.text, "lxml")
    winner = winner_name(soup_son)
    loser = loser_name(soup_son)
    print("winner:", winner, "  loser:", loser)

    link_text = soup_son.find(
        'div', class_="card-header text-center mb-2").get_text()

    filename = link_text.replace('\n', '').replace(
        ' ', '_').replace('-', '_') + '.csv'

    grandson_links = soup_son.find_all(
        'a', class_="list-group-item list-group-item-action")

    with open(filename, "w", newline='', encoding="UTF-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["winner:", winner])
        writer.writerow(["loser:", loser])
        writer.writerows(data_son(soup_son))

        for link1 in grandson_links:
            r3 = requests.get(link1.get('href'))
            r3.encoding = "UTF-8"
            response_json = r3.json()
            html_string = response_json.get("html")
            soup_grandson = BeautifulSoup(html_string, 'lxml')
            tbody_tags = soup_grandson.find_all('tbody')
            for tbody in tbody_tags:
                table_data = data_grandson(tbody)
                # Transpose the data
                transposed_data = list(map(list, zip(*table_data)))
                writer.writerows(transposed_data)
                writer.writerow([])
