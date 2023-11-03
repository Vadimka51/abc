import json
from pprint import pprint
import requests
from geopy import distance 
import folium
from flask import Flask


def fetch_coordinates(apikey, address):

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat

def get_user_distance(coffee_shops_with_distance):
    return coffee_shops_with_distance['distance']

def create_coffee_file():
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()

def make_coffee_shops_with_distance(coffee_shops):
    coffee_shops_with_distance = []
    for coffee_shop in coffee_shops:
        coffee_shop_coords  = [coffee_shop['geoData']['coordinates'][1], coffee_shop['geoData']['coordinates'][0]]
        coffee_shop_with_distance = {
            'title'    : coffee_shop['Name'],
            'distance' : distance.distance(user_coords, coffee_shop_coords).km,
            'lantitude': coffee_shop['geoData']['coordinates'][1],
            'longitude': coffee_shop['geoData']['coordinates'][0]
            }  
        coffee_shops_with_distance.append(coffee_shop_with_distance)
    return coffee_shops_with_distance

def make_coffee_marker(map):
    for coffee in nearest_coffee_shops:
        folium.Marker(
        location = [coffee['lantitude'], coffee['longitude']],
        tooltip  = "Click me!",
        popup    = coffee['title'],
        icon     = folium.Icon(icon="cloud"),
        ).add_to(map)
    return map

def make_user_marker(map):
    folium.Marker(
        location = user_coords,
        tooltip  = "Click me!",
        popup    = ['ты тут'],
        icon     = folium.Icon(color="green"),
    ).add_to(map)
    return map


if __name__ == "__main__":

    with open("coffee.json", "r") as my_file:
        file_contents = my_file.read()
    file_contents = json.loads(file_contents)

    user_yandex_geocooder_key = '9ae5ffc6-51c3-4f23-a5e8-bbd275e50f49'  # ваш ключ

    user_place = input('Где вы находитесь? ' )
    user_coords = fetch_coordinates(user_yandex_geocooder_key, user_place)
    user_coords = [user_coords[1], user_coords[0]]

    coffee_shops_with_distance = make_coffee_shops_with_distance(file_contents)
    
    sorted_coffee_shops = sorted(coffee_shops_with_distance, key = get_user_distance )
    nearest_coffee_shops = sorted_coffee_shops[0:10]

    map = folium.Map(location = user_coords )

    map = make_user_marker(map)
    map = make_coffee_marker(map)

    map.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'hello',create_coffee_file)
    app.run('0.0.0.0')