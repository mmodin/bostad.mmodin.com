import requests
import pandas as pd
import datetime
from collections import MutableMapping
from numpy import nan
from bs4 import BeautifulSoup


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = '{0}{1}{2}'.format(parent_key, sep, k) if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, list(map(flatten, v))))
        else:
            items.append((new_key, v))
    return dict(items)


def flatten_municipality(area_list):
    tmp = []
    for d in area_list:
        for l in d['Stadsdelar']:
            tmp.append({'municipality': d['Kommun'], 'district': l})

    return tmp


def extract_queue(html):
    soup = BeautifulSoup(html, 'html.parser')
    property = soup.find(class_='col40').find(class_='egenskap')
    if property is None:
        queue = nan
    else:
        queue = property.find(class_='v').get_text().replace(' av ', '/')
    return queue


def download_html(session, id, relevant):
    q = nan
    if relevant is True:
        url = 'https://bostad.stockholm.se/Lista/Details/?aid=%s' % id
        response = session.get(url)
        if response.status_code == 200:
            q = extract_queue(response.text)
            print('Downloaded queue(%s) for id: %s' % (q, id))
    return q


class BF:
    """ Class to get all apartment listings from Stockholms Bostadsformedling """

    def __init__(self, username, password, login=False, detail=False):
        from bf_data import column_names, fields, municipalities, types, districts
        self.url = 'https://bostad.stockholm.se'
        self.column_names = column_names
        self.fields = fields
        self.municipalities = municipalities
        self.types = types
        self.districts = districts
        self.login = login
        self.session = requests.Session()
        self.detail = detail

        if self.login:
            response = self.session.get(self.url + '/Minasidor/login/')
            #logger.info('Getting login cookie...status code: %s' % response.status_code)
            url = 'https://login001.stockholm.se/siteminderagent/forms/login.fcc'
            data = {
                'target': '-SM-https://bostad.stockholm.se/secure/login',
                'smauthreason': '0',
                'smagentname': 'bostad.stockholm.se',
                'USER': username,
                'PASSWORD': password
            }
            response = self.session.post(url, data=data)
            if response.status_code == 200:
                pass
                #logger.info('Successfully logged in...')
            else:
                #logger.error('Failed logging in with status code: %s' % response.status_code)
                raise Exception('Login error')

        response = self.session.get(self.url + '/Lista/AllaAnnonser')
        if response.status_code == 200:
            data = response.json()
            self.all_listings = pd.DataFrame([flatten(d) for d in data])
            self.swedish_column_names = self.all_listings.columns
            self.all_listings.columns = column_names
            #logger.info('Successfully downloaded %s listings...' % self.all_listings.shape[0])
            self.all_listings['fromDate'] = self.all_listings.fromDate.astype('datetime64[ns]')
            self.all_listings['toDate'] = self.all_listings.toDate.astype('datetime64[ns]')
            self.all_listings['relevant'] = self.all_listings.type.isin(self.types) \
                                            & self.all_listings.district.isin(self.districts) \
                                            & self.all_listings.canApply == self.login
        else:
            raise Exception('Unable to get all listings with status code: %s' % response.status_code)

        if self.login and self.detail:
            n = self.all_listings[self.all_listings.relevant == True].shape[0]
            #logger.info('Getting detailed data for %s listings...' % n)
            self.all_listings['queue'] = self.all_listings.apply(
                lambda row: download_html(self.session, row['id'], row['relevant']),
                axis=1
            )
            n_collected = self.all_listings[self.all_listings.queue.notnull()].shape[0]
            #logger.info('Successfully collected queue data for %s listings' % n_collected)

    def get_relevant_data(self):
        pd.options.display.float_format = '{:,.0f}'.format
        df = self.all_listings
        df.sort_values('fromDate', ascending=False, inplace=True)
        if self.detail:
            fields = self.fields + ['queue']
        else:
            fields = self.fields
        df = df[fields][df.relevant == True]
        return df

