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

"""Weko Authors API."""
import json
from copy import deepcopy

from invenio_db import db

from weko_authors.config import WEKO_AUTHORS_TSV_MAPPING

from .models import Authors, AuthorsPrefixSettings


class WekoAuthors(object):
    """Weko Authors API for import/export."""

    @classmethod
    def get_all(cls, with_deleted=True, with_gather=True):
        """Get all authors."""
        filters = []
        with db.session.no_autoflush:
            if not with_deleted:
                filters.append(Authors.is_deleted.is_(False))
            if not with_gather:
                filters.append(Authors.gather_flg == 0)
            query = Authors.query.filter(*filters)
            query = query.order_by(Authors.id)

            return query.all()

    @classmethod
    def get_identifier_scheme_info(cls):
        """Get all Identifier Scheme informations."""
        result = {}
        with db.session.no_autoflush:
            schemes = AuthorsPrefixSettings.query.order_by(
                AuthorsPrefixSettings.id).all()
            if schemes:
                for scheme in schemes:
                    result[str(scheme.id)] = dict(
                        scheme=scheme.scheme, url=scheme.url)

        return result

    @classmethod
    def prepare_export_data(cls, mappings, authors, schemes):
        """Prepare export data of all authors."""
        row_header = []
        row_label_en = []
        row_label_jp = []
        row_data = []

        if not mappings:
            mappings = deepcopy(WEKO_AUTHORS_TSV_MAPPING)
        if not authors:
            authors = cls.get_all(with_deleted=False, with_gather=False)
        if not schemes:
            schemes = cls.get_identifier_scheme_info()

        # calc max item of multiple case and prepare header, label
        for mapping in mappings:
            if mapping.get('child'):
                if not authors:
                    mapping['max'] = 1
                else:
                    mapping['max'] = max(
                        list(map(lambda x: len(json.loads(x.json).get(
                            mapping['json_id'], [])), authors))
                    )
                    if mapping['max'] == 0:
                        mapping['max'] = 1
                if authors and mapping['json_id'] == 'authorIdInfo':
                    if mapping['max'] > 1:
                        mapping['max'] -= 1

                for i in range(0, mapping['max']):
                    for child in mapping.get('child'):
                        row_header.append('{}[{}].{}'.format(
                            mapping['json_id'], i, child['json_id']))
                        row_label_en.append(
                            '{}[{}]'.format(child['label_en'], i))
                        row_label_jp.append(
                            '{}[{}]'.format(child['label_jp'], i))
            else:
                row_header.append(mapping['json_id'])
                row_label_en.append(mapping['label_en'])
                row_label_jp.append(mapping['label_jp'])
        row_header[0] = '#' + row_header[0]
        row_label_en[0] = '#' + row_label_en[0]
        row_label_jp[0] = '#' + row_label_jp[0]

        # handle data rows
        for author in authors:
            json_data = json.loads(author.json)
            row = []
            for mapping in mappings:
                if mapping.get('child'):
                    data = json_data.get(mapping['json_id'])
                    idx_start = 0
                    idx_size = mapping['max']
                    # ignore WEKO id
                    if mapping['json_id'] == 'authorIdInfo':
                        idx_start = 1
                        idx_size += 1

                    for i in range(idx_start, idx_size):
                        for child in mapping.get('child'):
                            if i >= len(data):
                                row.append(None)
                            elif 'mask' in child:
                                row.append(
                                    child['mask'].get(
                                        str(data[i].get(
                                            child['json_id'])).lower(),
                                        None
                                    )
                                )
                            else:
                                val = data[i].get(child['json_id'])
                                if child['json_id'] == 'idType':
                                    scheme = schemes.get(val)
                                    row.append(
                                        scheme['scheme'] if scheme else val)
                                else:
                                    row.append(val)
                else:
                    try:
                        if 'mask' in mapping:
                            row.append(
                                mapping['mask'].get(
                                    str(json_data.get(
                                        mapping['json_id'])).lower(),
                                    None
                                )
                            )
                        else:
                            row.append(json_data.get(mapping['json_id']))
                    except KeyError as ex:
                        row.append(None)
            row_data.append(row)

        return row_header, row_label_en, row_label_jp, row_data