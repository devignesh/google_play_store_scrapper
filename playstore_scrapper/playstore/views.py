from django.shortcuts import render
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
import json

PLAY_STORE_BASE_URL = "https://play.google.com"
PLAY_STORE_APP_CATEGORY_URL = "https://play.google.com/store/apps/category/"

# Create your views here.

def index(request):
    return render(request,'playstore/home.html')

def search(request):
    category =  request.GET.get('category','')
    # if category == '':
        # return default

    app_data = scrap(category)
    # print(app_data)
    return render(request,'playstore/search.html', {"app_data": app_data})


def scrap(category):
    url = PLAY_STORE_APP_CATEGORY_URL + category.upper()
    body = requests.get(url)
    data = body.text
    soup = BeautifulSoup(data, 'html.parser')

    app_dic = []

    i = 0
    for app in soup.find_all("div", class_="card no-rationale square-cover apps small"):
        app_title = app.find("a", class_="title").text
        app_link = PLAY_STORE_BASE_URL + app.find("a", class_="card-click-target", href=True)['href']
        app_image = app.find("img", class_="cover-image")
        app_rating = app.find("div", class_="tiny-star star-rating-non-editable-container")
        app_data = {
                "title": app_title.strip(),
                "link": app_link,
                "image": "https:"+app_image['src'],
                "rating": app_rating['aria-label'],
            }

        app_details = app_detail_extract(app_link)
        app_data["app_details"] = app_details

        app_dic.append(app_data)
        # i += 1
        # if i == 20:
        #     break

    return app_dic


def app_detail_extract(app_link):
    print(app_link)
    myurl = requests.get(app_link)

    data = myurl.text
    soup = BeautifulSoup(data, 'html.parser')

    appdata = soup.find("div", class_="JNury Ekdcne")
    
    app_details_main_div = appdata.findAll("div", class_="JHTxhe IQ1z0d")[1]
    app_details_inner_div = app_details_main_div.find("div", class_="xyOfqd")
    app_details = app_details_inner_div.findAll("div", class_="hAyfc")

    app_product = appdata.find("a", class_="hrTbp R8zArc", href=True)
    total_rating = appdata.find("div", class_="BHMmbe")
    Rating_people_count = appdata.find("span", class_="AYi5wd TBRnV")
    Update = appdata.find("span", class_="htlgb")
    Installation = app_details[2].find("span", class_="htlgb")
    Version = app_details[3].find("span", class_="htlgb")

    Developer_mail = appdata.find("a", class_="hrTbp KyaTEc")
    Privacy_policy = appdata.find("a", class_="hrTbp", href=True)

    company_info = app_details[len(app_details)-1].find("span", class_="htlgb")
    company_info_divs = company_info.findAll("div")
    Company_site = company_info_divs[0].find("a", class_="hrTbp",href=True)
    company_address = ""
    if len(company_info_divs) >= 5:
        company_address = company_info_divs[4].text

    data = {
        "app_dev_link": app_product['href'],
        "total_rating": total_rating.text,
        "rating_people": Rating_people_count.text,
        "last_updation": Update.text,
        "installation_count": Installation.text,
        "current_version": Version.text,
        "comapny_url": Company_site['href'],
        "feedback_mail": Developer_mail.text,
        "privacy_policy_url": Privacy_policy['href'],
        "company_address": company_address
    }
    return data



