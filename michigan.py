import shutil
from pathlib import Path
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
    directory = Path(f"michigan/{side}")
    os.makedirs(directory, exist_ok=True)
    dest = directory / f"{fn}{extension}"
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
    print("scraping michigan senate")
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

    # hard coded cleanup
    for contact in data:
        if contact['name'] == "John Dr. Bizon":
            contact['name'] = "Dr. John Bizon"
            break

    # download images
    for record in data:
        fn = record.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
        destination = Path(f"michigan/senate/{fn}.jpg")
        if not destination.is_file():
            download_image("senate",
                           record.get("image_url"),
                           fn)
        record["saved_image"] = destination

    write_header = not os.path.isfile("michigan.csv")
    with open("michigan.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=CONTACT.keys())
        if write_header:
            writer.writeheader()
        writer.writerows(data)

def try_other_house_link(name):
    res = requests.get("https://www.legislature.mi.gov/(S(vrj41w0gr3ymhtryc4rq0rso))/mileg.aspx?page=legislators")
    soup = BeautifulSoup(res.content, "html.parser")
    a = None
    for tr in soup.find_all('tr'):
        if name in tr.text:
            for span in tr.find_all("span"):
                if "Web Page" in span.text:
                    a = span.a.attrs.get("href")
                    break
    return a

def get_image_from_other_house_link(name):
    res = requests.get("https://www.legislature.mi.gov/(S(vrj41w0gr3ymhtryc4rq0rso))/mileg.aspx?page=legislators")
    soup = BeautifulSoup(res.content, "html.parser")
    for tr in soup.find_all('tr'):
        if name in tr.text:
            return "https://www.legislature.mi.gov/" + tr.img.attrs.get('src')
    return None



def scrape_michigan_house():
    print("scraping michigan house")
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
        try:
            name, party, district = re.fullmatch(r"(.*) \((\w).*\) District-(\d+)", row1.text.strip()).groups()
        except AttributeError:
            print(row1.text.strip())
            continue
        ln, fn = name.split(",")
        name = f"{fn.strip()} {ln.strip()}"
        contact['party'] = party
        contact['name'] = name
        contact['district'] = district
        try:
            contact['page_link'] = row1.find('a').attrs.get('href')
        except AttributeError:
            page_link = try_other_house_link(name)
            if page_link:
                contact['page_link'] = page_link
            else:
                contact['page_link'] = "no link"
        if "housedems.com" not in contact['page_link'] and "gophouse.org" not in contact['page_link']:
            page_link = try_other_house_link(name)
            if page_link:
                contact['page_link'] = page_link
        data.append(contact)

    # grab titles
    res = requests.get("https://www.house.mi.gov/Leadership")
    soup = BeautifulSoup(res.content, 'html.parser')
    for h4 in soup.find_all("h4"):
        for contact in data:
            if contact['name'].strip() == h4.text.strip():
                contact['title'] = h4.find_next_sibling('span').text.strip()

    print("Downloading images")
    for i, rep in enumerate(data):
        print(f"\t{i}/{len(data)}")
        link = rep.get("page_link")
        if not link:
            continue

        base = urlparse(link).netloc

        if "gophouse.org" in base:
            res = requests.get(link)
            soup = BeautifulSoup(res.content, 'html.parser')
            try:
                img_url = soup.find("img", class_="w-full").attrs.get("src")
            except AttributeError:
                img_url = get_image_from_other_house_link(rep.get('name'))
                if not img_url:
                    rep['saved_image'] = "no image"
                    continue
            rep['image_url'] = img_url
            fn = rep.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
            _, ext = os.path.splitext(img_url)
            destination = Path(f"michigan/house/{fn}{ext}")
            if not destination.is_file():
                download_image("house", img_url, fn, extension=ext)
            rep["saved_image"] = destination

        elif base == "housedems.com":
            res = requests.get(link)
            # this might have redirected
            new_url = res.request.url
            if "hootsuite" in new_url:
                url = try_other_house_link(rep.get("name"))
                res = requests.get(url)
                new_url = res.request.url
            about_page = new_url + "about"
            res = requests.get(about_page)

            if res.request.url == 'https://housedems.com/about/':
                # they're not at "about"
                soup = BeautifulSoup(requests.get(new_url).content, 'html.parser')
                for a in soup.select("li a"):
                    if "Meet" in a.text:
                        break
                else:
                    rep['saved_image'] = "Couldn't find image"
                    rep['image_url'] = "Couldn't find image"
                    continue
                res = requests.get(a.attrs.get("href"))
            soup = BeautifulSoup(res.content, 'html.parser')
            try:
                img_url = soup.find("a", text="Download Official Portrait").attrs.get("href")
            except AttributeError:
                rep["saved_image"] = "post content not found"
                continue
            if not img_url:
                rep['saved_image'] = "x"
                rep['image_url'] = "x"
                continue
            rep['image_url'] = img_url
            fn = rep.get("name").replace(' ', '-').replace('.', '').replace(',', '').lower()
            destination = Path(f"michigan/house/{fn}.jpg")
            if not destination.is_file():
                download_image("house", img_url, fn)
            rep["saved_image"] = destination

            # check for title
            check = soup.find(class_="fusion-button-wrapper").nextSibling
            if "Committees" in check.text:
                continue
            rep["title"] = check.text.strip()

        else:
            rep['saved_image'] = "None"
            rep['image_url'] = "None"

    write_header = not os.path.isfile("michigan.csv")
    with open("michigan.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=CONTACT.keys())
        if write_header:
            writer.writeheader()  # don't write row if this is after senate
        writer.writerows(data)

def run_michigan():
    scrape_michigan_senators()
    scrape_michigan_house()

if __name__ == '__main__':
    run_michigan()
