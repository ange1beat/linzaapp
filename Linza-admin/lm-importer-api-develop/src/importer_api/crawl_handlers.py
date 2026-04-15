import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from importer_api.handlers import BaseHandler
import requests
from bs4 import BeautifulSoup
from shared import get_logger
from urllib.parse import urlparse, urlsplit, urlunsplit
import uuid
from config import Config
import re
from tornado.escape import json_decode
from importer_api.schemas import GetWEBLinksSchema, GetParseResultSchema
from lxml.html.clean import Cleaner
import json
from requests_html import HTMLSession, HTML
from random import shuffle


logger = get_logger()


class GetParseResultsHandler(BaseHandler):
    """get parse results for visual mapper"""

    SUPPORTED_METHODS = ["POST", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def clean_content(self, content):
        if content:
            cleaner = Cleaner()
            cleaner.scripts = True
            # cleaner.links = True
            cleaner.javascript = True
            cleaner.embedded = True
            cleaner.forms = True
            # cleaner.style = True
            # cleaner.allow_tags = []
            cleaner.remove_unknown_tags = False
            cleaner.remove_tags = ['p', 'div', 'br', 'b']
            new_content = cleaner.clean_html(content)
            new_content = new_content.replace("\n", "").replace("\t", "").replace("\r", "")
            new_content = re.sub(r"<[^>]*>", "", new_content)
            return new_content
        else:
            return None

    def get_content(self, url):
        """go to url and get content"""
        logger.info("loading {}".format(url))
        response = None
        session = HTMLSession()
        try:
            response = session.get(url=url, verify=False)
        except Exception as e:
            logger.error("Error getting {}: {}".format(url, e))
        if response:
            if response.status_code == 200:
                logger.info("Response length: {}".format(len(response.text)))
                return response
            else:
                logger.error("Request returned {}, {}".format(response.status_code, response.reason))
                return b""
        else:
            logger.error("No response: {}".format(url))

    def validate_request_body(self, data):
        d = dict()
        payload_schema = GetParseResultSchema()
        payload, errors = payload_schema.load(data)
        if len(errors) == 0:
            d["payload"] = payload
        else:
            d["errors"] = errors
        return d

    def parse_field(self, field: str, response, mapping: dict):
        data = None
        if field in mapping:
            query = mapping[field]["area"][0]["query"]
            if isinstance(response.html, str):
                r_html = HTML(html=response.html)
                elem = r_html.xpath(query, first=True)
            else:
                elem = response.html.xpath(query, first=True)
            if elem:
                if field == "publishedDateTime":
                    if hasattr(elem, "attrs"):
                        if "time" in elem.attrs:
                            data = elem.attrs["time"]
                        else:
                            data = elem.text
                    else:
                        if isinstance(elem, str):
                            data = elem
                        else:
                            data = elem.text
                else:
                    if isinstance(elem, str):
                        data = elem
                    elif elem.base_url.startswith('https://www.1tv.ru/'):
                        data = elem.text.encode('latin1').decode('utf-8')
                    else:
                        data = elem.text
        return data

    def parse(self, response, mapping):
        """parsing content of every item(article) according to mapping"""
        parsed = dict()
        logger.debug("mapping: {}".format(mapping))
        for key, value in mapping.items():
            parsed[key] = self.clean_content(self.parse_field(field=key, response=response, mapping=mapping))
        return parsed

    def post(self):
        """Get parse results for visual mapper.
        ---
        description: Get parse results for visual mapper.
        parameters:
        -   name: url
            in: body
            description: url
            required: true
        -   name: mapping
            in: body
            description: mapping
            required: true           
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        parseResult:
                            type: string
                            description: parseResult                       
        """
        body = {}
        try:
            body = json_decode(self.request.body)
        except Exception as e:
            logger.error("Error getting request body: ", e)
            self.set_status(400)
            response = {"statusCode": 400, "description": "Error getting POST request body: {}".format(e),
                        "errorCode": None}
            response = {"response": response}
            self.write(response)
        if body:
            payload = self.validate_request_body(data=body)
            if "payload" in payload:
                response = self.get_content(payload["payload"]["url"])
                if response:
                    parsed_dict = self.parse(response, payload["payload"]["mapping"])
                    self.set_status(200)
                    self.write(parsed_dict)
            if "errors" in payload:
                self.set_status(400)
                self.write(payload["errors"])


class GetWEBLinksHandler(BaseHandler):
    """Input:
            Web url
        Output:
            array of urls found in monitoring_area"""
    SUPPORTED_METHODS = ["POST", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def response_encoder(self, response):
        response.encoding = "utf-8"
        return bytes(response.text, 'utf-8')

    def make_full_url(self, start_url, url: str)->str:
        """Often links are relative, make them absolute"""
        if all([not url.startswith("http"), not url.startswith("mailto")]):
            logger.debug("Making full url for {}".format(url))
            result = urlparse(start_url)
            schema = result.scheme
            domain = result.netloc
            tuple_ = (schema, domain, url, '', '')
            return urlunsplit(tuple_)
        else:
            return url

    def load_url(self, url):
        """load the web page itself"""
        logger.info("requesting WEB monitoring_area to find links{}".format(url))
        response = None
        session = HTMLSession()
        try:
            response = session.get(url=url, verify=False)
        except Exception as e:
            logger.error("Error getting {}: {}".format(url, e))
        if response.status_code == 200:
            return response
        else:
            logger.error("Request returned {}".format(response.status_code))
            return None

    def validate_request_body(self, data):
        d = dict()
        payload_schema = GetWEBLinksSchema()
        payload, errors = payload_schema.load(data)
        if len(errors) == 0:
            d["payload"] = payload
        else:
            d["errors"] = errors
        return d

    def filter_links(self, links, regexps, limit):
        results = []
        for link in links:
            for regex in regexps:
                link = re.match(regex, link)
                if link:
                    link = link.string
            if link:
                results.append(link)
        return results[:limit]

    def get_links_from_response(self, response, monitoring_area):
        logger.debug("Monitoring_area is: {}".format(monitoring_area))
        area = response.html.xpath(monitoring_area["area"][0]["query"], first=True)
        return area.absolute_links

    def post(self):
        """Get urls found in monitoring_area.
        ---
        description: Get urls found in monitoring_area.
        parameters:
        -   name: payload
            in: path
            description: url
            required: true
            type: object
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                       links:
                            type: list
                            description: links                        
        """
        body = {}
        try:
            body = json_decode(self.request.body)
        except Exception as e:
            logger.error("Error getting request body: ", e)
            self.set_status(400)
            response = {"statusCode": 400, "description": "Error getting POST request body: {}".format(e),
                        "errorCode": None}
            response = {"response": response}
            self.write(response)
        if body:
            payload = self.validate_request_body(body)
            if "payload" in payload:
                response = self.load_url(payload["payload"]["url"])
                if response:
                    links = self.get_links_from_response(response=response,
                                                         monitoring_area=payload["payload"]["monitoring_area"],
                                                         )

                    if len(links) > 0:
                        if len(payload["payload"]["monitoring_area"]["links_filter"]) > 0:
                            links = self.filter_links(links=links,
                                                      regexps=payload["payload"]["monitoring_area"]["links_filter"],
                                                      limit=500)
                        links = list(links)
                        shuffle(links)
                        self.set_status(200)
                        self.write(json.dumps(links))
            else:
                logger.error("Errors in POST body: {}".format(payload["errors"]))
                self.set_status(400)
                self.write("Errors in POST body: {}".format(payload["errors"]))


class GetRSSLinksHandler(BaseHandler):
    """Input:
            RSS url
            Page (optional, default=1)
            PageSize (optional, default=10)
        Output:
            array of urls found in rss"""
    SUPPORTED_METHODS = ["GET", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def clean_link(self, link):
        """links need cleanup sometimes"""
        link = link.replace(" ", "")
        return link

    def load_feed(self, url):
        """load the feed itself to find title, pubDate and link"""
        logger.info("requesting rss at {}".format(url))
        response = None
        try:
            response = requests.get(url=url, headers=self.HEADERS, verify=False)
        except Exception as e:
            logger.error("Error getting {}: {}".format(url, e))
        if response.status_code == 200:
            return response.content
        else:
            logger.error("Request returned {}".format(response.status_code))
            return None

    def get_xml_data(self, response)->list:
        """Looking for links in rss feed"""
        soup = BeautifulSoup(response.decode('utf-8', 'ignore'), "xml")
        data = []

        items = soup.find_all('item')
        for item in items:
            l = item.find('link').text
            data.append(l)
            logger.debug("Found link in RSS feed {}".format(l))
        logger.info("Found {} links in RsS feed".format(len(data)))
        return data

    def paginate(self, links, page, pageSize):
        """return paginated result"""
        a = [links[i:i+pageSize] for i in range(0, len(links), pageSize)]
        return a[page-1]

    def get(self):
        """Get RSS links.
        ---
        description: Get RSS links.
        parameters:
        -   name: url
            in: path
            description: url
            required: true
            type: string
        -   name: pageSize
            in: path
            description: pageSize
            required: false
            type: int
        -   name: page
            in: path
            description: page
            required: false
            type: int
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        statusCode:
                            type: int
                            description: statusCode
                        data:
                            type: object
                            description: metadata
                            properties:
                                page:
                                    type: int
                                    description: page
                                pageSize:
                                    type: int
                                    description: pageSize
                                count:
                                    type: int
                                    description: count
                                links:
                                    type: list
                                    description: links
        """
        rss_url = self.get_argument("url", None)
        if rss_url:
            logger.debug("received rss url = {}".format(rss_url))
            pageSize_str = self.get_argument("pageSize", default=10)
            page_str = self.get_argument("page", default=1)
            pageSize= int(pageSize_str)
            page = int(page_str)
            rss_content = self.load_feed(rss_url)
            if rss_content:
                links = self.get_xml_data(rss_content)
                links_paginated = self.paginate(links, page=page, pageSize=pageSize)
                self.set_status(200)
                self.write({"statusCode": 200, "data": {"page": page,
                                                       "pageSize": pageSize,
                                                       "count": len(links),
                                                       "links": links_paginated}})
            else:
                self.set_status(404)
                self.write([])
        else:
            logger.error("No rss url provided")
            self.set_status(400)
            response = {"statusCode": 400, "description": "Bad request. No RSS url provided"}
            self.write(response)


class DiscoverHandler(BaseHandler):

    SUPPORTED_METHODS = ["GET", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.set_status(204)
        self.finish()

    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    DataSourceTypes = Config.TYPES

    def get_content(self, url):
        """go to url and get content"""
        logger.info("loading {}".format(url))
        response = None
        session = HTMLSession()
        try:
            response = session.get(url=url, verify=False)
        except Exception as e:
            logger.error("Error getting {}: {}".format(url, e))
        if response:
            if response.status_code == 200:
                logger.info("Response length: {}".format(len(response.text)))
                return response.content
            else:
                logger.error("Request returned {}, {}".format(response.status_code, response.reason))
                return b""
        else:
            logger.error("No response: {}".format(url))

    def define_type(self, uri):
        """
        Find out DatSourceType
        :return: {"type": type, "text": response.text} or {"error": {"code":", message}"}
        """
        response = self.get_content(uri)
        if response:
            soup = BeautifulSoup(response.decode('utf-8', 'ignore'), "lxml")
            if soup.find("rss", version=re.compile(".*", re.I)) is not None:
                return {"type": "rss",  "text": response}
            elif soup.find("feed", xmlns=re.compile("Atom", re.I)) is not None:
                return {"type": "atom", "text": response}
            else:
                # web_soup = BeautifulSoup(response.text, 'html.parser')
                parse_result = urlparse(uri)
                if any(name in parse_result.netloc for name in ("vk.com", "vkontakte.ru")):
                    return {"type": "socialnetworks/vk", "text": response}
                elif any(name in parse_result.netloc for name in ("fb.com", "facebook.com")):
                    return {"type": "socialnetworks/facebook", "text": response}
                elif any(name in parse_result.netloc for name in ("odnoklassniki.ru", "ok.ru")):
                    return {"type": "socialnetworks/odnoklassniki", "text": response}
                elif any(name in parse_result.netloc for name in ("t.me", "telegram.org")):
                    return {"type": "messengers/telegram", "text": response}
                elif any(name in parse_result.netloc for name in ("twitter.com", "t.co")):
                    return {"type": "socialnetworks/twitter", "text": response}
                elif "instagram.com" in parse_result.netloc:
                    return {"type": "socialnetworks/instagram", "text": response}
                elif "youtube.com" in parse_result.netloc:
                    return {"type": "socialnetworks/youtube", "text": response}
                elif "livejournal.com" in parse_result.netloc:
                    return {"type": "socialnetworks/livejournal", "text": response}
                else:
                    return {"type": "web", "text": response}
        else:
            return {"error": "could not get content"}

    def get_meta(self, uri):
        """
        getting meta information from URI
        :return: {"title": title, "description": description, "iconUri": iconUri}
        """
        title = ""
        iconUri = ""
        description = ""
        links = []
        def_type = self.define_type(uri)
        if "error" in def_type:
            return def_type
        else:
            if any([def_type["type"] == "web",
                    def_type["type"].startswith("social"),
                    def_type["type"].startswith("messenger")]):
                if def_type["type"] == "socialnetworks/vk":
                    web_soup = BeautifulSoup(def_type["text"].decode('cp1251', 'ignore'), 'html.parser')
                else:
                    web_soup = BeautifulSoup(def_type["text"].decode('utf-8', 'ignore'), 'html.parser')
                if web_soup.title:
                    title = web_soup.title.string
                desc = web_soup.find_all(attrs={"name": re.compile("Description", re.I)})
                if len(desc) > 0:
                    description = desc[0]["content"]
                icon = web_soup.find("link", rel=re.compile(".*?icon", re.I))
                if icon:
                    iconUri = icon['href']
                    parse_uri = urlparse(uri)
                    parse_icon = urlparse(iconUri)
                    # logger.info("ICON: ", parse_icon)
                    if parse_icon.scheme.startswith("http"):
                        iconUri = iconUri
                    elif iconUri.startswith("//"):
                        iconUri = "http:" + iconUri
                    else:
                        tuple_ = (parse_uri.scheme, parse_uri.netloc, parse_icon.path, "", "")
                        iconUri = urlunsplit(tuple_)
            if def_type["type"] == "rss":
                rss_soup = BeautifulSoup(def_type["text"].decode('utf-8', 'ignore'), 'xml')
                if rss_soup.channel.title:
                    title = rss_soup.channel.title.string
                if rss_soup.channel.description:
                    description = rss_soup.channel.description.string
                if rss_soup.channel.image:
                    iconUri = rss_soup.channel.image.url.string
                try:
                    items = rss_soup.find_all('item')[:10]
                    for item in items:
                        link = item.find('link').text
                        links.append(link)
                except Exception as e:
                    logger.error("Can't find links in RSS feed: {}".format(e))

            if def_type["type"] == "atom":
                atom_soup = BeautifulSoup(def_type["text"], 'lxml')
                if atom_soup.title:
                    title = atom_soup.title.string
            return {"title": title, "description": description, "iconUri": iconUri, "type": def_type["type"],
                    "links": links}

    def get(self):
        """Go to url and get content.
        ---
        description: Go to url and get content.
        parameters:
        -   name: uri
            in: path
            description: uri
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: id
                        name:
                            type: name
                            description: description
                        metadata:
                            type: object
                            description: metadata
                            properties:
                                title:
                                    type: string
                                    description: title
                                description:
                                    type: string
                                    description: description
                                iconUri:
                                    type: string
                                    description: iconUri
                                links:
                                    type: list
                                    description: links
        """
        uri = self.get_argument("uri", None)
        logger.debug("New /discover request: {}".format(uri))
        if uri:
            meta = self.get_meta(uri)
            if "error" in meta:
                self.set_status(400)
                self.write(meta)
                return
            discoverresult = {
                "id": str(uuid.uuid4()),
                "name": meta["type"],
                "metadata": {
                    "title": meta["title"],
                    "description": meta["description"],
                    "iconUri": meta["iconUri"],
                    "links": meta["links"]
                }
            }
            self.set_status(200)
            self.write(discoverresult)
        else:
            self.set_status(400)
            response = {"statusCode": 400, "description": "Bad request. No uri provided"}
            self.write(response)
