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

"""Blueprint for schema rest."""

import inspect

from flask import Blueprint, current_app, jsonify, make_response, request, abort, Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from invenio_db import db
from invenio_oauth2server import require_api_auth, require_oauth_scopes
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.links import default_links_factory
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import \
    create_error_handlers as records_rest_error_handlers
from invenio_rest import ContentNegotiatedMethodView
from invenio_rest.views import create_api_errorhandler
from weko_deposit.api import WekoRecord
from weko_records.serializers import citeproc_v1

from .errors import VersionNotFoundRESTError
from .scopes import item_read_scope
from .views import escape_str

WEKO_RECORDS_UI_API_LIMIT_RATE_DEFAULT = ['100 per minute']

limiter = Limiter(app=Flask(__name__), key_func=get_remote_address, default_limits=WEKO_RECORDS_UI_API_LIMIT_RATE_DEFAULT)


def create_error_handlers(blueprint):
    """Create error handlers on blueprint."""
    blueprint.errorhandler(PIDInvalidAction)(create_api_errorhandler(
        status=403, message='Invalid action'
    ))
    records_rest_error_handlers(blueprint)


def create_blueprint(endpoints):
    """
    Create Weko-Records-ui-REST blueprint.
    See: :data:`weko_records_ui.config.WEKO_RECORDS_UI_REST_ENDPOINTS`.

    :param endpoints: List of endpoints configuration.
    :returns: The configured blueprint.
    """
    blueprint = Blueprint(
        'weko_records_ui_rest',
        __name__,
        url_prefix='',
    )

    @blueprint.teardown_request
    def dbsession_clean(exception):
        current_app.logger.debug("weko_records_ui dbsession_clean: {}".format(exception))
        if exception is None:
            try:
                db.session.commit()
            except:
                db.session.rollback()
        db.session.remove()

    for endpoint, options in (endpoints or {}).items():
        if endpoint == 'need_restricted_access':
            view_func = NeedRestrictedAccess.as_view(
                NeedRestrictedAccess.view_name.format(endpoint),
                default_media_type=options.get('default_media_type'),
            )
            blueprint.add_url_rule(
                options.get('route'),
                view_func=view_func,
                methods=['GET'],
            )

    return blueprint


def create_blueprint_cites(endpoints):
    """Create Weko-Records-UI-Cites-REST blueprint.

    See: :data:`invenio_deposit.config.DEPOSIT_REST_ENDPOINTS`.

    :param endpoints: List of endpoints configuration.
    :returns: The configured blueprint.
    """
    blueprint = Blueprint(
        'weko_records_ui_cites_rest',
        __name__,
        url_prefix='',
    )

    @blueprint.teardown_request
    def dbsession_clean(exception):
        current_app.logger.debug("weko_records_ui dbsession_clean: {}".format(exception))
        if exception is None:
            try:
                db.session.commit()
            except:
                db.session.rollback()
        db.session.remove()

    create_error_handlers(blueprint)

    for endpoint, options in (endpoints or {}).items():

        if 'record_serializers' in options:
            serializers = options.get('record_serializers')
            serializers = {mime: obj_or_import_string(func)
                           for mime, func in serializers.items()}
        else:
            serializers = {}

        record_class = obj_or_import_string(options['record_class'])

        ctx = dict(
            read_permission_factory=obj_or_import_string(
                options.get('read_permission_factory_imp')
            ),
            record_class=record_class,
            links_factory=obj_or_import_string(
                options.get('links_factory_imp'),
                default=default_links_factory
            ),
            # pid_type=options.get('pid_type'),
            # pid_minter=options.get('pid_minter'),
            # pid_fetcher=options.get('pid_fetcher'),
            loaders={
                options.get('default_media_type'): lambda: request.get_json()},
            default_media_type=options.get('default_media_type'),
        )

        cites = WekoRecordsCitesResource.as_view(
            WekoRecordsCitesResource.view_name.format(endpoint),
            serializers=serializers,
            # pid_type=options['pid_type'],
            ctx=ctx,
            default_media_type=options.get('default_media_type'),
        )
        blueprint.add_url_rule(
            options.get('cites_route'),
            view_func=cites,
            methods=['GET'],
        )

    return blueprint


class NeedRestrictedAccess(ContentNegotiatedMethodView):
    view_name = 'records_ui_{0}'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(NeedRestrictedAccess, self).__init__(*args, **kwargs)

    @require_api_auth(True)
    @require_oauth_scopes(item_read_scope.id)
    @limiter.limit('')
    def get(self, **kwargs):
        """
        Check if need restricted access.

        Returns:
            Result for each file.
        """
        version = kwargs.get('version')
        func_name = f'get_{version}'
        if func_name in [func[0] for func in inspect.getmembers(self, inspect.ismethod)]:
            return getattr(self, func_name)(**kwargs)
        else:
            raise VersionNotFoundRESTError()

    def get_v1(self, **kwargs):
        # Get record
        pid_value = kwargs.get('pid_value')
        record = self.__get_record(pid_value)
        if record is None:
            abort(404)

        # Get files
        from .utils import get_file_info_list
        _, files = get_file_info_list(record)

        res_json = []
        for file in files:
            # Check if file is restricted access.
            from .permissions import check_file_download_permission, check_content_clickable
            access_permission = check_file_download_permission(record, file)
            applicable = check_content_clickable(record, file)
            need_restricted_access = not access_permission and applicable

            # Create response
            res_json.append({
                'need_restricted_access': need_restricted_access,
                'filename': file.get('filename')
            })

        response = make_response(jsonify(res_json), 200)
        return response

    def __get_record(self, pid_value):
        record = None
        try:
            pid = PersistentIdentifier.get('recid', pid_value)

            # Get latest PID.
            from weko_deposit.pidstore import get_record_without_version
            pid_without_version = get_record_without_version(pid)
            latest_pid = PIDVersioning(child=pid_without_version).last_child

            # Check if activity is completed.
            from weko_workflow.api import WorkActivity
            from weko_workflow.models import ActivityStatusPolicy
            activity = WorkActivity().get_workflow_activity_by_item_id(latest_pid.object_uuid)
            if activity.activity_status != ActivityStatusPolicy.ACTIVITY_FINALLY:
                return None

            # Get record.
            record = WekoRecord.get_record(pid.object_uuid)
        except:
            return None

        return record


class WekoRecordsCitesResource(ContentNegotiatedMethodView):
    """Schema files resource."""

    view_name = '{0}_cites'

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super(WekoRecordsCitesResource, self).__init__(
            serializers,
            *args,
            **kwargs
        )
        for key, value in ctx.items():
            setattr(self, key, value)

    # @pass_record
    # @need_record_permission('read_permission_factory')
    def get(self, pid_value, **kwargs):
        """Render citation for record according to style and language."""
        style = request.values.get('style', 1)  # style or 'science'
        locale = request.values.get('locale', 2)
        try:
            pid = PersistentIdentifier.get('depid', pid_value)
            record = WekoRecord.get_record(pid.object_uuid)
            result = citeproc_v1.serialize(pid, record, style=style,
                                           locale=locale)
            result = escape_str(result)
            return make_response(jsonify(result), 200)
        except Exception:
            current_app.logger.exception(
                'Citation formatting for record {0} failed.'.format(
                    str(record.id)))
            return make_response(jsonify("Not found"), 404)
