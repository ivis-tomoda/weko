# -*- coding: utf-8 -*-

from collections import OrderedDict

import pytest

from weko_records.utils import copy_value_json_path, copy_values_json_path


@pytest.fixture
def jsonpath():
    return ['$.item_1551264418667.attribute_value_mlt[*].subitem_1551257245638[*].subitem_1551257276108', '$.item_1551265302120.attribute_value_mlt[*].subitem_1551256918211']


@pytest.fixture
def meta():
    return OrderedDict(
        [('pubdate', {'attribute_name': 'PubDate', 'attribute_value': '2021-10-26'}),
         ('item_1551264308487', {'attribute_name': 'Title', 'attribute_value_mlt': [
             {'subitem_1551255647225': 'タイトル日本語', 'subitem_1551255648112': 'ja'},
             {'subitem_1551255647225': 'Title', 'subitem_1551255648112': 'en'}]}),
         ('item_1551264340087', {'attribute_name': 'Creator', 'attribute_value_mlt':
                                 [{'subitem_1551255898956': [{'subitem_1551255905565': '作者', 'subitem_1551255907416': 'ja'}]}]}),
         ('item_1551264447183', {'attribute_name': 'Access Rights', 'attribute_value_mlt':
                                 [{'subitem_1551257553743': 'open access', 'subitem_1551257578398': 'http://purl.org/coar/access_right/c_abf2'}]}),
         ('item_1551264418667', {'attribute_name': 'Contributor', 'attribute_value_mlt':
                                 [{'subitem_1551257036415': 'Distributor', 'subitem_1551257339190':
                                   [{'subitem_1551257342360': ''}], 'subitem_1551257245638':
                                   [{'subitem_1551257276108': '寄与者', 'subitem_1551257279831': 'ja'},
                                    {'subitem_1551257276108': 'Contributor', 'subitem_1551257279831': 'en'}]}]}),
         ('item_1551264822581', {'attribute_name': 'Subject', 'attribute_value_mlt':
                                 [{'subitem_1551257315453': '日本史', 'subitem_1551257323812': 'ja', 'subitem_1551257329877': 'NDC'},
                                  {'subitem_1551257315453': 'General History of Japan', 'subitem_1551257323812': 'en',
                                   'subitem_1551257329877': 'NDC'}]}), ('item_1551265227803',
                                                                        {'attribute_name': 'Relation', 'attribute_value_mlt':
                                                                         [{'subitem_1551256388439': 'references', 'subitem_1551256465077':
                                                                           [{'subitem_1551256478339': 'localid', 'subitem_1551256629524': 'Local'}]}]}),
         ('item_1551264974654', {'attribute_name': 'Date', 'attribute_value_mlt':
                                 [{'subitem_1551255753471': '2000-01-01'}, {'subitem_1551255753471': '2012-06-11'},
                                  {'subitem_1551255753471': '2016-05-24'}]}),
         ('item_1551264846237', {'attribute_name': 'Description', 'attribute_value_mlt':
                                 [{'subitem_1551255577890': '概要', 'subitem_1551255592625': 'ja', 'subitem_1551255637472': 'Abstract'},
                                  {'subitem_1551255577890': 'その他', 'subitem_1551255592625': 'ja',
                                      'subitem_1551255637472': 'Other'},
                                  {'subitem_1551255577890': 'materials: text', 'subitem_1551255592625': 'en', 'subitem_1551255637472': 'Other'}]}),
         ('item_1551265002099', {'attribute_name': 'Language', 'attribute_value_mlt': [
          {'subitem_1551255818386': 'jpn'}]}),
         ('item_1551265032053', {'attribute_name': 'Resource Type', 'attribute_value_mlt':
                                 [{'resourcetype': 'manuscript', 'resourceuri': 'http://purl.org/coar/resource_type/c_0040'}]}),
         ('item_1551265302120', {'attribute_name': 'Temporal', 'attribute_value_mlt': [
          {'subitem_1551256918211': '2000-01-01/2021-03-30'}]}),
         ('item_title', 'タイトル日本語'),
         ('item_type_id', '12'), ('control_number', '870')])


def test_copy_value_json_path(meta, jsonpath):
    assert copy_value_json_path(meta, jsonpath[0]) == '寄与者'
    assert copy_value_json_path(meta, jsonpath[1]) == '2000-01-01/2021-03-30'


def test_copy_values_json_path(meta, jsonpath):
    assert copy_values_json_path(meta, jsonpath[0]) == [
        '寄与者', 'Contributor']
    assert copy_values_json_path(meta, jsonpath[1]) == [
        '2000-01-01/2021-03-30']
