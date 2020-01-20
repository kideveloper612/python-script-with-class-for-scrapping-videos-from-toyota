import requests
import json
import os
import csv
import re
from bs4 import BeautifulSoup

modelYearListJson = {
    "safety_features": "All",
    "entune_3.0": "All",
    "entune": "All",
    "toyota_for_good": "All",
    "toyota_technology": "All",
    "toyota_tv": "All",
    "4runner": "4Runner",
	"86": "86",
	"avalon": "Avalon",
	"avalon_hv": "Avalon Hybrid",
	"c-hr": "C-HR",
	"camry": "Camry",
	"camry_hv": "Camry Hybrid",
	"celica": "Celica",
	"corolla": "Corolla",
	"corolla_hv": "Corolla Hybrid",
	"corolla_hatchback": "Corolla Hatchback",
	"corolla_im": "Corolla iM",
	"corona": "Corona",
	"cressida": "Cressida",
	"echo": "Echo",
	"fj_cruiser": "FJ Cruiser",
	"highlander": "Highlander",
	"highlander_hv": "Highlander Hybrid",
	"land_cruiser": "Land Cruiser",
	"mr2": "MR2",
	"mr2_spyder": "MR2 Spyder",
	"matrix": "Matrix",
	"mirai": "Mirai",
	"paseo": "Paseo",
	"previa": "Previa",
	"prius": "Prius",
	"prius_c": "Prius c",
	"prius_phv": "Prius Plug-in Hybrid",
	"prius_prime": "Prius Prime",
	"prius_v": "Prius v",
	"rav4": "RAV4",
	"rav4_ev": "RAV4 EV",
	"rav4_hv": "RAV4 Hybrid",
	"sequoia": "Sequoia",
	"sienna": "Sienna",
	"solara": "Solara",
	"starlet": "Starlet",
	"supra": "Supra",
	"t100": "T100",
	"tacoma": "Tacoma",
	"tercel": "Tercel",
	"truck": "Truck",
	"tundra": "Tundra",
	"van": "Van",
	"venza": "Venza",
	"yaris": "Yaris",
	"yaris_hatchback": "Yaris Hatchback",
	"yaris_liftback": "Yaris Liftback",
	"yaris_ia": "Yaris iA",
	"fr-s": "FR-S",
	"ia": "iA",
	"im": "iM",
	"iq": "iQ",
	"iq_ev": "iQ EV",
	"tc": "tC",
	"xa": "xA",
	"xb": "xB",
	"xd": "xD"
}
all_section_list = [
    'All Videos',
    'Audio System',
    'Basic Operations',
    'Climate Control System',
    'Entune™',
    'Entune',
    'Headlights',
    'Hybrid Systems',
    'Instrument Cluster',
    'Interior Features',
    'Keys',
    'Mobile Apps',
    'Overview',
    'Safety Features',
    'Seating',
    'Steering Wheel',
    'Suspension',
    'Technology',
    'Traction Features',
    '4WD Features',
    'Exterior Features',
    'Features']
class toyota_video:
    def __init__(self, filename):
        self.csv_header = [['PUBLISHED', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'THUMBNAIL_URL', 'VIDEO_URL']]
        self.results = []
        self.make = 'Toyota'
        self.all_model = 'All'
        self.all_year = 'Year'
        self.filename = filename
        self.section_list = []
        self.section = ''

    def write_direct_csv(self, lines, filename):
        with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def get_landing_videos(self, URL):
        res = requests.get(url=URL)
        if res.status_code == 404:
            return
        res = res.text
        try:
            curly_start_index = res.find('{')
            curly_last_index = res.rfind('}')
            return json.loads(res[curly_start_index:curly_last_index+1])['feed']['entry']
        except:
            curly_start_index = res.find('{')
            curly_last_index = res.rfind('}')
            print(res[curly_start_index:curly_last_index+1])
            exit(-1)

    def get_section_list_for_each_sub_url(self, section_key, year):
        URL = 'https://www.toyota.com/owners/resources/how-to-videos/%s/%s' % (section_key, year)
        res = requests.get(url=URL).content
        soup = BeautifulSoup(res, 'html.parser')
        select = soup.select('select[id="model-nav"]')[0]
        options = select.find_all('option')
        section_list = []
        for option in options:
            section_list.append(option.text)
        return section_list

    def video_list_for_landing_page(self, sub_url, filename):
        URL = "https://www.toyota.com/toyota-owners-theme/json/how-to-videos/youtube/%s.1578285524030.json" % sub_url
        video_list = self.get_landing_videos(URL=URL)
        if video_list is None:
            return
        sub_url_list = sub_url.split("_", 1)
        try:
            int(sub_url_list[0])
            year = sub_url_list[0]
            model_key = sub_url_list[1]
            model = modelYearListJson.get(model_key)
            self.section_list = self.get_section_list_for_each_sub_url(section_key=model_key, year=year)
        except:
            if '.' in sub_url_list[0]:
                year = sub_url_list[0]
                model_key = sub_url_list[1]
                model = modelYearListJson.get(model_key)
                self.section_list = self.get_section_list_for_each_sub_url(section_key=model_key, year=year)
            else:
                year = ''
                model = self.all_model
                self.section = sub_url
        for video in video_list:
            if not year:
                year = video['published']['$t'].split("T")[0]
            sections = video['category']
            for section in sections:
                if section['term'] in self.section_list:
                    self.section = section['term']
            title = video['title']['$t']
            description = video['media$group']['media$description']['$t']
            video_url = video['link'][0]['href']
            thumbnail_url = video['media$group']['media$thumbnail'][0]['url']

            line = [[year, self.make, model, self.section, title, description, thumbnail_url, video_url]]
            print(line)
            self.write_csv(lines=line, filename=filename)

    def get_year_model_suburl_list(self):
        year_model_list_url = "https://www.toyota.com/toyota-owners-theme/json/how-to-videos/how-to-videos-modelyear-list.1578285524030.json"
        res = requests.get(url=year_model_list_url).text
        rep = {"modelYearListJson = [": "", "];": ""}
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))
        array = pattern.sub(lambda m: rep[re.escape(m.group(0))], res).split(',')
        list_remove = list(map(str.strip, array))
        year_model_list = [sub[1:-1] for sub in list_remove]
        return year_model_list

    def loop_request_urls(self):
        sub_urls = self.get_year_model_suburl_list()
        for sub_url in sub_urls:
            URL = "https://www.toyota.com/toyota-owners-theme/json/how-to-videos/youtube/%s.1578285524030.json" % sub_url
            print('Start to work on: %s' % URL)
            sub_url_request = self.video_list_for_landing_page(sub_url=sub_url, filename=self.filename)
            if sub_url_request is None:
                continue
            print('The End: %s' % URL)

print('==========================Start script============================')
filename = 'Toyota_how_to_videos.csv'
toyota_video = toyota_video(filename=filename)
toyota_video.loop_request_urls()
print('=========================The End Script===========================')

