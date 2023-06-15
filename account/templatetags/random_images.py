from django import template

register = template.Library()


@register.simple_tag
def get_random_bing_image():
    from random import choice
    from requests import get

    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8"
    r = get(url)
    BING_URL = "https://www.bing.com"
    bing_images = [f"{BING_URL}{i['url']}" for i in r.json()["images"]]
    iotd = choice(bing_images)
    return iotd
