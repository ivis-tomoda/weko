# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp

"""Module tests."""

from typing_extensions import reveal_type
import pytest
from mock import patch
import uuid
from collections import OrderedDict

from elasticsearch.exceptions import NotFoundError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.errors import MissingModelError
from invenio_records_rest.errors import PIDResolveRESTError
from invenio_records_files.models import RecordsBuckets
from invenio_records_files.api import Record
from invenio_files_rest.models import Bucket, ObjectVersion        
from six import BytesIO
from sqlalchemy.orm.exc import NoResultFound
from weko_admin.models import AdminSettings
from weko_records.api import ItemTypes
from invenio_pidrelations.serializers.utils import serialize_relations
from weko_deposit.api import WekoDeposit, WekoFileObject, WekoIndexer, \
    WekoRecord, _FormatSysBibliographicInformation, _FormatSysCreator
from invenio_accounts.testutils import login_user_via_view,login_user_via_session
from invenio_accounts.models import User
from weko_items_ui.config import WEKO_ITEMS_UI_MS_MIME_TYPE,WEKO_ITEMS_UI_FILE_SISE_PREVIEW_LIMIT

class MockClient():
    def __init__(self):
        self.is_get_error=True
    def update_get_error(self, flg):
        self.is_get_error = flg
    def search(self, index=None, doc_type=None, body=None, scroll=None):
        return None

    def index(self, index=None, doc_type=None, id=None, body=None, version=None, version_type=None):
        return {}

    def get(self, index=None, doc_type=None, id=None, body=None):
        return {"_source": {"authorNameInfo": {},
                            "authorIdInfo": {},
                            "emailInfo": {},
                            "affiliationInfo":{}
                            }
                }

    def update(self, index=None, doc_type=None, id=None, body=None):
        if self.is_get_error:
            raise NotFoundError
        else:
            return None
    def delete(self, index=None, doc_type=None, id=None, routing=None):
        return None
    def exists(self, index=None, doc_type=None, id=None):
        return None

# class WekoFileObject(FileObject):
# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoFileObject -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
class TestWekoFileObject:

    # def __init__(self, obj, data):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoFileObject::test___init__ -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test___init__(self,app,location):
        bucket = Bucket.create()
        key = 'hello.txt'
        stream = BytesIO(b'helloworld')
        obj = ObjectVersion.create(bucket=bucket, key=key, stream=stream)
        with app.test_request_context():
            file = WekoFileObject(obj,{})
            assert type(file)==WekoFileObject
        
    # def info(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoFileObject::test_info -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_info(self,app,location):
        bucket = Bucket.create()
        key = 'hello.txt'
        stream = BytesIO(b'helloworld')
        obj = ObjectVersion.create(bucket=bucket, key=key, stream=stream)
        with app.test_request_context():
            file = WekoFileObject(obj,{})
            assert file.info()['key']==key
    
    #  def file_preview_able(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoFileObject::test_file_preview_able -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_file_preview_able(self,app,location):
        bucket = Bucket.create()
        key = 'hello.txt'
        stream = BytesIO(b'helloworld')
        obj = ObjectVersion.create(bucket=bucket, key=key, stream=stream)
        with app.test_request_context():
            file = WekoFileObject(obj,{})
            assert file.file_preview_able()==True
            app.config["WEKO_ITEMS_UI_MS_MIME_TYPE"] = WEKO_ITEMS_UI_MS_MIME_TYPE
            app.config["WEKO_ITEMS_UI_FILE_SISE_PREVIEW_LIMIT+"] = {'ms_word': 30,'ms_powerpoint': 20,'ms_excel': 10}
            assert file.file_preview_able()==True
            file.data['format'] = 'application/vnd.ms-excel'
            assert file.file_preview_able()==True
            file.data['size'] = 10000000+1
            assert file.file_preview_able()==False

            
    



# class WekoIndexer(RecordIndexer):

# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
class TestWekoIndexer:

    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_get_es_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_es_index(self,app):
        indexer = WekoIndexer()
        assert isinstance(indexer,WekoIndexer)

        # def get_es_index(self):
        with app.test_request_context():
            indexer.get_es_index()
            assert indexer.es_index==app.config['SEARCH_UI_SEARCH_INDEX']
            assert indexer.es_doc_type==app.config['INDEXER_DEFAULT_DOCTYPE']
            assert indexer.file_doc_type=='content'

    #  def upload_metadata(self, jrc, item_id, revision_id, skip_files=False):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_upload_metadata -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_upload_metadata(self,app,es_records):
        indexer, records = es_records
        record_data = records[0]['record_data']
        item_id = records[0]['recid'].id
        revision_id=5
        skip_files=False
        title = 'UPDATE{}'.format(uuid.uuid4())
        record_data['title'] = title
        indexer.upload_metadata(record_data,item_id,revision_id,skip_files)
        ret = indexer.get_metadata_by_item_id(item_id)
        assert ret['_source']['title'] == title


    # def delete_file_index(self, body, parent_id):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_delete_file_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_file_index(self,app,es_records):
        indexer, records = es_records
        record = records[0]['record']
        dep = WekoDeposit(record,record.model)
        indexer.delete_file_index([record.id],record.pid)
        from elasticsearch.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            ret = indexer.get_metadata_by_item_id(record.pid)




    # def update_publish_status(self, record):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_update_publish_status -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_publish_status(self,app,es_records):
        indexer, records = es_records
        record = records[0]['record']
        with app.test_request_context():
            assert indexer.update_publish_status(record)=={'_index': 'test-weko-item-v1.0.0', '_type': 'item-v1.0.0', '_id': '{}'.format(record.id), '_version': 2, 'result': 'noop', '_shards': {'total': 0, 'successful': 0, 'failed': 0}}

    # def update_relation_version_is_last(self, version):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_update_relation_version_is_last -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_relation_version_is_last(self,es_records):
        indexer, records = es_records
        version = records[0]['record']
        pid = records[0]['recid']
        relations = serialize_relations(pid)
        relations_ver = relations['version'][0]
        relations_ver['id'] = pid.object_uuid
        relations_ver['is_last'] = relations_ver.get('index') == 0
        assert indexer.update_relation_version_is_last(relations_ver)=={'_index': 'test-weko-item-v1.0.0', '_type': 'item-v1.0.0', '_id': '{}'.format(pid.object_uuid), '_version': 3, 'result': 'updated', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 9, '_primary_term': 1}

    # def update_path(self, record, update_revision=True,
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_update_path -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_path(self,es_records):
        indexer, records = es_records
        record = records[0]['record']
        assert indexer.update_path(record, update_revision=False,update_oai=False, is_deleted=False)=={'_index': 'test-weko-item-v1.0.0', '_type': 'item-v1.0.0', '_id': '{}'.format(record.id), '_version': 3, 'result': 'updated', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 9, '_primary_term': 1}


    # def index(self, record):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_index(self,es_records):
        indexer, records = es_records
        record = records[0]['record']
        indexer.index(record)


    # def delete(self, record):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_delete -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete(self,es_records):
        indexer, records = es_records
        record = records[0]['record']
        indexer.delete(record)

    #     def delete_by_id(self, uuid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_delete_by_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_by_id(self,es_records):
        indexer, records = es_records
        record = records[0]['record']
        indexer.delete_by_id(record.id)

    # def get_count_by_index_id(self, tree_path):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_get_count_by_index_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_count_by_index_id(self,es_records):
        indexer, records = es_records
        metadata = records[0]['metadata']
        ret = indexer.get_count_by_index_id(1)
        assert ret==4
        ret = indexer.get_count_by_index_id(2)
        assert ret==5

    #     def get_pid_by_es_scroll(self, path):
    #         def get_result(result):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_get_pid_by_es_scroll -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_pid_by_es_scroll(self,es_records):
        indexer, records = es_records
        ret = indexer.get_pid_by_es_scroll(1)
        assert ret is not None

    #     def get_metadata_by_item_id(self, item_id):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_get_metadata_by_item_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_metadata_by_item_id(self,es_records):
        indexer, records = es_records
        record = records[0]['record']
        ret = indexer.get_metadata_by_item_id(record.id)
        assert ret=={'_index': 'test-weko-item-v1.0.0', '_type': 'item-v1.0.0', '_id': '{}'.format(record.id), '_version': 2, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'rightsHolder': {'rightsHolderName': ['Right Holder Name'], 'nameIdentifier': ['xxxxxx']}, 'date': [{'dateType': 'Available', 'value': '2021-06-30'}], 'sourceIdentifier': [{'identifierType': 'ISSN', 'value': 'xxxx-xxxx-xxxx'}], 'subject': [{'value': 'Sibject1', 'subjectScheme': 'Other'}], 'language': ['jpn'], 'type': ['conference paper'], 'relation': {'relatedIdentifier': [{'identifierType': 'arXiv', 'value': 'xxxxx'}], '@attributes': {'relationType': [['isVersionOf']]}, 'relatedTitle': ['Related Title']}, 'path': ['2'], 'fundingReference': {'funderName': ['Funder Name'], 'funderIdentifier': ['http://xxx'], 'awardTitle': ['Award Title'], 'awardNumber': ['Award Number']}, 'apc': ['Unknown'], 'pageStart': ['1'], 'temporal': ['Temporal'], 'identifier': [{'identifierType': 'URI', 'value': 'http://localhost'}], 'issue': ['111'], 'sourceTitle': ['Source Title'], 'degreeName': ['Degree Name'], 'version': ['Version'], 'volume': ['1'], 'versiontype': ['AO'], '_oai': {'sets': ['2'], 'id': 'oai:weko3.example.org:00000001'}, 'publisher': ['Publisher'], 'publish_date': '2021-08-06', '_item_metadata': {'item_1617186499011': {'attribute_name': 'Rights', 'attribute_value_mlt': [{'subitem_1522650727486': 'http://localhost', 'subitem_1522650717957': 'ja', 'subitem_1522651041219': 'Rights Information'}]}, 'item_1617186994930': {'attribute_name': 'Number of Pages', 'attribute_value_mlt': [{'subitem_1551256248092': '12'}]}, 'item_type_id': '1', 'item_1617186476635': {'attribute_name': 'Access Rights', 'attribute_value_mlt': [{'subitem_1600958577026': 'http://purl.org/coar/access_right/c_abf2', 'subitem_1522299639480': 'open access'}]}, 'item_1617186660861': {'attribute_name': 'Date', 'attribute_value_mlt': [{'subitem_1522300722591': '2021-06-30', 'subitem_1522300695726': 'Available'}]}, 'item_1617186385884': {'attribute_name': 'Alternative Title', 'attribute_value_mlt': [{'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'en'}, {'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'ja'}]}, 'title': ['ja_conference paperITEM00000002(public_open_access_open_access_simple)'], 'item_1617187045071': {'attribute_name': 'Page End', 'attribute_value_mlt': [{'subitem_1551256185532': '3'}]}, 'item_1617605131499': {'attribute_name': 'File', 'attribute_type': 'file', 'attribute_value_mlt': [{'date': [{'dateValue': '2021-07-12', 'dateType': 'Available'}], 'accessrole': 'open_access', 'displaytype': 'simple', 'filename': '1KB.pdf', 'format': 'text/plain', 'mimetype': 'application/pdf', 'filesize': [{'value': '1 KB'}], 'version_id': '08725856-0ded-4b39-8231-394a80b297df', 'url': {'url': 'https://localhost:8443/record/1/files/1KB.pdf'}}]}, 'item_1617186419668': {'attribute_name': 'Creator', 'attribute_type': 'creator', 'attribute_value_mlt': [{'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorNames': [{'creatorName': '情報, 太郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'creatorAffiliations': [{'affiliationNames': [{'affiliationName': 'University', 'affiliationNameLang': 'en'}], 'affiliationNameIdentifiers': [{'affiliationNameIdentifierURI': 'http://isni.org/isni/0000000121691048', 'affiliationNameIdentifier': '0000000121691048', 'affiliationNameIdentifierScheme': 'ISNI'}]}], 'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifierScheme': 'WEKO', 'nameIdentifier': '4'}, {'nameIdentifierScheme': 'ORCID', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'CiNii', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'KAKEN2', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifier': 'zzzzzzz'}]}, {'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorNames': [{'creatorName': '情報, 太郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifierScheme': 'ORCID', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'CiNii', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'KAKEN2', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifier': 'zzzzzzz'}]}, {'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorNames': [{'creatorName': '情報, 太郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifierScheme': 'ORCID', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'CiNii', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'KAKEN2', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifier': 'zzzzzzz'}]}]}, 'item_1617351524846': {'attribute_name': 'APC', 'attribute_value_mlt': [{'subitem_1523260933860': 'Unknown'}]}, 'author_link': ['4'], 'path': ['2'], 'item_1617186609386': {'attribute_name': 'Subject', 'attribute_value_mlt': [{'subitem_1522300014469': 'Other', 'subitem_1522299896455': 'ja', 'subitem_1523261968819': 'Sibject1', 'subitem_1522300048512': 'http://localhost/'}]}, 'item_1617186882738': {'attribute_name': 'Geo Location', 'attribute_value_mlt': [{'subitem_geolocation_place': [{'subitem_geolocation_place_text': 'Japan'}]}]}, 'item_1617258105262': {'attribute_name': 'Resource Type', 'attribute_value_mlt': [{'resourceuri': 'http://purl.org/coar/resource_type/c_5794', 'resourcetype': 'conference paper'}]}, 'item_1617620223087': {'attribute_name': 'Heading', 'attribute_value_mlt': [{'subitem_1565671149650': 'ja', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheading'}, {'subitem_1565671149650': 'en', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheding'}]}, 'control_number': '1', 'weko_shared_id': -1, 'relation_version_is_last': True, 'item_1617187024783': {'attribute_name': 'Page Start', 'attribute_value_mlt': [{'subitem_1551256198917': '1'}]}, 'item_1617186702042': {'attribute_name': 'Language', 'attribute_value_mlt': [{'subitem_1551255818386': 'jpn'}]}, 'item_1617186941041': {'attribute_name': 'Source Title', 'attribute_value_mlt': [{'subitem_1522650068558': 'en', 'subitem_1522650091861': 'Source Title'}]}, 'item_title': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'item_1617187136212': {'attribute_name': 'Date Granted', 'attribute_value_mlt': [{'subitem_1551256096004': '2021-06-30'}]}, 'publish_status': '0', 'pubdate': {'attribute_name': 'PubDate', 'attribute_value': '2021-08-06'}, 'item_1617186626617': {'attribute_name': 'Description', 'attribute_value_mlt': [{'subitem_description_type': 'Abstract', 'subitem_description_language': 'en', 'subitem_description': 'Description\nDescription<br/>Description'}, {'subitem_description_type': 'Abstract', 'subitem_description_language': 'ja', 'subitem_description': '概要\n概要\n概要\n概要'}]}, 'item_1617186643794': {'attribute_name': 'Publisher', 'attribute_value_mlt': [{'subitem_1522300316516': 'Publisher', 'subitem_1522300295150': 'en'}]}, 'item_1617186920753': {'attribute_name': 'Source Identifier', 'attribute_value_mlt': [{'subitem_1522646500366': 'ISSN', 'subitem_1522646572813': 'xxxx-xxxx-xxxx'}]}, 'owner': '1', 'item_1617944105607': {'attribute_name': 'Degree Grantor', 'attribute_value_mlt': [{'subitem_1551256037922': [{'subitem_1551256042287': 'Degree Grantor Name', 'subitem_1551256047619': 'en'}], 'subitem_1551256015892': [{'subitem_1551256027296': 'xxxxxx', 'subitem_1551256029891': 'kakenhi'}]}]}, 'item_1617186783814': {'attribute_name': 'Identifier', 'attribute_value_mlt': [{'subitem_identifier_type': 'URI', 'subitem_identifier_uri': 'http://localhost'}]}, 'item_1617349709064': {'attribute_name': 'Contributor', 'attribute_value_mlt': [{'contributorMails': [{'contributorMail': 'wekosoftware@nii.ac.jp'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifierScheme': 'ORCID', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'CiNii', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifier': 'xxxxxxx'}, {'nameIdentifierScheme': 'KAKEN2', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifier': 'xxxxxxx'}], 'contributorType': 'ContactPerson', 'contributorNames': [{'lang': 'ja', 'contributorName': '情報, 太郎'}, {'lang': 'ja-Kana', 'contributorName': 'ジョウホウ, タロウ'}, {'lang': 'en', 'contributorName': 'Joho, Taro'}]}]}, 'item_1617186859717': {'attribute_name': 'Temporal', 'attribute_value_mlt': [{'subitem_1522658031721': 'Temporal', 'subitem_1522658018441': 'en'}]}, 'item_1617187187528': {'attribute_name': 'Conference', 'attribute_value_mlt': [{'subitem_1599711655652': '1', 'subitem_1599711758470': [{'subitem_1599711769260': 'Conference Venue', 'subitem_1599711775943': 'ja'}], 'subitem_1599711699392': {'subitem_1599711743722': '2020', 'subitem_1599711727603': '12', 'subitem_1599711739022': '12', 'subitem_1599711704251': '2020/12/11', 'subitem_1599711735410': '1', 'subitem_1599711731891': '2000', 'subitem_1599711712451': '1', 'subitem_1599711745532': 'ja'}, 'subitem_1599711788485': [{'subitem_1599711798761': 'Conference Place', 'subitem_1599711803382': 'ja'}], 'subitem_1599711813532': 'JPN', 'subitem_1599711660052': [{'subitem_1599711686511': 'ja', 'subitem_1599711680082': 'Sponsor'}], 'subitem_1599711633003': [{'subitem_1599711636923': 'Conference Name', 'subitem_1599711645590': 'ja'}]}]}, 'item_1617186901218': {'attribute_name': 'Funding Reference', 'attribute_value_mlt': [{'subitem_1522399651758': [{'subitem_1522721929892': 'Award Title', 'subitem_1522721910626': 'en'}], 'subitem_1522399143519': {'subitem_1522399281603': 'ISNI', 'subitem_1522399333375': 'http://xxx'}, 'subitem_1522399571623': {'subitem_1522399628911': 'Award Number', 'subitem_1522399585738': 'Award URI'}, 'subitem_1522399412622': [{'subitem_1522737543681': 'Funder Name', 'subitem_1522399416691': 'en'}]}]}, 'item_1617186331708': {'attribute_name': 'Title', 'attribute_value_mlt': [{'subitem_1551255647225': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'subitem_1551255648112': 'ja'}, {'subitem_1551255647225': 'en_conference paperITEM00000002(public_open_access_simple)', 'subitem_1551255648112': 'en'}]}, 'item_1617265215918': {'attribute_name': 'Version Type', 'attribute_value_mlt': [{'subitem_1522305645492': 'AO', 'subitem_1600292170262': 'http://purl.org/coar/version/c_b1a7d7d4d402bcce'}]}, 'item_1617187112279': {'attribute_name': 'Degree Name', 'attribute_value_mlt': [{'subitem_1551256129013': 'en', 'subitem_1551256126428': 'Degree Name'}]}, 'item_1617610673286': {'attribute_name': 'Rights Holder', 'attribute_value_mlt': [{'nameIdentifiers': [{'nameIdentifierScheme': 'ORCID', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifier': 'xxxxxx'}], 'rightHolderNames': [{'rightHolderLanguage': 'ja', 'rightHolderName': 'Right Holder Name'}]}]}, 'item_1617186959569': {'attribute_name': 'Volume Number', 'attribute_value_mlt': [{'subitem_1551256328147': '1'}]}, 'item_1617353299429': {'attribute_name': 'Relation', 'attribute_value_mlt': [{'subitem_1522306287251': {'subitem_1522306382014': 'arXiv', 'subitem_1522306436033': 'xxxxx'}, 'subitem_1523320863692': [{'subitem_1523320867455': 'en', 'subitem_1523320909613': 'Related Title'}], 'subitem_1522306207484': 'isVersionOf'}]}, 'publish_date': '2021-08-06', 'item_1617349808926': {'attribute_name': 'Version', 'attribute_value_mlt': [{'subitem_1523263171732': 'Version'}]}, 'item_1617186981471': {'attribute_name': 'Issue Number', 'attribute_value_mlt': [{'subitem_1551256294723': '111'}]}}, 'conference': {'conferenceName': ['Conference Name'], 'conferenceCountry': ['JPN'], 'conferenceSponsor': ['Sponsor'], 'conferenceVenue': ['Conference Venue'], 'conferenceDate': ['2020/12/11'], 'conferenceSequence': ['1']}, 'description': [{'descriptionType': 'Abstract', 'value': 'Description\nDescription<br/>Description'}, {'descriptionType': 'Abstract', 'value': '概要\n概要\n概要\n概要'}], 'title': ['ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'en_conference paperITEM00000002(public_open_access_simple)'], 'content': [{'date': [{'dateValue': '2021-07-12', 'dateType': 'Available'}], 'accessrole': 'open_access', 'displaytype': 'simple', 'filename': '1KB.pdf', 'attachment': {}, 'format': 'text/plain', 'mimetype': 'application/pdf', 'filesize': [{'value': '1 KB'}], 'version_id': '08725856-0ded-4b39-8231-394a80b297df', 'url': {'url': 'https://localhost:8443/record/1/files/1KB.pdf'}}], 'author_link': ['4'], 'numPages': ['12'], 'degreeGrantor': {'degreeGrantorName': ['Degree Grantor Name'], 'nameIdentifier': ['xxxxxx']}, 'contributor': {'contributorAlternative': [], 'affiliation': {'affiliationName': [], 'nameIdentifier': []}, 'givenName': ['太郎', 'タロウ', 'Taro'], 'familyName': ['情報', 'ジョウホウ', 'Joho'], '@attributes': {'contributorType': [['ContactPerson']]}, 'contributorName': ['情報, 太郎', 'ジョウホウ, タロウ', 'Joho, Taro'], 'nameIdentifier': ['xxxxxxx', 'xxxxxxx', 'xxxxxxx']}, 'file': {'date': [{'dateType': 'fileDate.fileDateType'}], 'extent': ['1 KB'], 'mimeType': ['text/plain'], 'URI': [{'value': 'https://weko3.example.org/record/12/files/1KB.pdf'}], 'version': []}, 'pageEnd': ['3'], 'rights': ['Rights Information'], 'control_number': '1', 'weko_shared_id': -1, 'dateGranted': ['2021-06-30'], 'publish_status': '0', 'creator': {'affiliation': {'affiliationName': ['University'], 'nameIdentifier': ['0000000121691048']}, 'familyName': ['情報', 'ジョウホウ', 'Joho', '情報', 'ジョウホウ', 'Joho', '情報', 'ジョウホウ', 'Joho'], 'givenName': ['太郎', 'タロウ', 'Taro', '太郎', 'タロウ', 'Taro', '太郎', 'タロウ', 'Taro'], 'creatorName': ['情報, 太郎', 'ジョウホウ, タロウ', 'Joho, Taro', '情報, 太郎', 'ジョウホウ, タロウ', 'Joho, Taro', '情報, 太郎', 'ジョウホウ, タロウ', 'Joho, Taro'], 'creatorAlternative': [], 'nameIdentifier': ['4', 'xxxxxxx', 'xxxxxxx', 'zzzzzzz', 'xxxxxxx', 'xxxxxxx', 'zzzzzzz', 'xxxxxxx', 'xxxxxxx', 'zzzzzzz']}, 'weko_creator_id': '1', 'alternative': ['Alternative Title', 'Alternative Title'], '_updated': '2022-09-04T06:56:08.339432+00:00', 'itemtype': 'デフォルトアイテムタイプ（フル）', 'geoLocation': {'geoLocationPlace': ['Japan']}, '_created': '2022-08-27T06:05:51.306953+00:00', 'accessRights': ['open access']}}

    #     def update_feedback_mail_list(self, feedback_mail):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_bulk_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_feedback_mail_list(selft,es_records):
        indexer, records = es_records
        metadata = records[0]['mdataset']

    #     def update_author_link(self, author_link):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_bulk_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp

    #     def update_jpcoar_identifier(self, dc, item_id):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_bulk_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp

    #     def __build_bulk_es_data(self, updated_data):
    #     def bulk_update(self, updated_data):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoIndexer::test_bulk_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_bulk_update(self,es_records):
        indexer, records = es_records
        res = []
        res.append(records[0]['record'])
        res.append(records[1]['record'])
        res.append(records[2]['record'])
        indexer.bulk_update(res)

# class WekoDeposit(Deposit):
# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
class TestWekoDeposit:
    # def item_metadata(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_item_metadata(self,app,es_records):
        indexer, records = es_records
        record = records[0]['record']
        assert False

    # def is_published(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_is_published -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_is_published(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            assert dep.is_published()==False



    # def merge_with_published(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_merge_with_published -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_merge_with_published(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            dep.merge_with_published()
    
    # def _patch(diff_result, destination, in_place=False):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__patch -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__patch(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            diff_result = [('change', '_buckets.deposit', ('753ff0d7-0659-4460-9b1a-fd1ef38467f2', '688f2d41-be61-468f-95e2-a06abefdaf60')), ('change', '_buckets.deposit', ('753ff0d7-0659-4460-9b1a-fd1ef38467f2', '688f2d41-be61-468f-95e2-a06abefdaf60')), ('add', '', [('_oai', {})]), ('add', '', [('_oai', {})]), ('add', '_oai', [('id', 'oai:weko3.example.org:00000013')]), ('add', '_oai', [('id', 'oai:weko3.example.org:00000013')]), ('add', '_oai', [('sets', [])]), ('add', '_oai', [('sets', [])]), ('add', '_oai.sets', [(0, '1661517684078')]), ('add', '_oai.sets', [(0, '1661517684078')]), ('add', '', [('author_link', [])]), ('add', '', [('author_link', [])]), ('add', 'author_link', [(0, '4')]), ('add', 'author_link', [(0, '4')]), ('add', '', [('item_1617186331708', {})]), ('add', '', [('item_1617186331708', {})]), ('add', 'item_1617186331708', [('attribute_name', 'Title')]), ('add', 'item_1617186331708', [('attribute_name', 'Title')]), ('add', 'item_1617186331708', [('attribute_value_mlt', [])]), ('add', 'item_1617186331708', [('attribute_value_mlt', [])]), ('add', 'item_1617186331708.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186331708.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186331708', 'attribute_value_mlt', 0], [('subitem_1551255647225', 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 0], [('subitem_1551255647225', 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 0], [('subitem_1551255648112', 'ja')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 0], [('subitem_1551255648112', 'ja')]), ('add', 'item_1617186331708.attribute_value_mlt', [(1, {})]), ('add', 'item_1617186331708.attribute_value_mlt', [(1, {})]), ('add', ['item_1617186331708', 'attribute_value_mlt', 1], [('subitem_1551255647225', 'en_conference paperITEM00000001(public_open_access_simple)')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 1], [('subitem_1551255647225', 'en_conference paperITEM00000001(public_open_access_simple)')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 1], [('subitem_1551255648112', 'en')]), ('add', ['item_1617186331708', 'attribute_value_mlt', 1], [('subitem_1551255648112', 'en')]), ('add', '', [('item_1617186385884', {})]), ('add', '', [('item_1617186385884', {})]), ('add', 'item_1617186385884', [('attribute_name', 'Alternative Title')]), ('add', 'item_1617186385884', [('attribute_name', 'Alternative Title')]), ('add', 'item_1617186385884', [('attribute_value_mlt', [])]), ('add', 'item_1617186385884', [('attribute_value_mlt', [])]), ('add', 'item_1617186385884.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186385884.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186385884', 'attribute_value_mlt', 0], [('subitem_1551255720400', 'Alternative Title')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 0], [('subitem_1551255720400', 'Alternative Title')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 0], [('subitem_1551255721061', 'en')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 0], [('subitem_1551255721061', 'en')]), ('add', 'item_1617186385884.attribute_value_mlt', [(1, {})]), ('add', 'item_1617186385884.attribute_value_mlt', [(1, {})]), ('add', ['item_1617186385884', 'attribute_value_mlt', 1], [('subitem_1551255720400', 'Alternative Title')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 1], [('subitem_1551255720400', 'Alternative Title')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 1], [('subitem_1551255721061', 'ja')]), ('add', ['item_1617186385884', 'attribute_value_mlt', 1], [('subitem_1551255721061', 'ja')]), ('add', '', [('item_1617186419668', {})]), ('add', '', [('item_1617186419668', {})]), ('add', 'item_1617186419668', [('attribute_name', 'Creator')]), ('add', 'item_1617186419668', [('attribute_name', 'Creator')]), ('add', 'item_1617186419668', [('attribute_type', 'creator')]), ('add', 'item_1617186419668', [('attribute_type', 'creator')]), ('add', 'item_1617186419668', [('attribute_value_mlt', [])]), ('add', 'item_1617186419668', [('attribute_value_mlt', [])]), ('add', 'item_1617186419668.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186419668.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorAffiliations', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorAffiliations', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0], [('affiliationNameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0], [('affiliationNameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifier', '0000000121691048')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifier', '0000000121691048')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifierScheme', 'ISNI')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifierScheme', 'ISNI')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifierURI', 'http://isni.org/isni/0000000121691048')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNameIdentifiers', 0], [('affiliationNameIdentifierURI', 'http://isni.org/isni/0000000121691048')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0], [('affiliationNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0], [('affiliationNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames', 0], [('affiliationName', 'University')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames', 0], [('affiliationName', 'University')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames', 0], [('affiliationNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorAffiliations', 0, 'affiliationNames', 0], [('affiliationNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', '4')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', '4')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'WEKO')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'WEKO')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(3, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(3, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 0, 'nameIdentifiers', 3], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', 'item_1617186419668.attribute_value_mlt', [(1, {})]), ('add', 'item_1617186419668.attribute_value_mlt', [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 1, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', 'item_1617186419668.attribute_value_mlt', [(2, {})]), ('add', 'item_1617186419668.attribute_value_mlt', [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('creatorMails', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorMails'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorMails', 0], [('creatorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('creatorNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 0], [('creatorName', '情報, 太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 0], [('creatorNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 1], [('creatorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 1], [('creatorNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 2], [('creatorName', 'Joho, Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'creatorNames', 2], [('creatorNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('familyNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('givenNames', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2], [('nameIdentifiers', [])]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifier', 'zzzzzzz')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', ['item_1617186419668', 'attribute_value_mlt', 2, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', '', [('item_1617186476635', {})]), ('add', '', [('item_1617186476635', {})]), ('add', 'item_1617186476635', [('attribute_name', 'Access Rights')]), ('add', 'item_1617186476635', [('attribute_name', 'Access Rights')]), ('add', 'item_1617186476635', [('attribute_value_mlt', [])]), ('add', 'item_1617186476635', [('attribute_value_mlt', [])]), ('add', 'item_1617186476635.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186476635.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186476635', 'attribute_value_mlt', 0], [('subitem_1522299639480', 'open access')]), ('add', ['item_1617186476635', 'attribute_value_mlt', 0], [('subitem_1522299639480', 'open access')]), ('add', ['item_1617186476635', 'attribute_value_mlt', 0], [('subitem_1600958577026', 'http://purl.org/coar/access_right/c_abf2')]), ('add', ['item_1617186476635', 'attribute_value_mlt', 0], [('subitem_1600958577026', 'http://purl.org/coar/access_right/c_abf2')]), ('add', '', [('item_1617186499011', {})]), ('add', '', [('item_1617186499011', {})]), ('add', 'item_1617186499011', [('attribute_name', 'Rights')]), ('add', 'item_1617186499011', [('attribute_name', 'Rights')]), ('add', 'item_1617186499011', [('attribute_value_mlt', [])]), ('add', 'item_1617186499011', [('attribute_value_mlt', [])]), ('add', 'item_1617186499011.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186499011.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522650717957', 'ja')]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522650717957', 'ja')]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522650727486', 'http://localhost')]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522650727486', 'http://localhost')]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522651041219', 'Rights Information')]), ('add', ['item_1617186499011', 'attribute_value_mlt', 0], [('subitem_1522651041219', 'Rights Information')]), ('add', '', [('item_1617186609386', {})]), ('add', '', [('item_1617186609386', {})]), ('add', 'item_1617186609386', [('attribute_name', 'Subject')]), ('add', 'item_1617186609386', [('attribute_name', 'Subject')]), ('add', 'item_1617186609386', [('attribute_value_mlt', [])]), ('add', 'item_1617186609386', [('attribute_value_mlt', [])]), ('add', 'item_1617186609386.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186609386.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522299896455', 'ja')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522299896455', 'ja')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522300014469', 'Other')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522300014469', 'Other')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522300048512', 'http://localhost/')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1522300048512', 'http://localhost/')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1523261968819', 'Sibject1')]), ('add', ['item_1617186609386', 'attribute_value_mlt', 0], [('subitem_1523261968819', 'Sibject1')]), ('add', '', [('item_1617186626617', {})]), ('add', '', [('item_1617186626617', {})]), ('add', 'item_1617186626617', [('attribute_name', 'Description')]), ('add', 'item_1617186626617', [('attribute_name', 'Description')]), ('add', 'item_1617186626617', [('attribute_value_mlt', [])]), ('add', 'item_1617186626617', [('attribute_value_mlt', [])]), ('add', 'item_1617186626617.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186626617.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description', 'Description\nDescription<br/>Description')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description', 'Description\nDescription<br/>Description')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description_language', 'en')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description_language', 'en')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description_type', 'Abstract')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 0], [('subitem_description_type', 'Abstract')]), ('add', 'item_1617186626617.attribute_value_mlt', [(1, {})]), ('add', 'item_1617186626617.attribute_value_mlt', [(1, {})]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description', '概要\n概要\n概要\n概要')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description', '概要\n概要\n概要\n概要')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description_language', 'ja')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description_language', 'ja')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description_type', 'Abstract')]), ('add', ['item_1617186626617', 'attribute_value_mlt', 1], [('subitem_description_type', 'Abstract')]), ('add', '', [('item_1617186643794', {})]), ('add', '', [('item_1617186643794', {})]), ('add', 'item_1617186643794', [('attribute_name', 'Publisher')]), ('add', 'item_1617186643794', [('attribute_name', 'Publisher')]), ('add', 'item_1617186643794', [('attribute_value_mlt', [])]), ('add', 'item_1617186643794', [('attribute_value_mlt', [])]), ('add', 'item_1617186643794.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186643794.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186643794', 'attribute_value_mlt', 0], [('subitem_1522300295150', 'en')]), ('add', ['item_1617186643794', 'attribute_value_mlt', 0], [('subitem_1522300295150', 'en')]), ('add', ['item_1617186643794', 'attribute_value_mlt', 0], [('subitem_1522300316516', 'Publisher')]), ('add', ['item_1617186643794', 'attribute_value_mlt', 0], [('subitem_1522300316516', 'Publisher')]), ('add', '', [('item_1617186660861', {})]), ('add', '', [('item_1617186660861', {})]), ('add', 'item_1617186660861', [('attribute_name', 'Date')]), ('add', 'item_1617186660861', [('attribute_name', 'Date')]), ('add', 'item_1617186660861', [('attribute_value_mlt', [])]), ('add', 'item_1617186660861', [('attribute_value_mlt', [])]), ('add', 'item_1617186660861.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186660861.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186660861', 'attribute_value_mlt', 0], [('subitem_1522300695726', 'Available')]), ('add', ['item_1617186660861', 'attribute_value_mlt', 0], [('subitem_1522300695726', 'Available')]), ('add', ['item_1617186660861', 'attribute_value_mlt', 0], [('subitem_1522300722591', '2021-06-30')]), ('add', ['item_1617186660861', 'attribute_value_mlt', 0], [('subitem_1522300722591', '2021-06-30')]), ('add', '', [('item_1617186702042', {})]), ('add', '', [('item_1617186702042', {})]), ('add', 'item_1617186702042', [('attribute_name', 'Language')]), ('add', 'item_1617186702042', [('attribute_name', 'Language')]), ('add', 'item_1617186702042', [('attribute_value_mlt', [])]), ('add', 'item_1617186702042', [('attribute_value_mlt', [])]), ('add', 'item_1617186702042.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186702042.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186702042', 'attribute_value_mlt', 0], [('subitem_1551255818386', 'jpn')]), ('add', ['item_1617186702042', 'attribute_value_mlt', 0], [('subitem_1551255818386', 'jpn')]), ('add', '', [('item_1617186783814', {})]), ('add', '', [('item_1617186783814', {})]), ('add', 'item_1617186783814', [('attribute_name', 'Identifier')]), ('add', 'item_1617186783814', [('attribute_name', 'Identifier')]), ('add', 'item_1617186783814', [('attribute_value_mlt', [])]), ('add', 'item_1617186783814', [('attribute_value_mlt', [])]), ('add', 'item_1617186783814.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186783814.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186783814', 'attribute_value_mlt', 0], [('subitem_identifier_type', 'URI')]), ('add', ['item_1617186783814', 'attribute_value_mlt', 0], [('subitem_identifier_type', 'URI')]), ('add', ['item_1617186783814', 'attribute_value_mlt', 0], [('subitem_identifier_uri', 'http://localhost')]), ('add', ['item_1617186783814', 'attribute_value_mlt', 0], [('subitem_identifier_uri', 'http://localhost')]), ('add', '', [('item_1617186859717', {})]), ('add', '', [('item_1617186859717', {})]), ('add', 'item_1617186859717', [('attribute_name', 'Temporal')]), ('add', 'item_1617186859717', [('attribute_name', 'Temporal')]), ('add', 'item_1617186859717', [('attribute_value_mlt', [])]), ('add', 'item_1617186859717', [('attribute_value_mlt', [])]), ('add', 'item_1617186859717.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186859717.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186859717', 'attribute_value_mlt', 0], [('subitem_1522658018441', 'en')]), ('add', ['item_1617186859717', 'attribute_value_mlt', 0], [('subitem_1522658018441', 'en')]), ('add', ['item_1617186859717', 'attribute_value_mlt', 0], [('subitem_1522658031721', 'Temporal')]), ('add', ['item_1617186859717', 'attribute_value_mlt', 0], [('subitem_1522658031721', 'Temporal')]), ('add', '', [('item_1617186882738', {})]), ('add', '', [('item_1617186882738', {})]), ('add', 'item_1617186882738', [('attribute_name', 'Geo Location')]), ('add', 'item_1617186882738', [('attribute_name', 'Geo Location')]), ('add', 'item_1617186882738', [('attribute_value_mlt', [])]), ('add', 'item_1617186882738', [('attribute_value_mlt', [])]), ('add', 'item_1617186882738.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186882738.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0], [('subitem_geolocation_place', [])]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0], [('subitem_geolocation_place', [])]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0, 'subitem_geolocation_place'], [(0, {})]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0, 'subitem_geolocation_place'], [(0, {})]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0, 'subitem_geolocation_place', 0], [('subitem_geolocation_place_text', 'Japan')]), ('add', ['item_1617186882738', 'attribute_value_mlt', 0, 'subitem_geolocation_place', 0], [('subitem_geolocation_place_text', 'Japan')]), ('add', '', [('item_1617186901218', {})]), ('add', '', [('item_1617186901218', {})]), ('add', 'item_1617186901218', [('attribute_name', 'Funding Reference')]), ('add', 'item_1617186901218', [('attribute_name', 'Funding Reference')]), ('add', 'item_1617186901218', [('attribute_value_mlt', [])]), ('add', 'item_1617186901218', [('attribute_value_mlt', [])]), ('add', 'item_1617186901218.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186901218.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399143519', {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399143519', {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399143519'], [('subitem_1522399281603', 'ISNI')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399143519'], [('subitem_1522399281603', 'ISNI')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399143519'], [('subitem_1522399333375', 'http://xxx')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399143519'], [('subitem_1522399333375', 'http://xxx')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399412622', [])]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399412622', [])]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622'], [(0, {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622'], [(0, {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622', 0], [('subitem_1522399416691', 'en')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622', 0], [('subitem_1522399416691', 'en')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622', 0], [('subitem_1522737543681', 'Funder Name')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399412622', 0], [('subitem_1522737543681', 'Funder Name')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399571623', {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399571623', {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399571623'], [('subitem_1522399585738', 'Award URI')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399571623'], [('subitem_1522399585738', 'Award URI')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399571623'], [('subitem_1522399628911', 'Award Number')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399571623'], [('subitem_1522399628911', 'Award Number')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399651758', [])]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0], [('subitem_1522399651758', [])]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758'], [(0, {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758'], [(0, {})]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758', 0], [('subitem_1522721910626', 'en')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758', 0], [('subitem_1522721910626', 'en')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758', 0], [('subitem_1522721929892', 'Award Title')]), ('add', ['item_1617186901218', 'attribute_value_mlt', 0, 'subitem_1522399651758', 0], [('subitem_1522721929892', 'Award Title')]), ('add', '', [('item_1617186920753', {})]), ('add', '', [('item_1617186920753', {})]), ('add', 'item_1617186920753', [('attribute_name', 'Source Identifier')]), ('add', 'item_1617186920753', [('attribute_name', 'Source Identifier')]), ('add', 'item_1617186920753', [('attribute_value_mlt', [])]), ('add', 'item_1617186920753', [('attribute_value_mlt', [])]), ('add', 'item_1617186920753.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186920753.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186920753', 'attribute_value_mlt', 0], [('subitem_1522646500366', 'ISSN')]), ('add', ['item_1617186920753', 'attribute_value_mlt', 0], [('subitem_1522646500366', 'ISSN')]), ('add', ['item_1617186920753', 'attribute_value_mlt', 0], [('subitem_1522646572813', 'xxxx-xxxx-xxxx')]), ('add', ['item_1617186920753', 'attribute_value_mlt', 0], [('subitem_1522646572813', 'xxxx-xxxx-xxxx')]), ('add', '', [('item_1617186941041', {})]), ('add', '', [('item_1617186941041', {})]), ('add', 'item_1617186941041', [('attribute_name', 'Source Title')]), ('add', 'item_1617186941041', [('attribute_name', 'Source Title')]), ('add', 'item_1617186941041', [('attribute_value_mlt', [])]), ('add', 'item_1617186941041', [('attribute_value_mlt', [])]), ('add', 'item_1617186941041.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186941041.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186941041', 'attribute_value_mlt', 0], [('subitem_1522650068558', 'en')]), ('add', ['item_1617186941041', 'attribute_value_mlt', 0], [('subitem_1522650068558', 'en')]), ('add', ['item_1617186941041', 'attribute_value_mlt', 0], [('subitem_1522650091861', 'Source Title')]), ('add', ['item_1617186941041', 'attribute_value_mlt', 0], [('subitem_1522650091861', 'Source Title')]), ('add', '', [('item_1617186959569', {})]), ('add', '', [('item_1617186959569', {})]), ('add', 'item_1617186959569', [('attribute_name', 'Volume Number')]), ('add', 'item_1617186959569', [('attribute_name', 'Volume Number')]), ('add', 'item_1617186959569', [('attribute_value_mlt', [])]), ('add', 'item_1617186959569', [('attribute_value_mlt', [])]), ('add', 'item_1617186959569.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186959569.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186959569', 'attribute_value_mlt', 0], [('subitem_1551256328147', '1')]), ('add', ['item_1617186959569', 'attribute_value_mlt', 0], [('subitem_1551256328147', '1')]), ('add', '', [('item_1617186981471', {})]), ('add', '', [('item_1617186981471', {})]), ('add', 'item_1617186981471', [('attribute_name', 'Issue Number')]), ('add', 'item_1617186981471', [('attribute_name', 'Issue Number')]), ('add', 'item_1617186981471', [('attribute_value_mlt', [])]), ('add', 'item_1617186981471', [('attribute_value_mlt', [])]), ('add', 'item_1617186981471.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186981471.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186981471', 'attribute_value_mlt', 0], [('subitem_1551256294723', '111')]), ('add', ['item_1617186981471', 'attribute_value_mlt', 0], [('subitem_1551256294723', '111')]), ('add', '', [('item_1617186994930', {})]), ('add', '', [('item_1617186994930', {})]), ('add', 'item_1617186994930', [('attribute_name', 'Number of Pages')]), ('add', 'item_1617186994930', [('attribute_name', 'Number of Pages')]), ('add', 'item_1617186994930', [('attribute_value_mlt', [])]), ('add', 'item_1617186994930', [('attribute_value_mlt', [])]), ('add', 'item_1617186994930.attribute_value_mlt', [(0, {})]), ('add', 'item_1617186994930.attribute_value_mlt', [(0, {})]), ('add', ['item_1617186994930', 'attribute_value_mlt', 0], [('subitem_1551256248092', '12')]), ('add', ['item_1617186994930', 'attribute_value_mlt', 0], [('subitem_1551256248092', '12')]), ('add', '', [('item_1617187024783', {})]), ('add', '', [('item_1617187024783', {})]), ('add', 'item_1617187024783', [('attribute_name', 'Page Start')]), ('add', 'item_1617187024783', [('attribute_name', 'Page Start')]), ('add', 'item_1617187024783', [('attribute_value_mlt', [])]), ('add', 'item_1617187024783', [('attribute_value_mlt', [])]), ('add', 'item_1617187024783.attribute_value_mlt', [(0, {})]), ('add', 'item_1617187024783.attribute_value_mlt', [(0, {})]), ('add', ['item_1617187024783', 'attribute_value_mlt', 0], [('subitem_1551256198917', '1')]), ('add', ['item_1617187024783', 'attribute_value_mlt', 0], [('subitem_1551256198917', '1')]), ('add', '', [('item_1617187045071', {})]), ('add', '', [('item_1617187045071', {})]), ('add', 'item_1617187045071', [('attribute_name', 'Page End')]), ('add', 'item_1617187045071', [('attribute_name', 'Page End')]), ('add', 'item_1617187045071', [('attribute_value_mlt', [])]), ('add', 'item_1617187045071', [('attribute_value_mlt', [])]), ('add', 'item_1617187045071.attribute_value_mlt', [(0, {})]), ('add', 'item_1617187045071.attribute_value_mlt', [(0, {})]), ('add', ['item_1617187045071', 'attribute_value_mlt', 0], [('subitem_1551256185532', '3')]), ('add', ['item_1617187045071', 'attribute_value_mlt', 0], [('subitem_1551256185532', '3')]), ('add', '', [('item_1617187112279', {})]), ('add', '', [('item_1617187112279', {})]), ('add', 'item_1617187112279', [('attribute_name', 'Degree Name')]), ('add', 'item_1617187112279', [('attribute_name', 'Degree Name')]), ('add', 'item_1617187112279', [('attribute_value_mlt', [])]), ('add', 'item_1617187112279', [('attribute_value_mlt', [])]), ('add', 'item_1617187112279.attribute_value_mlt', [(0, {})]), ('add', 'item_1617187112279.attribute_value_mlt', [(0, {})]), ('add', ['item_1617187112279', 'attribute_value_mlt', 0], [('subitem_1551256126428', 'Degree Name')]), ('add', ['item_1617187112279', 'attribute_value_mlt', 0], [('subitem_1551256126428', 'Degree Name')]), ('add', ['item_1617187112279', 'attribute_value_mlt', 0], [('subitem_1551256129013', 'en')]), ('add', ['item_1617187112279', 'attribute_value_mlt', 0], [('subitem_1551256129013', 'en')]), ('add', '', [('item_1617187136212', {})]), ('add', '', [('item_1617187136212', {})]), ('add', 'item_1617187136212', [('attribute_name', 'Date Granted')]), ('add', 'item_1617187136212', [('attribute_name', 'Date Granted')]), ('add', 'item_1617187136212', [('attribute_value_mlt', [])]), ('add', 'item_1617187136212', [('attribute_value_mlt', [])]), ('add', 'item_1617187136212.attribute_value_mlt', [(0, {})]), ('add', 'item_1617187136212.attribute_value_mlt', [(0, {})]), ('add', ['item_1617187136212', 'attribute_value_mlt', 0], [('subitem_1551256096004', '2021-06-30')]), ('add', ['item_1617187136212', 'attribute_value_mlt', 0], [('subitem_1551256096004', '2021-06-30')]), ('add', '', [('item_1617187187528', {})]), ('add', '', [('item_1617187187528', {})]), ('add', 'item_1617187187528', [('attribute_name', 'Conference')]), ('add', 'item_1617187187528', [('attribute_name', 'Conference')]), ('add', 'item_1617187187528', [('attribute_value_mlt', [])]), ('add', 'item_1617187187528', [('attribute_value_mlt', [])]), ('add', 'item_1617187187528.attribute_value_mlt', [(0, {})]), ('add', 'item_1617187187528.attribute_value_mlt', [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711633003', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711633003', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003', 0], [('subitem_1599711636923', 'Conference Name')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003', 0], [('subitem_1599711636923', 'Conference Name')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003', 0], [('subitem_1599711645590', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711633003', 0], [('subitem_1599711645590', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711655652', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711655652', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711660052', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711660052', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052', 0], [('subitem_1599711680082', 'Sponsor')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052', 0], [('subitem_1599711680082', 'Sponsor')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052', 0], [('subitem_1599711686511', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711660052', 0], [('subitem_1599711686511', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711699392', {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711699392', {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711704251', '2020/12/11')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711704251', '2020/12/11')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711712451', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711712451', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711727603', '12')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711727603', '12')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711731891', '2000')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711731891', '2000')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711735410', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711735410', '1')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711739022', '12')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711739022', '12')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711743722', '2020')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711743722', '2020')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711745532', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711699392'], [('subitem_1599711745532', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711758470', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711758470', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470', 0], [('subitem_1599711769260', 'Conference Venue')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470', 0], [('subitem_1599711769260', 'Conference Venue')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470', 0], [('subitem_1599711775943', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711758470', 0], [('subitem_1599711775943', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711788485', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711788485', [])]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485'], [(0, {})]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485', 0], [('subitem_1599711798761', 'Conference Place')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485', 0], [('subitem_1599711798761', 'Conference Place')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485', 0], [('subitem_1599711803382', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0, 'subitem_1599711788485', 0], [('subitem_1599711803382', 'ja')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711813532', 'JPN')]), ('add', ['item_1617187187528', 'attribute_value_mlt', 0], [('subitem_1599711813532', 'JPN')]), ('add', '', [('item_1617258105262', {})]), ('add', '', [('item_1617258105262', {})]), ('add', 'item_1617258105262', [('attribute_name', 'Resource Type')]), ('add', 'item_1617258105262', [('attribute_name', 'Resource Type')]), ('add', 'item_1617258105262', [('attribute_value_mlt', [])]), ('add', 'item_1617258105262', [('attribute_value_mlt', [])]), ('add', 'item_1617258105262.attribute_value_mlt', [(0, {})]), ('add', 'item_1617258105262.attribute_value_mlt', [(0, {})]), ('add', ['item_1617258105262', 'attribute_value_mlt', 0], [('resourcetype', 'conference paper')]), ('add', ['item_1617258105262', 'attribute_value_mlt', 0], [('resourcetype', 'conference paper')]), ('add', ['item_1617258105262', 'attribute_value_mlt', 0], [('resourceuri', 'http://purl.org/coar/resource_type/c_5794')]), ('add', ['item_1617258105262', 'attribute_value_mlt', 0], [('resourceuri', 'http://purl.org/coar/resource_type/c_5794')]), ('add', '', [('item_1617265215918', {})]), ('add', '', [('item_1617265215918', {})]), ('add', 'item_1617265215918', [('attribute_name', 'Version Type')]), ('add', 'item_1617265215918', [('attribute_name', 'Version Type')]), ('add', 'item_1617265215918', [('attribute_value_mlt', [])]), ('add', 'item_1617265215918', [('attribute_value_mlt', [])]), ('add', 'item_1617265215918.attribute_value_mlt', [(0, {})]), ('add', 'item_1617265215918.attribute_value_mlt', [(0, {})]), ('add', ['item_1617265215918', 'attribute_value_mlt', 0], [('subitem_1522305645492', 'AO')]), ('add', ['item_1617265215918', 'attribute_value_mlt', 0], [('subitem_1522305645492', 'AO')]), ('add', ['item_1617265215918', 'attribute_value_mlt', 0], [('subitem_1600292170262', 'http://purl.org/coar/version/c_b1a7d7d4d402bcce')]), ('add', ['item_1617265215918', 'attribute_value_mlt', 0], [('subitem_1600292170262', 'http://purl.org/coar/version/c_b1a7d7d4d402bcce')]), ('add', '', [('item_1617349709064', {})]), ('add', '', [('item_1617349709064', {})]), ('add', 'item_1617349709064', [('attribute_name', 'Contributor')]), ('add', 'item_1617349709064', [('attribute_name', 'Contributor')]), ('add', 'item_1617349709064', [('attribute_value_mlt', [])]), ('add', 'item_1617349709064', [('attribute_value_mlt', [])]), ('add', 'item_1617349709064.attribute_value_mlt', [(0, {})]), ('add', 'item_1617349709064.attribute_value_mlt', [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorMails', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorMails', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorMails'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorMails'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorMails', 0], [('contributorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorMails', 0], [('contributorMail', 'wekosoftware@nii.ac.jp')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 0], [('contributorName', '情報, 太郎')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 0], [('contributorName', '情報, 太郎')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 0], [('lang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 0], [('lang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 1], [('contributorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 1], [('contributorName', 'ジョウホウ, タロウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 1], [('lang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 1], [('lang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 2], [('contributorName', 'Joho, Taro')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 2], [('contributorName', 'Joho, Taro')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 2], [('lang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'contributorNames', 2], [('lang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorType', 'ContactPerson')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('contributorType', 'ContactPerson')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('familyNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('familyNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyName', '情報')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 0], [('familyNameLang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyName', 'ジョウホウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 1], [('familyNameLang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyName', 'Joho')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'familyNames', 2], [('familyNameLang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('givenNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('givenNames', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenName', '太郎')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 0], [('givenNameLang', 'ja')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenName', 'タロウ')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 1], [('givenNameLang', 'ja-Kana')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenName', 'Taro')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'givenNames', 2], [('givenNameLang', 'en')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(1, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierScheme', 'CiNii')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 1], [('nameIdentifierURI', 'https://ci.nii.ac.jp/')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(2, {})]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifier', 'xxxxxxx')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierScheme', 'KAKEN2')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', ['item_1617349709064', 'attribute_value_mlt', 0, 'nameIdentifiers', 2], [('nameIdentifierURI', 'https://kaken.nii.ac.jp/')]), ('add', '', [('item_1617349808926', {})]), ('add', '', [('item_1617349808926', {})]), ('add', 'item_1617349808926', [('attribute_name', 'Version')]), ('add', 'item_1617349808926', [('attribute_name', 'Version')]), ('add', 'item_1617349808926', [('attribute_value_mlt', [])]), ('add', 'item_1617349808926', [('attribute_value_mlt', [])]), ('add', 'item_1617349808926.attribute_value_mlt', [(0, {})]), ('add', 'item_1617349808926.attribute_value_mlt', [(0, {})]), ('add', ['item_1617349808926', 'attribute_value_mlt', 0], [('subitem_1523263171732', 'Version')]), ('add', ['item_1617349808926', 'attribute_value_mlt', 0], [('subitem_1523263171732', 'Version')]), ('add', '', [('item_1617351524846', {})]), ('add', '', [('item_1617351524846', {})]), ('add', 'item_1617351524846', [('attribute_name', 'APC')]), ('add', 'item_1617351524846', [('attribute_name', 'APC')]), ('add', 'item_1617351524846', [('attribute_value_mlt', [])]), ('add', 'item_1617351524846', [('attribute_value_mlt', [])]), ('add', 'item_1617351524846.attribute_value_mlt', [(0, {})]), ('add', 'item_1617351524846.attribute_value_mlt', [(0, {})]), ('add', ['item_1617351524846', 'attribute_value_mlt', 0], [('subitem_1523260933860', 'Unknown')]), ('add', ['item_1617351524846', 'attribute_value_mlt', 0], [('subitem_1523260933860', 'Unknown')]), ('add', '', [('item_1617353299429', {})]), ('add', '', [('item_1617353299429', {})]), ('add', 'item_1617353299429', [('attribute_name', 'Relation')]), ('add', 'item_1617353299429', [('attribute_name', 'Relation')]), ('add', 'item_1617353299429', [('attribute_value_mlt', [])]), ('add', 'item_1617353299429', [('attribute_value_mlt', [])]), ('add', 'item_1617353299429.attribute_value_mlt', [(0, {})]), ('add', 'item_1617353299429.attribute_value_mlt', [(0, {})]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1522306207484', 'isVersionOf')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1522306207484', 'isVersionOf')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1522306287251', {})]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1522306287251', {})]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1522306287251'], [('subitem_1522306382014', 'arXiv')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1522306287251'], [('subitem_1522306382014', 'arXiv')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1522306287251'], [('subitem_1522306436033', 'xxxxx')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1522306287251'], [('subitem_1522306436033', 'xxxxx')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1523320863692', [])]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0], [('subitem_1523320863692', [])]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692'], [(0, {})]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692'], [(0, {})]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692', 0], [('subitem_1523320867455', 'en')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692', 0], [('subitem_1523320867455', 'en')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692', 0], [('subitem_1523320909613', 'Related Title')]), ('add', ['item_1617353299429', 'attribute_value_mlt', 0, 'subitem_1523320863692', 0], [('subitem_1523320909613', 'Related Title')]), ('add', '', [('item_1617605131499', {})]), ('add', '', [('item_1617605131499', {})]), ('add', 'item_1617605131499', [('attribute_name', 'File')]), ('add', 'item_1617605131499', [('attribute_name', 'File')]), ('add', 'item_1617605131499', [('attribute_type', 'file')]), ('add', 'item_1617605131499', [('attribute_type', 'file')]), ('add', 'item_1617605131499', [('attribute_value_mlt', [])]), ('add', 'item_1617605131499', [('attribute_value_mlt', [])]), ('add', 'item_1617605131499.attribute_value_mlt', [(0, {})]), ('add', 'item_1617605131499.attribute_value_mlt', [(0, {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('accessrole', 'open_access')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('accessrole', 'open_access')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('date', [])]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('date', [])]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date'], [(0, {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date'], [(0, {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date', 0], [('dateType', 'Available')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date', 0], [('dateType', 'Available')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date', 0], [('dateValue', '2021-07-12')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'date', 0], [('dateValue', '2021-07-12')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('displaytype', 'simple')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('displaytype', 'simple')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('filename', '1KB.pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('filename', '1KB.pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('filesize', [])]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('filesize', [])]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'filesize'], [(0, {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'filesize'], [(0, {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'filesize', 0], [('value', '1 KB')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'filesize', 0], [('value', '1 KB')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('format', 'text/plain')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('format', 'text/plain')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('mimetype', 'application/pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('mimetype', 'application/pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('url', {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('url', {})]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'url'], [('url', 'https://weko3.example.org/record/13/files/1KB.pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0, 'url'], [('url', 'https://weko3.example.org/record/13/files/1KB.pdf')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('version_id', '7cdce099-fe63-445f-b78b-cf2909a8163f')]), ('add', ['item_1617605131499', 'attribute_value_mlt', 0], [('version_id', '7cdce099-fe63-445f-b78b-cf2909a8163f')]), ('add', '', [('item_1617610673286', {})]), ('add', '', [('item_1617610673286', {})]), ('add', 'item_1617610673286', [('attribute_name', 'Rights Holder')]), ('add', 'item_1617610673286', [('attribute_name', 'Rights Holder')]), ('add', 'item_1617610673286', [('attribute_value_mlt', [])]), ('add', 'item_1617610673286', [('attribute_value_mlt', [])]), ('add', 'item_1617610673286.attribute_value_mlt', [(0, {})]), ('add', 'item_1617610673286.attribute_value_mlt', [(0, {})]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0], [('nameIdentifiers', [])]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers'], [(0, {})]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxx')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifier', 'xxxxxx')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierScheme', 'ORCID')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'nameIdentifiers', 0], [('nameIdentifierURI', 'https://orcid.org/')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0], [('rightHolderNames', [])]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0], [('rightHolderNames', [])]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames'], [(0, {})]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames'], [(0, {})]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames', 0], [('rightHolderLanguage', 'ja')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames', 0], [('rightHolderLanguage', 'ja')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames', 0], [('rightHolderName', 'Right Holder Name')]), ('add', ['item_1617610673286', 'attribute_value_mlt', 0, 'rightHolderNames', 0], [('rightHolderName', 'Right Holder Name')]), ('add', '', [('item_1617620223087', {})]), ('add', '', [('item_1617620223087', {})]), ('add', 'item_1617620223087', [('attribute_name', 'Heading')]), ('add', 'item_1617620223087', [('attribute_name', 'Heading')]), ('add', 'item_1617620223087', [('attribute_value_mlt', [])]), ('add', 'item_1617620223087', [('attribute_value_mlt', [])]), ('add', 'item_1617620223087.attribute_value_mlt', [(0, {})]), ('add', 'item_1617620223087.attribute_value_mlt', [(0, {})]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671149650', 'ja')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671149650', 'ja')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671169640', 'Banner Headline')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671169640', 'Banner Headline')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671178623', 'Subheading')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 0], [('subitem_1565671178623', 'Subheading')]), ('add', 'item_1617620223087.attribute_value_mlt', [(1, {})]), ('add', 'item_1617620223087.attribute_value_mlt', [(1, {})]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671149650', 'en')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671149650', 'en')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671169640', 'Banner Headline')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671169640', 'Banner Headline')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671178623', 'Subheding')]), ('add', ['item_1617620223087', 'attribute_value_mlt', 1], [('subitem_1565671178623', 'Subheding')]), ('add', '', [('item_1617944105607', {})]), ('add', '', [('item_1617944105607', {})]), ('add', 'item_1617944105607', [('attribute_name', 'Degree Grantor')]), ('add', 'item_1617944105607', [('attribute_name', 'Degree Grantor')]), ('add', 'item_1617944105607', [('attribute_value_mlt', [])]), ('add', 'item_1617944105607', [('attribute_value_mlt', [])]), ('add', 'item_1617944105607.attribute_value_mlt', [(0, {})]), ('add', 'item_1617944105607.attribute_value_mlt', [(0, {})]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0], [('subitem_1551256015892', [])]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0], [('subitem_1551256015892', [])]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892'], [(0, {})]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892'], [(0, {})]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892', 0], [('subitem_1551256027296', 'xxxxxx')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892', 0], [('subitem_1551256027296', 'xxxxxx')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892', 0], [('subitem_1551256029891', 'kakenhi')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256015892', 0], [('subitem_1551256029891', 'kakenhi')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0], [('subitem_1551256037922', [])]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0], [('subitem_1551256037922', [])]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922'], [(0, {})]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922'], [(0, {})]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922', 0], [('subitem_1551256042287', 'Degree Grantor Name')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922', 0], [('subitem_1551256042287', 'Degree Grantor Name')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922', 0], [('subitem_1551256047619', 'en')]), ('add', ['item_1617944105607', 'attribute_value_mlt', 0, 'subitem_1551256037922', 0], [('subitem_1551256047619', 'en')]), ('add', '', [('item_title', 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', '', [('item_title', 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', '', [('item_type_id', '15')]), ('add', '', [('item_type_id', '15')]), ('add', '', [('owner', '1')]), ('add', '', [('owner', '1')]), ('add', '', [('path', [])]), ('add', '', [('path', [])]), ('add', 'path', [(0, '1661517684078')]), ('add', 'path', [(0, '1661517684078')]), ('add', '', [('pubdate', {})]), ('add', '', [('pubdate', {})]), ('add', 'pubdate', [('attribute_name', 'PubDate')]), ('add', 'pubdate', [('attribute_name', 'PubDate')]), ('add', 'pubdate', [('attribute_value', '2021-08-06')]), ('add', 'pubdate', [('attribute_value', '2021-08-06')]), ('add', '', [('publish_date', '2021-08-06')]), ('add', '', [('publish_date', '2021-08-06')]), ('add', '', [('publish_status', '0')]), ('add', '', [('publish_status', '0')]), ('add', '', [('relation_version_is_last', True)]), ('add', '', [('relation_version_is_last', True)]), ('add', '', [('title', [])]), ('add', '', [('title', [])]), ('add', 'title', [(0, 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', 'title', [(0, 'ja_conference paperITEM00000001(public_open_access_open_access_simple)')]), ('add', '', [('weko_shared_id', -1)]), ('add', '', [('weko_shared_id', -1)])]
            distination = {'recid': '13', '$schema': 'https://127.0.0.1/schema/deposits/deposit-v1.0.0.json', '_buckets': {'deposit': '753ff0d7-0659-4460-9b1a-fd1ef38467f2'}, '_deposit': {'id': '13', 'owners': [1], 'status': 'draft'}}
            ret = dep._patch(diff_result,distination)
            assert ret==''

    # def add(node, changes):
    # def change(node, changes):
    # def remove(node, changes):
    
    # def _publish_new(self, id_=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__publish_new -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__publish_new(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            record=dep._publish_new()
            assert record['status']=='draft'

    # def _update_version_id(self, metas, bucket_id):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__update_version_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__update_version_id(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            assert False

    # def publish(self, pid=None, id_=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_publish -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_publish(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            assert False

    # def publish_without_commit(self, pid=None, id_=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_publish_without_commit -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_publish_without_commit(self,app,location):
        with app.test_request_context():
            dep = WekoDeposit.create({})
            assert False

    # def create(cls, data, id_=None, recid=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_create -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_create(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            db.session.commit()
            assert isinstance(ex,WekoDeposit)
            id = uuid.uuid4()
            ex2 = WekoDeposit.create({},id_=id)
            db.session.commit()
            assert isinstance(ex2,WekoDeposit)

    # def update(self, *args, **kwargs):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_update -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False


    # def clear(self, *args, **kwargs):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_clear -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_clear(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def delete(self, force=True, pid=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def commit(self, *args, **kwargs):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_commit -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_commit(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False


    # def newversion(self, pid=None, is_draft=False):
    #             # NOTE: We call the superclass `create()` method, because
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_newversion -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_newversion(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def get_content_files(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_get_content_files -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_content_files(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def get_file_data(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_get_file_data -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_file_data(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def save_or_update_item_metadata(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_save_or_update_item_metadata -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_save_or_update_item_metadata(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def delete_old_file_index(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete_old_file_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_old_file_index(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False


    # def delete_item_metadata(self, data):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete_item_metadata -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_item_metadata(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def convert_item_metadata(self, index_obj, data=None):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_convert_item_metadata -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_convert_item_metadata(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def _convert_description_to_object(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__convert_description_to_object -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__convert_description_to_object(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def _convert_jpcoar_data_to_es(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__convert_jpcoar_data_to_es -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__convert_jpcoar_data_to_es(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def _convert_data_for_geo_location(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test__convert_data_for_geo_location -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__convert_data_for_geo_location(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    #         def _convert_geo_location(value):
    #         def _convert_geo_location_box():

    # def delete_by_index_tree_id(cls, index_id: str, ignore_items: list = []):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete_by_index_tree_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_by_index_tree_id(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def update_pid_by_index_tree_id(self, path):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_update_pid_by_index_tree_id -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_pid_by_index_tree_id(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def update_item_by_task(self, *args, **kwargs):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_update_item_by_task -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_item_by_task(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def delete_es_index_attempt(self, pid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete_es_index_attempt -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_es_index_attempt(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def update_author_link(self, author_link):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_update_author_link -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_author_link(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def update_feedback_mail(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_update_feedback_mail -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_update_feedback_mail(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def remove_feedback_mail(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_remove_feedback_mail -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_remove_feedback_mail(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def clean_unuse_file_contents(self, item_id, pre_object_versions,
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_clean_unuse_file_contents -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_clean_unuse_file_contents(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def merge_data_to_record_without_version(self, pid, keep_version=False,
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_newversion -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_merge_data_to_record_without_version(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def prepare_draft_item(self, recid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_prepare_draft_item -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_prepare_draft_item(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

    # def delete_content_files(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoDeposit::test_delete_content_files -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_delete_content_files(sel,app,db,location):
        with app.test_request_context():
            ex = WekoDeposit.create({})
            assert False

# class WekoRecord(Record):
# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
class TestWekoRecord:
    #     def pid(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid(self):
        record = WekoRecord({})
        assert record.pid()==""

    #     def pid_recid(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid_recid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid_recid(self):
        record = WekoRecord({})
        assert record.pid_recid()==""

    #     def hide_file(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_hide_file -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_hide_file(self):
        record = WekoRecord({})
        assert record.hide_file()==""

    #     def navi(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_navi -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_navi(self):
        record = WekoRecord({})
        assert record.navi()==""

    #     def item_type_info(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_item_type_info -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_item_type_info(self):
        record = WekoRecord({})
        assert record.item_type_info()==""

    #     def switching_language(data):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_switching_language -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_switching_language(self):
        record = WekoRecord({})
        assert record.switching_language({})==""

    #     def __get_titles_key(item_type_mapping):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test___get_titles_key -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test___get_titles_key(self):
        record = WekoRecord({})
        assert record.__get_titles_key({})==""

    #     def get_titles(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_titles -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_titles(self):
        record = WekoRecord({})
        assert record.get_titles()==""

    #     def items_show_list(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_items_show_list -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_items_show_list(self):
        record = WekoRecord({})
        assert record.items_show_list()==""

    #     def display_file_info(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_display_file_info -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_display_file_info(self):
        record = WekoRecord({})
        assert record.display_file_info()==""

    #     def __remove_special_character_of_weko2(self, metadata):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test___remove_special_character_of_weko2 -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test___remove_special_character_of_weko2(self):
        record = WekoRecord({})
        assert record.__remove_special_character_of_weko2({})==""

    #     def _get_creator(meta_data, hide_email_flag):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test__get_creator -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__get_creator(self):
        record = WekoRecord({})
        assert record._get_creator({},False)==""

    #     def __remove_file_metadata_do_not_publish(self, file_metadata_list):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test___remove_file_metadata_do_not_publish -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test___remove_file_metadata_do_not_publish(self):
        record = WekoRecord({})
        assert record.__remove_file_metadata_do_not_publish([])==""

    #     def __check_user_permission(user_id_list):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test___check_user_permission -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test___check_user_permission(self):
        record = WekoRecord({})
        assert record.__check_user_permission([])==""

    #     def is_input_open_access_date(file_metadata):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_is_input_open_access_date -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_is_input_open_access_date(self):
        record = WekoRecord({})
        assert record.is_input_open_access_date()==""

    #     def is_do_not_publish(file_metadata):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_is_do_not_publish -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_is_do_not_publish(self):
        record = WekoRecord({})
        assert record.is_do_not_publish()==""

    #     def get_open_date_value(file_metadata):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_open_date_value -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_open_date_value(self):
        record = WekoRecord({})
        assert record.get_open_date_value({})==""

    #     def is_future_open_date(self, file_metadata):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_is_future_open_date -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_is_future_open_date(self):
        record = WekoRecord({})
        assert record.is_future_open_date({})==""

    #     def pid_doi(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid_doi -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid_doi(self):
        record = WekoRecord({})
        assert record.pid_doi()==""

    #     def pid_cnri(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid_cnri -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid_cnri(self):
        record = WekoRecord({})
        assert record.pid_cnri()==""

    #     def pid_parent(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid_parent -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid_parent(self):
        record = WekoRecord({})
        assert record.pid_parent()==""

    #     def get_record_by_pid(cls, pid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_record_by_pid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_record_by_pid(self):
        record = WekoRecord({})
        assert record.get_record_by_pid(1)==""

    #     def get_record_by_uuid(cls, uuid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_record_by_uuid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_record_by_uuid(self):
        record = WekoRecord({})
        assert record.get_record_by_uuid('')==""

    #     def get_record_cvs(cls, uuid):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_record_cvsd -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_record_cvsd(self):
        record = WekoRecord({})
        assert record.get_record_cvs('')==""

    #     def _get_pid(self, pid_type):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test__get_pid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test__get_pid(self):
        record = WekoRecord({})
        assert record._get_pid('')==""

    #     def update_item_link(self, pid_value):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_pid -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_pid(self):
        record = WekoRecord({})
        assert record.pid()==""

    #     def get_file_data(self):
    # .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::TestWekoRecord::test_get_file_data -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
    def test_get_file_data(self):
        record = WekoRecord({})
        assert record.get_file_data()==""


# class _FormatSysCreator:
#     def __init__(self, creator):
#     def _get_creator_languages_order(self):
#     def _format_creator_to_show_detail(self, language: str, parent_key: str,
#     def _get_creator_to_show_popup(self, creators: Union[list, dict],
#         def _run_format_affiliation(affiliation_max, affiliation_min,
#         def format_affiliation(affiliation_data):
#     def _get_creator_based_on_language(creator_data: dict,
#     def format_creator(self) -> dict:
#     def _format_creator_on_creator_popup(self, creators: Union[dict, list],
#     def _format_creator_name(creator_data: dict,
#     def _format_creator_affiliation(creator_data: dict,
#         def _get_max_list_length() -> int:
#     def _get_creator_to_display_on_popup(self, creator_list: list):
#     def _merge_creator_data(self, creator_data: Union[list, dict],
#         def merge_data(key, value):
#     def _get_default_creator_name(self, list_parent_key: list,
#         def _get_creator(_language):
# class _FormatSysBibliographicInformation:
#     def __init__(self, bibliographic_meta_data_lst, props_lst):
#     def is_bibliographic(self):
#         def check_key(_meta_data):
#     def get_bibliographic_list(self, is_get_list):
#     def _get_bibliographic(self, bibliographic, is_get_list):
#     def _get_property_name(self, key):
#     def _get_translation_key(key, lang):
#     def _get_bibliographic_information(self, bibliographic):
#     def _get_bibliographic_show_list(self, bibliographic, language):
#     def _get_source_title(source_titles):
#     def _get_source_title_show_list(source_titles, current_lang):
#     def _get_page_tart_and_page_end(page_start, page_end):
#     def _get_issue_date(issue_date):

def test_missing_location(app, record):
    """Test missing location."""
    with pytest.raises(AttributeError):
        WekoRecord.create({}).file
    # for file in record.files:
        # file_info = file.info()


def test_record_create(app, db, location):
    """Test record creation with only bucket."""
    record = WekoRecord.create({'title': 'test'})
    db.session.commit()
    # assert record['_bucket'] == record.bucket_id
    assert '_files' not in record
    # assert len(record.pid)


# .tox/c1/bin/pytest --cov=weko_deposit tests/test_api.py::test_weko_record -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-items-ui/.tox/c1/tmp
def test_weko_record(app,client, db, users, location):
    """Test record files property."""
    user = User.query.filter_by(email=users[4]['email']).first()
    login_user_via_session(client=client,user=user)
    with pytest.raises(MissingModelError):
        WekoRecord({}).files

    AdminSettings.update(
        'items_display_settings',
        {'items_search_author': 'name', 'items_display_email': True},
        1
    )

    # item_type = ItemTypes.create(item_type_name='test', name='test')

    # deposit = WekoDeposit.create({'item_type_id': item_type.id})
    deposit = WekoDeposit.create({})
    db.session.commit()

    record = WekoRecord.get_record_by_pid(deposit.pid.pid_value)

    record.pid

    record.pid_recid

    # record.hide_file

    # record.navi

    # record.item_type_info
    with pytest.raises(AttributeError):
        record.items_show_list

    with pytest.raises(AttributeError):
        record.display_file_info

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        record._get_creator([{}], True)

    record._get_creator({}, False)


def test_files_property(app, db, location):
    """Test record files property."""
    with pytest.raises(MissingModelError):
        WekoRecord({}).files

    deposit = WekoDeposit.create({})
    db.session.commit()

    record = WekoRecord.get_record_by_pid(deposit.pid.pid_value)

    assert 0 == len(record.files)
    assert 'invalid' not in record.files
    # make sure that _files key is not added after accessing record.files
    assert '_files' not in record

    with pytest.raises(KeyError):
        record.files['invalid']

    bucket = record.files.bucket
    assert bucket


def test_format_sys_creator(app, db):
    with app.test_request_context(headers=[('Accept-Language','en')]):
        creator = {
            'creatorNames': [{
                'creatorName': 'test',
                'creatorNameLang': 'en'
            }]
        }

        format_creator = _FormatSysCreator(creator)


def test_format_sys_bibliographic_information_multiple(app, db):
    metadata = [
        {
            "bibliographic_titles":
            [
                {
                    "bibliographic_title": "test",
                    "bibliographic_titleLang": "en"
                }
            ],
            "bibliographicPageEnd": "",
            "bibliographicIssueNumber": "",
            "bibliographicPageStart": "",
            "bibliographicVolumeNumber": "",
            "bibliographicNumberOfPages": "",
            "bibliographicIssueDates": ""
        }
    ]
    with app.test_request_context(headers=[('Accept-Language','en')]):
        sys_bibliographic = _FormatSysBibliographicInformation(metadata, [])

        sys_bibliographic.is_bibliographic()

        sys_bibliographic.get_bibliographic_list(True)

        sys_bibliographic.get_bibliographic_list(False)


def test_weko_deposit(app, db, location):
    deposit = WekoDeposit.create({})
    db.session.commit()

    with pytest.raises(PIDResolveRESTError):
        deposit.update({'actions': 'publish', 'index': '0', }, {})

    with pytest.raises(NoResultFound):
        deposit.item_metadata

    deposit.is_published()

    deposit['_deposit'] = {
        'pid': {
            'revision_id': 1,
            'type': 'pid',
            'value': '1'
        }
    }


def test_weko_indexer(app, db, location):
    deposit = WekoDeposit.create({})
    db.session.commit()

    indexer = WekoIndexer()
    indexer.client=MockClient()
    indexer.client.update_get_error(True)
    with pytest.raises(NotFoundError):
        indexer.update_publish_status(deposit)
    indexer.client.update_get_error(False)
    indexer.get_es_index()

    indexer.upload_metadata(
        jrc={},
        item_id=deposit.id,
        revision_id=0,
        skip_files=True
    )
    indexer.client.update_get_error(True)
    with pytest.raises(NotFoundError):
        indexer.update_relation_version_is_last({
            'id': 1,
            'is_last': True
        })
    indexer.client.update_get_error(False)
    indexer.update_path(deposit, update_revision=False)

    indexer.delete_file_index([deposit.id], 0)

    indexer.get_pid_by_es_scroll('')


def test_weko_indexer(app, db, location):
    deposit = WekoDeposit.create({})
    db.session.commit()

    indexer = WekoIndexer()
    indexer.client=MockClient()
    indexer.client.update_get_error(True)
    with pytest.raises(NotFoundError):
        indexer.update_publish_status(deposit)
    indexer.client.update_get_error(False)
    indexer.get_es_index()

    indexer.upload_metadata(
        jrc={},
        item_id=deposit.id,
        revision_id=0,
        skip_files=True
    )

    indexer.get_pid_by_es_scroll('')


def test_weko_file_object(app, db, location, testfile):
    record = WekoFileObject(
        obj=testfile,
        data={
            'size': 1,
            'format': 'application/msword',
        }
    )


def test_weko_deposit_new(app, db, location):
    recid = '1'
    deposit = WekoDeposit.create({}, recid=int(recid))
    db.session.commit()

    pid = PersistentIdentifier.query.filter_by(
        pid_type='recid',
        pid_value=recid
    ).first()

    record = WekoDeposit.get_record(pid.object_uuid)
    deposit = WekoDeposit(record, record.model)
    with patch('weko_deposit.api.WekoIndexer.update_relation_version_is_last', side_effect=NotFoundError):
        with pytest.raises(NotFoundError):
            deposit.publish()


def test_delete_item_metadata(app, db, location):
    a = {'_oai': {'id': 'oai:weko3.example.org:00000002.1', 'sets': []}, 'path': ['1031'], 'owner': '1', 'recid': '2.1', 'title': ['ja_conference paperITEM00000002(public_open_access_open_access_simple)'], 'pubdate': {'attribute_name': 'PubDate', 'attribute_value': '2021-02-13'}, '_buckets': {'deposit': '9766676f-0a12-439b-b5eb-6c39a61032c6'}, '_deposit': {'id': '2.1', 'pid': {'type': 'depid', 'value': '2.1', 'revision_id': 0}, 'owners': [1], 'status': 'draft'}, 'item_title': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'author_link': ['1', '2', '3'], 'item_type_id': '15', 'publish_date': '2021-02-13', 'publish_status': '0', 'weko_shared_id': -1, 'item_1617186331708': {'attribute_name': 'Title', 'attribute_value_mlt': [{'subitem_1551255647225': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'subitem_1551255648112': 'ja'}, {'subitem_1551255647225': 'en_conference paperITEM00000002(public_open_access_simple)', 'subitem_1551255648112': 'en'}]}, 'item_1617186385884': {'attribute_name': 'Alternative Title', 'attribute_value_mlt': [{'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'en'}, {'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'ja'}]}, 'item_1617186419668': {'attribute_name': 'Creator', 'attribute_type': 'creator', 'attribute_value_mlt': [{'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'creatorNames': [{'creatorName': '情報, 太郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifier': '1', 'nameIdentifierScheme': 'WEKO'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifierScheme': 'ORCID'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'zzzzzzz', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}], 'creatorAffiliations': [{'affiliationNames': [{'affiliationName': 'University', 'affiliationNameLang': 'en'}], 'affiliationNameIdentifiers': [{'affiliationNameIdentifier': '0000000121691048', 'affiliationNameIdentifierURI': 'http://isni.org/isni/0000000121691048', 'affiliationNameIdentifierScheme': 'ISNI'}]}]}, {'givenNames': [{'givenName': '次郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'creatorNames': [{'creatorName': '情報, 次郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifier': '2', 'nameIdentifierScheme': 'WEKO'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'zzzzzzz', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}]}, {'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'creatorNames': [{'creatorName': '情報, 三郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifier': '3', 'nameIdentifierScheme': 'WEKO'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'zzzzzzz', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}]}]}, 'item_1617186476635': {'attribute_name': 'Access Rights', 'attribute_value_mlt': [{'subitem_1522299639480': 'open access', 'subitem_1600958577026': 'http://purl.org/coar/access_right/c_abf2'}]}, 'item_1617186499011': {'attribute_name': 'Rights', 'attribute_value_mlt': [{'subitem_1522650717957': 'ja', 'subitem_1522650727486': 'http://localhost', 'subitem_1522651041219': 'Rights Information'}]}, 'item_1617186609386': {'attribute_name': 'Subject', 'attribute_value_mlt': [{'subitem_1522299896455': 'ja', 'subitem_1522300014469': 'Other', 'subitem_1522300048512': 'http://localhost/', 'subitem_1523261968819': 'Sibject1'}]}, 'item_1617186626617': {'attribute_name': 'Description', 'attribute_value_mlt': [{'subitem_description': 'Description\\nDescription<br/>Description&EMPTY&\\nDescription', 'subitem_description_type': 'Abstract', 'subitem_description_language': 'en'}, {'subitem_description': '概要\\n概要&EMPTY&\\n概要\\n概要', 'subitem_description_type': 'Abstract', 'subitem_description_language': 'ja'}]}, 'item_1617186643794': {'attribute_name': 'Publisher', 'attribute_value_mlt': [{'subitem_1522300295150': 'en', 'subitem_1522300316516': 'Publisher'}]}, 'item_1617186660861': {'attribute_name': 'Date', 'attribute_value_mlt': [{'subitem_1522300695726': 'Available', 'subitem_1522300722591': '2021-06-30'}]}, 'item_1617186702042': {'attribute_name': 'Language', 'attribute_value_mlt': [{'subitem_1551255818386': 'jpn'}]}, 'item_1617186783814': {'attribute_name': 'Identifier', 'attribute_value_mlt': [{'subitem_identifier_uri': 'http://localhost', 'subitem_identifier_type': 'URI'}]}, 'item_1617186859717': {'attribute_name': 'Temporal', 'attribute_value_mlt': [{'subitem_1522658018441': 'en', 'subitem_1522658031721': 'Temporal'}]}, 'item_1617186882738': {'attribute_name': 'Geo Location', 'attribute_value_mlt': [{'subitem_geolocation_place': [{'subitem_geolocation_place_text': 'Japan'}]}]}, 'item_1617186901218': {'attribute_name': 'Funding Reference', 'attribute_value_mlt': [{'subitem_1522399143519': {'subitem_1522399281603': 'ISNI', 'subitem_1522399333375': 'http://xxx'}, 'subitem_1522399412622': [{'subitem_1522399416691': 'en', 'subitem_1522737543681': 'Funder Name'}], 'subitem_1522399571623': {'subitem_1522399585738': 'Award URI', 'subitem_1522399628911': 'Award Number'}, 'subitem_1522399651758': [{'subitem_1522721910626': 'en', 'subitem_1522721929892': 'Award Title'}]}]}, 'item_1617186920753': {'attribute_name': 'Source Identifier', 'attribute_value_mlt': [{'subitem_1522646500366': 'ISSN', 'subitem_1522646572813': 'xxxx-xxxx-xxxx'}]}, 'item_1617186941041': {'attribute_name': 'Source Title', 'attribute_value_mlt': [{'subitem_1522650068558': 'en', 'subitem_1522650091861': 'Source Title'}]}, 'item_1617186959569': {'attribute_name': 'Volume Number', 'attribute_value_mlt': [{'subitem_1551256328147': '1'}]}, 'item_1617186981471': {'attribute_name': 'Issue Number', 'attribute_value_mlt': [{'subitem_1551256294723': '111'}]}, 'item_1617186994930': {'attribute_name': 'Number of Pages', 'attribute_value_mlt': [{'subitem_1551256248092': '12'}]}, 'item_1617187024783': {'attribute_name': 'Page Start', 'attribute_value_mlt': [{'subitem_1551256198917': '1'}]}, 'item_1617187045071': {'attribute_name': 'Page End', 'attribute_value_mlt': [{'subitem_1551256185532': '3'}]}, 'item_1617187112279': {'attribute_name': 'Degree Name', 'attribute_value_mlt': [{'subitem_1551256126428': 'Degree Name', 'subitem_1551256129013': 'en'}]}, 'item_1617187136212': {'attribute_name': 'Date Granted', 'attribute_value_mlt': [{'subitem_1551256096004': '2021-06-30'}]}, 'item_1617187187528': {'attribute_name': 'Conference', 'attribute_value_mlt': [{'subitem_1599711633003': [{'subitem_1599711636923': 'Conference Name', 'subitem_1599711645590': 'ja'}], 'subitem_1599711655652': '1', 'subitem_1599711660052': [{'subitem_1599711680082': 'Sponsor', 'subitem_1599711686511': 'ja'}], 'subitem_1599711699392': {'subitem_1599711704251': '2020/12/11', 'subitem_1599711712451': '1', 'subitem_1599711727603': '12', 'subitem_1599711731891': '2000', 'subitem_1599711735410': '1', 'subitem_1599711739022': '12', 'subitem_1599711743722': '2020', 'subitem_1599711745532': 'ja'}, 'subitem_1599711758470': [{'subitem_1599711769260': 'Conference Venue', 'subitem_1599711775943': 'ja'}], 'subitem_1599711788485': [{'subitem_1599711798761': 'Conference Place', 'subitem_1599711803382': 'ja'}], 'subitem_1599711813532': 'JPN'}]}, 'item_1617258105262': {'attribute_name': 'Resource Type', 'attribute_value_mlt': [{'resourceuri': 'http://purl.org/coar/resource_type/c_5794', 'resourcetype': 'conference paper'}]}, 'item_1617265215918': {'attribute_name': 'Version Type', 'attribute_value_mlt': [{'subitem_1522305645492': 'AO', 'subitem_1600292170262': 'http://purl.org/coar/version/c_b1a7d7d4d402bcce'}]}, 'item_1617349709064': {'attribute_name': 'Contributor', 'attribute_value_mlt': [{'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'contributorType': 'ContactPerson', 'nameIdentifiers': [{'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifierScheme': 'ORCID'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}], 'contributorMails': [{'contributorMail': 'wekosoftware@nii.ac.jp'}], 'contributorNames': [{'lang': 'ja', 'contributorName': '情報, 太郎'}, {'lang': 'ja-Kana', 'contributorName': 'ジョウホウ, タロウ'}, {'lang': 'en', 'contributorName': 'Joho, Taro'}]}]}, 'item_1617349808926': {'attribute_name': 'Version', 'attribute_value_mlt': [{'subitem_1523263171732': 'Version'}]}, 'item_1617351524846': {'attribute_name': 'APC', 'attribute_value_mlt': [{'subitem_1523260933860': 'Unknown'}]}, 'item_1617353299429': {'attribute_name': 'Relation', 'attribute_value_mlt': [{'subitem_1522306207484': 'isVersionOf', 'subitem_1522306287251': {'subitem_1522306382014': 'arXiv', 'subitem_1522306436033': 'xxxxx'}, 'subitem_1523320863692': [{'subitem_1523320867455': 'en', 'subitem_1523320909613': 'Related Title'}]}]}, 'item_1617605131499': {'attribute_name': 'File', 'attribute_type': 'file', 'attribute_value_mlt': [{'url': {'url': 'https://weko3.example.org/record/2.1/files/1KB.pdf'}, 'date': [{'dateType': 'Available', 'dateValue': '2021-07-12'}], 'format': 'text/plain', 'filename': '1KB.pdf', 'filesize': [{'value': '1 KB'}], 'mimetype': 'application/pdf', 'accessrole': 'open_access', 'version_id': '6f80e3cb-f681-45eb-bd54-b45be0f7d3ee', 'displaytype': 'simple'}]}, 'item_1617610673286': {'attribute_name': 'Rights Holder', 'attribute_value_mlt': [{'nameIdentifiers': [{'nameIdentifier': 'xxxxxx', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifierScheme': 'ORCID'}], 'rightHolderNames': [{'rightHolderName': 'Right Holder Name', 'rightHolderLanguage': 'ja'}]}]}, 'item_1617620223087': {'attribute_name': 'Heading', 'attribute_value_mlt': [{'subitem_1565671149650': 'ja', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheading'}, {'subitem_1565671149650': 'en', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheding'}]}, 'item_1617944105607': {'attribute_name': 'Degree Grantor', 'attribute_value_mlt': [{'subitem_1551256015892': [{'subitem_1551256027296': 'xxxxxx', 'subitem_1551256029891': 'kakenhi'}], 'subitem_1551256037922': [{'subitem_1551256042287': 'Degree Grantor Name', 'subitem_1551256047619': 'en'}]}]}, 'relation_version_is_last': True}
    b = {'pid': {'type': 'depid', 'value': '2.0', 'revision_id': 0}, 'lang': 'ja', 'owner': '1', 'title': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'owners': [1], 'status': 'published', '$schema': '15', 'pubdate': '2021-02-13', 'edit_mode': 'keep', 'created_by': 1, 'deleted_items': ['item_1617187056579', 'approval1', 'approval2'], 'shared_user_id': -1, 'weko_shared_id': -1, 'item_1617186331708': [{'subitem_1551255647225': 'ja_conference paperITEM00000002(public_open_access_open_access_simple)', 'subitem_1551255648112': 'ja'}, {'subitem_1551255647225': 'en_conference paperITEM00000002(public_open_access_simple)', 'subitem_1551255648112': 'en'}], 'item_1617186385884': [{'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'en'}, {'subitem_1551255720400': 'Alternative Title', 'subitem_1551255721061': 'ja'}], 'item_1617186419668': [{'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}]}, {'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'creatorMails': [{'creatorMail': 'wekosoftware@nii.ac.jp'}], 'creatorNames': [{'creatorName': '情報, 三郎', 'creatorNameLang': 'ja'}, {'creatorName': 'ジョウホウ, タロウ', 'creatorNameLang': 'ja-Kana'}, {'creatorName': 'Joho, Taro', 'creatorNameLang': 'en'}], 'nameIdentifiers': [{'nameIdentifier': '3', 'nameIdentifierScheme': 'WEKO'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'zzzzzzz', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}]}], 'item_1617186476635': {'subitem_1522299639480': 'open access', 'subitem_1600958577026': 'http://purl.org/coar/access_right/c_abf2'}, 'item_1617186499011': [{'subitem_1522650717957': 'ja', 'subitem_1522650727486': 'http://localhost', 'subitem_1522651041219': 'Rights Information'}], 'item_1617186609386': [{'subitem_1522299896455': 'ja', 'subitem_1522300014469': 'Other', 'subitem_1522300048512': 'http://localhost/', 'subitem_1523261968819': 'Sibject1'}], 'item_1617186626617': [{'subitem_description': 'Description\\nDescription<br/>Description&EMPTY&\\nDescription', 'subitem_description_type': 'Abstract', 'subitem_description_language': 'en'}, {'subitem_description': '概要\\n概要&EMPTY&\\n概要\\n概要', 'subitem_description_type': 'Abstract', 'subitem_description_language': 'ja'}], 'item_1617186643794': [{'subitem_1522300295150': 'en', 'subitem_1522300316516': 'Publisher'}], 'item_1617186660861': [{'subitem_1522300695726': 'Available', 'subitem_1522300722591': '2021-06-30'}], 'item_1617186702042': [{'subitem_1551255818386': 'jpn'}], 'item_1617186783814': [{'subitem_identifier_uri': 'http://localhost', 'subitem_identifier_type': 'URI'}], 'item_1617186859717': [{'subitem_1522658018441': 'en', 'subitem_1522658031721': 'Temporal'}], 'item_1617186882738': [{'subitem_geolocation_place': [{'subitem_geolocation_place_text': 'Japan'}]}], 'item_1617186901218': [{'subitem_1522399143519': {'subitem_1522399281603': 'ISNI', 'subitem_1522399333375': 'http://xxx'}, 'subitem_1522399412622': [{'subitem_1522399416691': 'en', 'subitem_1522737543681': 'Funder Name'}], 'subitem_1522399571623': {'subitem_1522399585738': 'Award URI', 'subitem_1522399628911': 'Award Number'}, 'subitem_1522399651758': [{'subitem_1522721910626': 'en', 'subitem_1522721929892': 'Award Title'}]}], 'item_1617186920753': [{'subitem_1522646500366': 'ISSN', 'subitem_1522646572813': 'xxxx-xxxx-xxxx'}], 'item_1617186941041': [{'subitem_1522650068558': 'en', 'subitem_1522650091861': 'Source Title'}], 'item_1617186959569': {'subitem_1551256328147': '1'}, 'item_1617186981471': {'subitem_1551256294723': '111'}, 'item_1617186994930': {'subitem_1551256248092': '12'}, 'item_1617187024783': {'subitem_1551256198917': '1'}, 'item_1617187045071': {'subitem_1551256185532': '3'}, 'item_1617187112279': [{'subitem_1551256126428': 'Degree Name', 'subitem_1551256129013': 'en'}], 'item_1617187136212': {'subitem_1551256096004': '2021-06-30'}, 'item_1617187187528': [{'subitem_1599711633003': [{'subitem_1599711636923': 'Conference Name', 'subitem_1599711645590': 'ja'}], 'subitem_1599711655652': '1', 'subitem_1599711660052': [{'subitem_1599711680082': 'Sponsor', 'subitem_1599711686511': 'ja'}], 'subitem_1599711699392': {'subitem_1599711704251': '2020/12/11', 'subitem_1599711712451': '1', 'subitem_1599711727603': '12', 'subitem_1599711731891': '2000', 'subitem_1599711735410': '1', 'subitem_1599711739022': '12', 'subitem_1599711743722': '2020', 'subitem_1599711745532': 'ja'}, 'subitem_1599711758470': [{'subitem_1599711769260': 'Conference Venue', 'subitem_1599711775943': 'ja'}], 'subitem_1599711788485': [{'subitem_1599711798761': 'Conference Place', 'subitem_1599711803382': 'ja'}], 'subitem_1599711813532': 'JPN'}], 'item_1617258105262': {'resourceuri': 'http://purl.org/coar/resource_type/c_5794', 'resourcetype': 'conference paper'}, 'item_1617265215918': {'subitem_1522305645492': 'AO', 'subitem_1600292170262': 'http://purl.org/coar/version/c_b1a7d7d4d402bcce'}, 'item_1617349709064': [{'givenNames': [{'givenName': '太郎', 'givenNameLang': 'ja'}, {'givenName': 'タロウ', 'givenNameLang': 'ja-Kana'}, {'givenName': 'Taro', 'givenNameLang': 'en'}], 'familyNames': [{'familyName': '情報', 'familyNameLang': 'ja'}, {'familyName': 'ジョウホウ', 'familyNameLang': 'ja-Kana'}, {'familyName': 'Joho', 'familyNameLang': 'en'}], 'contributorType': 'ContactPerson', 'nameIdentifiers': [{'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifierScheme': 'ORCID'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://ci.nii.ac.jp/', 'nameIdentifierScheme': 'CiNii'}, {'nameIdentifier': 'xxxxxxx', 'nameIdentifierURI': 'https://kaken.nii.ac.jp/', 'nameIdentifierScheme': 'KAKEN2'}], 'contributorMails': [{'contributorMail': 'wekosoftware@nii.ac.jp'}], 'contributorNames': [{'lang': 'ja', 'contributorName': '情報, 太郎'}, {'lang': 'ja-Kana', 'contributorName': 'ジョウホウ, タロウ'}, {'lang': 'en', 'contributorName': 'Joho, Taro'}]}], 'item_1617349808926': {'subitem_1523263171732': 'Version'}, 'item_1617351524846': {'subitem_1523260933860': 'Unknown'}, 'item_1617353299429': [{'subitem_1522306207484': 'isVersionOf', 'subitem_1522306287251': {'subitem_1522306382014': 'arXiv', 'subitem_1522306436033': 'xxxxx'}, 'subitem_1523320863692': [{'subitem_1523320867455': 'en', 'subitem_1523320909613': 'Related Title'}]}], 'item_1617605131499': [{'url': {'url': 'https://weko3.example.org/record/2/files/1KB.pdf'}, 'date': [{'dateType': 'Available', 'dateValue': '2021-07-12'}], 'format': 'text/plain', 'filename': '1KB.pdf', 'filesize': [{'value': '1 KB'}], 'mimetype': 'application/pdf', 'accessrole': 'open_access', 'version_id': 'c92410f6-ed23-4d2e-a8c5-0b3b06cc79c8', 'displaytype': 'simple'}], 'item_1617610673286': [{'nameIdentifiers': [{'nameIdentifier': 'xxxxxx', 'nameIdentifierURI': 'https://orcid.org/', 'nameIdentifierScheme': 'ORCID'}], 'rightHolderNames': [{'rightHolderName': 'Right Holder Name', 'rightHolderLanguage': 'ja'}]}], 'item_1617620223087': [{'subitem_1565671149650': 'ja', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheading'}, {'subitem_1565671149650': 'en', 'subitem_1565671169640': 'Banner Headline', 'subitem_1565671178623': 'Subheding'}], 'item_1617944105607': [{'subitem_1551256015892': [{'subitem_1551256027296': 'xxxxxx', 'subitem_1551256029891': 'kakenhi'}], 'subitem_1551256037922': [{'subitem_1551256042287': 'Degree Grantor Name', 'subitem_1551256047619': 'en'}]}]}
    # deposit = WekoDeposit.create(a)
    # print("deposit: {}".format(deposit))