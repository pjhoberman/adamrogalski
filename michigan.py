import csv
import re

from bs4 import BeautifulSoup
import requests


def scrape_michigan():
    base_url = "https://senate.michigan.gov/"
    senator_url = "https://senate.michigan.gov/senatorinfo_complete.html"
    req = requests.get(senator_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    contact = {
        "side": "Senate",
        "name": "",
        "page_link": "",
        "district": "",
        "party": "",
        "title": "",
        "image_url": "",
        "saved_image": "",
    }
    data = []
    el = soup.find("h1", text="Senators")
    _contact = contact.copy()
    while el:
        try:
            class_ = el.attrs.get("class")
        except AttributeError:
            el = el.nextSibling
            continue
        tag = el.name

        if tag == "div":
            if "left" in class_:
                image = el.img.attrs.get("src")
                image_url = base_url + image
                _contact["image_url"] = image_url
            elif "right" in class_:
                # data
                name = el.h2.a.text
                party = re.findall(r"\(\w\)", name)[0]  # get party
                name = name.replace(party, "").strip()  # remove party from name
                ln, fn = name.split(",")
                name = f"{fn.strip()} {ln.strip()}"  # flip name
                party = party.replace("(", "").replace(")","")
                url = el.h2.a.attrs.get("href")
                if el.h2.nextSibling and el.h2.nextSibling != "\n":
                    _contact["title"] = el.h2.nextSibling.strip()
                    district = el.h2.nextSibling.nextSibling.nextSibling.text.replace("(PDF)", "").replace("Map", "").replace("  ", " ")
                else:
                    district = el.h2.nextSibling.nextSibling.text.replace("(PDF)", "").replace("Map", "").replace("  ", " ")
                # print(name)
                # print(district)
                # print("\n")
                _contact["name"] = name
                _contact["page_link"] = url
                _contact["district"] = district
                _contact["party"] = party
                data.append(_contact)
                _contact = contact.copy()
        # elif tag == "strong":
        #     # committees
        #     committees = el.nextSibling.text
        #     pass
        el = el.nextSibling

    with open("michigan.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=contact.keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    scrape_michigan()
