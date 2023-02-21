import requests
import utils
import json
import traceback
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class OpenDataSoftCrawler(interface):
    
    def __init__(self, domain):
        self.domain = domain

    def get_package_list(self):
        """Get all the packages ids"""
        try:
            total_ids = []
            response = requests.get(self.domain + '/api/v2/catalog/datasets?limit=100&lang=es&timezone=UTC')
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', None)
                    
                for p in datasets:
                    id = p['dataset'].get('dataset_id', None)
                    total_ids.append(id)
            return total_ids
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get(self.domain + '/api/v2/catalog/datasets/' + str(id) + '?lang=es&timezone=UTC')
            
            if response.status_code == 200:                
                meta_json = response.json()
                
                metadata = dict()
                
                metadata['identifier'] = id
                
                dataset = meta_json.get('dataset', None)
                
                if dataset is not None:
                    meta = dataset.get('metas', None).get('default', None)
                    metadata['title'] = meta.get('title', None)
                    metadata['description'] = meta.get('description', None)
                    metadata['theme'] = meta.get('theme', None)
                
                    resource_list = []
                    mediaList = []
                    linkList = []
                    aux = dict()

                    res = requests.get(self.domain + '/api/v2/catalog/datasets/' + str(id) + '/exports')
                    if res.status_code == 200:
                        mediaTypes = res.json()
                        mediaTypesLinks = mediaTypes.get('links', None)
                        for m in mediaTypesLinks:
                            if m.get('rel', None) != 'self':
                                mediaList.append(m.get('rel', None))
                                linkList.append(m.get('href', None))
                    
                    aux['downloadUrl'] = linkList
                    aux['mediaType'] = mediaList

                    resource_list.append(aux)

                    metadata['resources'] = resource_list
                    metadata['modified'] = meta.get('modified', None)
                    metadata['license'] = meta.get('license', None)
                    metadata['source'] = self.domain
                # Saving all meta in a json file
                # try:
                #     path = 'C:\\Users\\Usuario\\Desktop\\Crawler2.0\\OpenDataCrawler\\opendatacrawler\\prueba'
                #     with open(path + "/all_" + str(metadata['identifier']) + '.json',
                #             'w', encoding='utf-8') as f:
                #         json.dump(meta_json, f, ensure_ascii=False, indent=4)
                # except Exception as e:
                #     logger.error('Error saving metadata  %s',
                #                 path + "/all_" + metadata['identifier'] + '.json')
                #     logger.error(e)
                # Saving metadata in a json file
                # try:
                #     path = 'C:\\Users\\Usuario\\Desktop\\Crawler2.0\\OpenDataCrawler\\opendatacrawler\\prueba'
                #     with open(path + "/metadata_" + str(metadata['identifier']) + '.json',
                #             'w', encoding='utf-8') as f:
                #         json.dump(metadata, f, ensure_ascii=False, indent=4)
                # except Exception as e:
                #     logger.error('Error saving metadata  %s',
                #                 path + "/metadata_" + metadata['identifier'] + '.json')
                #     logger.error(e)
                return metadata
            else:
                return None
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None