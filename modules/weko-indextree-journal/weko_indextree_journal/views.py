# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 National Institute of Informatics.
#
# WEKO-Indextree-Journal is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module of weko-indextree-journal."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from __future__ import absolute_import, print_function
import sys

from flask import (
    Blueprint, render_template, render_template_string, current_app, json, abort, jsonify)
from flask_login import login_required
from invenio_i18n.ext import current_i18n
from flask_babelex import gettext as _
from weko_records.api import ItemTypes
from weko_groups.api import Group

from .permissions import indextree_journal_permission

blueprint = Blueprint(
    'weko_indextree_journal',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/indextree/journal',
)


@blueprint.route("/")
def index():
    """Render a basic view."""
    return render_template(
        current_app.config['WEKO_INDEXTREE_JOURNAL_INDEX_TEMPLATE'],
        get_tree_json=current_app.config['WEKO_INDEX_TREE_LIST_API'],
        upt_tree_json='',
        mod_tree_detail=current_app.config['WEKO_INDEX_TREE_API'],
        mod_journal_detail=current_app.config['WEKO_INDEXTREE_JOURNAL_API'],
    )


@blueprint.route("/right-content/<string:index_id>", methods=['GET'])
def get_journal_content(index_id=None):
    """Render a content of journal."""
    item_type_id = 19 # item tpye's journal = 21
    lists = ItemTypes.get_latest()
    if lists is None or len(lists) == 0:
        return render_template(
            current_app.config['WEKO_ITEMS_UI_ERROR_TEMPLATE']
        )
    item_type = ItemTypes.get_by_id(item_type_id)
    if item_type is None:
        return
    json_schema = '/indextree/journal/jsonschema/{}'.format(item_type_id)
    schema_form = '/indextree/journal/schemaform/{}'.format(item_type_id)

    # return render_template(
    #     current_app.config['WEKO_INDEXTREE_JOURNAL_CONTENT_TEMPLATE'],
    #     record=None,
    #     jsonschema=json_schema,
    #     schemaform=schema_form,
    #     lists=lists,
    #     links=None,
    #     id=item_type_id,
    #     files=None,
    #     pid=None
    # )
    return render_template_string(
    """
        <div class="hide" id="cur_index_id">{{index_id}}</div>
        <div class="row">
        <div class="col-sm-3 col-md-3 col-lg-3 m-top-20">
            <app-root-tree-hensyu></app-root-tree-hensyu>
        </div>
        <div class="col-sm-8 col-md-8 col-lg-8 m-top-20">
            <div class="row">
            <div id="item_management"class="hide">indextree</div>
            <div role="navigation">
                <ul class="nav nav-tabs">
                <li role="presentation">
                    <a data-show-tab="display">{{_('Index Edit')}}</a></li>
                <li role="presentation" class="active activity_li">
                    <a class="active activity_li" data-show-tab="display">{{_('Journal')}}</a></li>
                </ul>
            </div>
            <br>
            <div class="panel panel-default">
                <div class="panel-heading clearfix">
                <span class="panel-title">
                    {{_('Journal')}}
                </span>
                </div>
                <div class="panel-body">
                <div id="weko-records">
                    <invenio-records
                    {%- if pid %}
                        initialization="{{ config.DEPOSIT_RECORDS_EDIT_API.format(pid_value=pid.pid_value) }}"
                        links='{{links|tojson}}'
                    {%- else %}
                        initialization="{{ config.DEPOSIT_SEARCH_API }}"
                    {%- endif %}
                    response-params='{{ config.DEPOSIT_RESPONSE_MESSAGES | tojson }}'
                    extra-params='{"headers":{"Content-Type": "application/json"}}'
                    form="{{ schemaform }}"
                    record='{{ record | tojson }}'
                    schema="{{ jsonschema }}">
                    <invenio-records-loading
                        template="{{ url_for('static', filename='node_modules/invenio-records-js/dist/templates/loading.html') }}">
                    </invenio-records-loading>
                    <invenio-records-alert
                        template="{{ url_for('static', filename='node_modules/invenio-records-js/dist/templates/alert.html') }}">
                    </invenio-records-alert>
                    <invenio-records-form
                        form-templates='{{ config.DEPOSIT_FORM_TEMPLATES | tojson }}'
                        form-templates-base="{{ url_for('static', filename=config.DEPOSIT_FORM_TEMPLATES_BASE) }}"
                        template="{{ url_for('static', filename=config.DEPOSIT_UI_JSTEMPLATE_FORM) }}">
                    </invenio-records-form>
                    </invenio-records>
                </div>
                </div>
                <div class="panel-footer">
                <button id="index-detail-submit" class="btn btn-info" (click)="">{{_('Save')}}</button>
                </div>
            </div>
            </div>
        </div>
        </div>
    """
    )


@blueprint.route('/jsonschema/<int:item_type_id>', methods=['GET'])
@login_required
# @item_permission.require(http_exception=403)
def get_json_schema(item_type_id=0):
    """Get json schema.

    :param item_type_id: Item type ID. (Default: 0)
    :return: The json object.
    """
    try:
        result = None
        if item_type_id > 0:
            result = ItemTypes.get_record(item_type_id)
            if 'filemeta' in json.dumps(result):
                group_list = Group.get_group_list()
                group_enum = list(group_list.keys())
                filemeta_group = result.get('properties').get('filemeta').get(
                    'items').get('properties').get('groups')
                filemeta_group['enum'] = group_enum
        if result is None:
            return '{}'
        return jsonify(result)
    except:
        current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
    return abort(400)


@blueprint.route('/schemaform/<int:item_type_id>', methods=['GET'])
@login_required
# @item_permission.require(http_exception=403)
def get_schema_form(item_type_id=0):
    """Get schema form.

    :param item_type_id: Item type ID. (Default: 0)
    :return: The json object.
    """
    try:
        # cur_lang = 'default'
        # if current_app.config['I18N_SESSION_KEY'] in session:
        #     cur_lang = session[current_app.config['I18N_SESSION_KEY']]
        cur_lang = current_i18n.language
        result = None
        if item_type_id > 0:
            result = ItemTypes.get_by_id(item_type_id)
        if result is None:
            return '["*"]'
        schema_form = result.form
        filemeta_form = schema_form[0]
        if 'filemeta' == filemeta_form.get('key'):
            group_list = Group.get_group_list()
            filemeta_form_group = filemeta_form.get('items')[-1]
            filemeta_form_group['type'] = 'select'
            filemeta_form_group['titleMap'] = group_list
        if 'default' != cur_lang:
            for elem in schema_form:
                if 'title_i18n' in elem:
                    if cur_lang in elem['title_i18n']:
                        if len(elem['title_i18n'][cur_lang]) > 0:
                            elem['title'] = elem['title_i18n'][cur_lang]
                if 'items' in elem:
                    for sub_elem in elem['items']:
                        if 'title_i18n' in sub_elem:
                            if cur_lang in sub_elem['title_i18n']:
                                if len(sub_elem['title_i18n'][cur_lang]) > 0:
                                    sub_elem['title'] = sub_elem['title_i18n'][
                                        cur_lang]
        return jsonify(schema_form)
    except:
        current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
    return abort(400)