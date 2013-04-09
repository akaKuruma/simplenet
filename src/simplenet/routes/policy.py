# Copyright 2012 Locaweb.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @author: Juliano Martinez (ncode), Locaweb.
# @author: Luiz Ozaki, Locaweb.

import json

from bottle import delete, put, get, post
from bottle import abort, request, response

from simplenet.common.auth import handle_auth
from simplenet.common.config import config, get_rolesdb
from simplenet.common.http_utils import (
    reply_json, create_manager
)

logger = get_logger()

cas_endpoint = config.get("authentication", "cas_endpoint")
cas_sys_endpoint = config.get("authentication", "cas_sys_endpoint")
cas_service  = config.get("authentication", "cas_service")


@handle_auth
@get('/<network_appliance>/policy/<owner_type>/<policy_id>/info')
@reply_json
def policy_info(network_appliance, owner_type, policy_id):
    """
    ::

      GET /<network_appliance>/policy/<owner_type>/<policy_id>/info

    Get policy informations
    """
    manager = create_manager(network_appliance)
    return manager.policy_info(owner_type, policy_id)


@handle_auth
@post('/<network_appliance>/policy/<owner_type>/<owner_id>')
@reply_json
def policy_create(network_appliance, owner_type, owner_id):
    """
    ::

      POST /<network_appliance>/policy/<owner_type>/<owner_id>

    Create a new policy
    """
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    policy = manager.policy_create(owner_type, owner_id, data)
    location = "%s/policy/%s/%s" % (network_appliance, owner_type, policy['id'])
    response.set_header("Location", location)
    return policy


@handle_auth
@delete('/<network_appliance>/policy/<owner_type>/<policy_id>/delete')
@reply_json
def policy_delete(network_appliance, owner_type, policy_id):
    """
    ::

      DELETE /<network_appliance>/policy/<owner_type>/<policy_id>/delete

    Deletes policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_delete(owner_type, policy_id)


@handle_auth
@get('/<network_appliance>/policy/by-type/<owner_type>/list')
@reply_json
def policy_list(network_appliance, owner_type):
    """
    ::

      GET /<network_appliance>/policy/<owner_type>/list

    Get all policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_list(owner_type)


@handle_auth
@get('/<network_appliance>/policy/by-owner/<owner_type>/<owner_id>/list')
@reply_json
def policy_list_by_owner(network_appliance, owner_type, owner_id):
    """
    ::

      GET /<network_appliance>/policy/by-owner/<owner_type>/<owner_id>/list

    Get all policy from a given owner
    """
    manager = create_manager(network_appliance)
    return manager.policy_list_by_owner(owner_type, owner_id)
