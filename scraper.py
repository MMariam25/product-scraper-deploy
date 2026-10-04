import requests


class Scraper:
    def __init__(self, product, url):
        while url.endswith('/'):
            url = url[:-1]
        self.url = url
        self.product = product
        self.results = []

    def fix_url(self, url):
        if url.startswith("http:") or url.startswith("https:"):
            return url
        while url.startswith('/'):
            url = url[1:]
        return self.url + '/' + url

    def unpack(self, url, olddata=None, entry=0):
        if olddata is None:
            olddata = {}
        try:
            req = requests.get(url, timeout=15)
            req.encoding = 'utf-8'
            text = req.text
            text = text[text.index('<div class="home_ul_img">'):]
            products = text.split('\n                                        <')
            products = products[1:]
            for product in products:
                if entry == 0:
                    olddata = {}
                data = {}
                if '<div class="' in product and '<a title="' in product:
                    key = '<a title="'
                    product = product[product.index(key) + len(key):]
                    key = '" href="'
                    keyname = 'title-' + str(entry)
                    if keyname == 'title-0':
                        keyname = 'category'
                    data[keyname] = product.split(key)[0]
                    product = product[product.index(key) + len(key):]
                    data['href-' + str(entry)] = self.fix_url(product.split('">')[0])
                    key = '" data-original="'
                    product = product[product.index(key) + len(key):]
                    key = '" class="'
                    keyname = 'image-' + str(entry)
                    if keyname == 'image-0':
                        keyname = 'category-image'
                    data[keyname] = self.fix_url(product.split(key)[0])
                    for k, v in data.items():
                        olddata[k] = v
                    data = dict(olddata)
                    if entry < 2:
                        self.unpack(data['href-' + str(entry)], dict(olddata), entry + 1)
                    else:
                        req2 = requests.get(data['href-' + str(entry)], timeout=15)
                        req2.encoding = 'utf-8'
                        self.extract(req2.text, dict(data))
        except Exception:
            pass

    def extract(self, text, data=None):
        if data is None:
            data = {}
        try:
            comment = text.split('<!--  <ul>')[1].split('</ul>')[0].strip()
        except Exception:
            return
        for line in comment.split('</li>'):
            line = line.strip()
            if '<a href="' in line:
                href = line[line.index('<a href="') + 9:].split('" target="_blank">')[0]
                data['image'] = self.fix_url(href)
                continue
            if not line.startswith('<li>'):
                continue
            line = line[4:]
            key = line
            for sep in [' ', ':', '：']:
                key = key.split(sep)[0]
            value = line[len(key):]
            for sep in [' ', ':', '：']:
                if sep in value:
                    value = value[value.index(sep) + len(sep):]
            data[key] = value
        self.results.append(dict(data))

    def run(self):
        self.results = []
        self.unpack(self.url)
        return self.results
