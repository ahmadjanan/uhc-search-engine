from typing import Dict, Tuple
import requests
import json
import concurrent.futures
import requests
import logging
from tqdm import tqdm


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


class ThreadedJsonDownloader:
    '''
    A JsonDownloader which downloads and formats a JSON file from provided URL. 
    '''
    def __init__(self, url, session):
        self.url = url
        self.session = session

    @staticmethod
    def process_name_data(data: Dict) -> Dict:
        '''
        Process and company data from company name point-of-view.

        Parameters
        ----------
        data: Dict
            Dictionary containing company data.

        Returns
        -------
        processed_name_data: Dict
            Company data processed from company name pov.
        '''

        plan_id = data['reporting_structure'][0]['reporting_plans'][0]['plan_id']
        processed_name_data = {
            'plan_name': data['reporting_structure'][0]['reporting_plans'][0]['plan_name'],
            'plan_id': plan_id,
            'urls': [],
        }
        
        for file_url in data['reporting_structure'][0]['in_network_files']:
            processed_name_data['urls'].append(file_url['location'])
        
        return processed_name_data
    
    @staticmethod
    def process_ein_data(data: Dict) -> Dict:
        '''
        Process and company data from company EIN point-of-view.

        Parameters
        ----------
        data: Dict
            Dictionary containing company data.

        Returns
        -------
        processed_name_data: Dict
            Company data processed from company EIN pov.
        '''

        return {
            'plan_name': data['plan_name'],
            'plan_id': data.pop('plan_id'),
            'urls': data['urls']
        }
        
    def process_data(self, data: Dict) -> Tuple:
        '''
        Process and company data from company both EIN and Name point-of-view.

        Parameters
        ----------
        data: Dict
            Dictionary containing company data.

        Returns
        -------
        processed_name_data: Dict
            Company data processed from company name pov.
        processed_ein_data: Dict
            Company data processed from company EIN pov.
        '''

        processed_name_data = self.process_name_data(data)
        processed_ein_data = self.process_ein_data(processed_name_data)

        return processed_name_data, processed_ein_data

    def download(self) -> Dict:
        '''
        Process and company data from company both EIN and Name point-of-view.

        Returns
        -------
        processed_data: Dict
            Processed and formatted company data.
        '''

        response = self.session.get(self.url)
        fetched_company_data = json.loads(response.content)
        processed_name_data, processed_ein_data = self.process_data(fetched_company_data)
        company_name = fetched_company_data['reporting_entity_name']

        return {
            'name': company_name, 
            'name_data': processed_name_data,
            'ein_data': processed_ein_data,
        }


def populate_name_json(company_name: str, name_data: Dict, name_json_dict: Dict) -> None:
    '''
    Populate central name data database dictionary.

    Parameters
    ----------
    company_name: str
        Dictionary containing company data.
    name_data: Dict
        Dictionary containing company data from name pov.
    name_json_dict: Dict
        Central database dictionary for storing name data.
    '''

    if not name_data['urls']:
        return
        
    if company_name not in name_json_dict:
        name_json_dict[company_name] = [name_data]
    elif name_data not in name_json_dict[company_name]:
        name_json_dict[company_name].append(name_data)


def populate_ein_json(company_name: str, ein_data: Dict, ein_json_dict: Dict) -> None:
    '''
    Populate central EIN data database dictionary.

    Parameters
    ----------
    company_name: str
        Dictionary containing company data.
    name_data: Dict
        Dictionary containing company data from EIN pov.
    ein_json_dict: Dict
        Central database dictionary for storing EIN data.
    '''

    plan_id = ein_data['plan_id']
    if ein_data['urls']:
        ein_json_dict[plan_id] = [{
            'company_name': company_name,
            'plan_name': ein_data['plan_name'],
            'urls': ein_data['urls']
        }]

def main():
    '''
    Main function.
    '''

    with open('company_files.txt') as f:
        urls = f.readlines()
        urls = [url.strip('\n') for url in urls]

    logging.info('Collected JSON files URLs.')
    name_json_dict = {}
    ein_json_dict = {}
    
    with requests.Session() as s:
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=50)
        s.mount('https://', adapter)

        logging.info('Launching concurrent requests to JSON URLs ...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = [executor.submit(ThreadedJsonDownloader(url, s).download) for url in urls]
            for result in tqdm(concurrent.futures.as_completed(results)):
                result = result.result()
                company_name, name_data, ein_data = result['name'], result['name_data'], result['ein_data']
                populate_name_json(company_name, name_data, name_json_dict)
                populate_ein_json(company_name, ein_data, ein_json_dict)

    logging.info('Data downloaded. Writing to Database ...')

    with open('name_db.json', 'w') as f:
        f.write(json.dumps(name_json_dict))

    with open('ein_db.json', 'w') as f:
        f.write(json.dumps(ein_json_dict))
    
    logging.info('Database Created.')


if __name__=='__main__':
    main()
