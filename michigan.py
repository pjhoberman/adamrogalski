import shutil
from urllib.request import urlretrieve
from urllib.parse import urlparse
import csv
import re
import os

from PIL import Image
from bs4 import BeautifulSoup
import requests

CONTACT = {
    "side": "Senate",
    "name": "",
    "page_link": "",
    "district": "",
    "party": "",
    "title": "",
    "image_url": "",
    "saved_image": "",
}


def download_image(side, url, fn, extension=".jpg"):
    directory = f"michigan/{side}"
    os.makedirs(directory, exist_ok=True)
    dest = f"{directory}/{fn}{extension}"
    urlretrieve(url, dest)

    # downsize images
    if os.stat(dest).st_size / 1000 > 300:  # over 300k
        size = os.stat(dest).st_size / 1000
        # shutil.copyfile(f"{side}/{fn}.jpg", f"{side}/{fn}.original.jpg")
        img = Image.open(dest)
        quality = 100
        if size > 1000:
            quality = 33
        elif size > 500:
            quality = 50
        elif size > 300:
            quality = 75
        img.save(dest, quality=quality)


def scrape_michigan_senators():
    base_url = "https://senate.michigan.gov/"
    senator_url = "https://senate.michigan.gov/senatorinfo_complete.html"
    req = requests.get(senator_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    data = []
    el = soup.find("h1", text="Senators")
    _contact = CONTACT.copy()
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
                    district = el.h2.nextSibling.nextSibling.nextSibling.text  # .replace("(PDF)", "").replace("Map", "").replace("  ", " ")
                else:
                    district = el.h2.nextSibling.nextSibling.text  # .replace("(PDF)", "").replace("Map", "").replace("  ", " ")
                district = re.findall(r"\d+", district)[0]
                # print(name)
                # print(district)
                # print("\n")
                if not urlparse(url).netloc:
                    url = base_url + url

                _contact["name"] = name
                _contact["page_link"] = url
                _contact["district"] = district
                _contact["party"] = party
                data.append(_contact)
                _contact = CONTACT.copy()
        # elif tag == "strong":
        #     # committees
        #     committees = el.nextSibling.text
        #     pass
        el = el.nextSibling

    # download images
    for record in data:
        fn = record.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
        if not os.path.isfile(f"michigan/senate/{fn}.jpg"):
            download_image("senate",
                           record.get("image_url"),
                           fn)
        record["saved_image"] = f"michigan/senate/{fn}.jpg"

    write_header = not os.path.isfile("michigan.csv")
    with open("michigan.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=CONTACT.keys())
        if write_header:
            writer.writeheader()
        writer.writerows(data)

def scrape_michigan_house():
    req = requests.get("https://www.house.mi.gov/AllRepresentatives")
    soup = BeautifulSoup(req.content, 'html.parser')

    # republicans = soup.find(id="republicanlist").findChildren("li")
    # democrats = soup.find(id="democratlist").findChildren("li")
    members = soup.find(id="allrepslist").findChildren("li")
    data = []
    for rep in members:
        # skip first one
        contact = CONTACT.copy()
        contact['side'] = "House"

        try:
            row1, row2 = rep.find_all(class_="row")
        except ValueError:
            continue  # skip empty ones
        name, party, district = re.fullmatch(r"(.*) \((\w).*\) District-(\d+)", row1.text.strip()).groups()
        ln, fn = name.split(",")
        name = f"{fn.strip()} {ln.strip()}"
        contact['party'] = party
        contact['name'] = name
        contact['district'] = district
        try:
            contact['page_link'] = row1.find('a').attrs.get('href')
        except AttributeError:
            pass  # no link
        data.append(contact)

    print("Downloading images")
    for i, rep in enumerate(data):
        print(f"\t{i}/{len(data)}")
        link = rep.get("page_link")
        if not link:
            continue

        base = urlparse(link).netloc

        if base == "gophouse.org":
            res = requests.get(link)
            soup = BeautifulSoup(res.content, 'html.parser')
            img_url = soup.find("img", class_="w-full").attrs.get("src")
            rep['image_url'] = img_url
            fn = rep.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
            _, ext = os.path.splitext(img_url)
            if not os.path.isfile(f"michigan/house/{fn}{ext}"):
                download_image("house", img_url, fn, extension=ext)
            rep["saved_image"] = f"michigan/house/{fn}{ext}"

        elif base == "housedems.com":
            res = requests.get(link)
            soup = BeautifulSoup(res.content, 'html.parser')
            try:
                img_url = soup.find(class_="post-content").findChild('div', class_="lazyload").attrs.get("data-bg-url")
            except AttributeError:
                rep["saved_image"] = "post content not found"
                continue
            if not img_url:
                rep['saved_image'] = "x"
                rep['image_url'] = "x"
                continue
            rep['image_url'] = img_url
            fn = rep.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
            if not os.path.isfile(f"michigan/house/{fn}.jpg"):
                download_image("house", img_url, fn)
            rep["saved_image"] = f"michigan/house/{fn}.jpg"

        else:
            rep['saved_image'] = "None"
            rep['image_url'] = "None"

    write_header = not os.path.isfile("michigan.csv")
    with open("michigan.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=CONTACT.keys())
        if write_header:
            writer.writeheader()  # don't write row if this is after senate
        writer.writerows(data)



if __name__ == '__main__':
    scrape_michigan_senators()
    scrape_michigan_house()
