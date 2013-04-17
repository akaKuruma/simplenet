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

from simplenet.common import event
from simplenet.common.config import config, get_logger
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotImplemented, EntityNotFound,
    OperationNotPermited, FeatureNotAvailable
)
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()

class Net(SimpleNet):

    def _enqueue_rules_(self, owner_type, owner_id):
        logger.debug("Getting rules from %s with id %s" % (owner_type, owner_id))
        policy_list = []
        _get_data = getattr(self, "_get_data_%s_" % owner_type)
        _data = _get_data(owner_id)

        if (owner_type != 'zone') and ('vlan_id' in _data):
            logger.debug("Getting devices by vlan %s" % _data['vlan_id'])
            devices = self.device_list_by_vlan(_data['vlan_id'])
        elif ('anycast_id' in _data):
            logger.debug("Getting devices by anycast %s" % _data['anycast_id'])
            devices = self.device_list_by_anycast(_data['anycast_id'])
        else:
            logger.debug("Getting devices by anycast %s" % _data['zone_id'])
            devices = self.device_list_by_zone(_data['zone_id'])

        for device in devices:
            logger.debug("Getting data from device %s" % device['id'])
            zone_id = device['zone_id']
            dev_id = device['device_id'] if (owner_type != 'zone') else device['id']

            policy_list = policy_list + self.policy_list_by_owner('zone', zone_id)
            _data.update({'policy': self.policy_list_by_owner('zone', zone_id)})
            for vlan in self.vlan_list_by_device(dev_id): # Cascade thru the vlans of the device
                logger.debug("Getting policy data from subnet %s" % vlan)
                policy_list = policy_list + self.policy_list_by_owner('vlan', vlan['vlan_id'])
                for subnet in self.subnet_list_by_vlan(vlan['vlan_id']): # Cascade thru the subnets of the vlan
                    logger.debug("Getting policy data from vlan %s" % subnet)
                    policy_list = policy_list + self.policy_list_by_owner('subnet', subnet['id'])
                    for ip in self.ip_list_by_subnet(subnet['id']): # Cascade thru the IPs of the subnet
                        logger.debug("Getting policy data from ip %s" % ip)
                        policy_list = policy_list + self.policy_list_by_owner('ip', ip['id'])

            for anycast in self.anycast_list_by_device(dev_id): # Cascade thru the anycasts of the device
                logger.debug("Getting policy data from anycast %s" % anycast)
                policy_list = policy_list + self.policy_list_by_owner('anycast', anycast['anycast_id'])
                for anycastip in self.anycastip_list_by_anycast(anycast['anycast_id']): # Cascade thru the IPs of the anycast subnet
                    logger.debug("Getting policy data from anycasip %s" % anycastip)
                    policy_list = policy_list + self.policy_list_by_owner('anycastip', anycastip['id'])

            _data.update({'policy': policy_list})
            logger.debug("Received rules: %s from %s with id %s and device %s" % (
                _data, owner_type, id, device['name'])
            )
            if policy_list:
                event.EventManager().raise_event(device['name'], _data)

    def policy_list(self, owner_type):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_list_("%sPolicy" % owner_type.capitalize(), _model)

    def policy_create(self, owner_type, owner_id, data):
        logger.debug("Creating rule on %s: %s using data: %s" %
            (owner_type, owner_id, data)
        )
        data.update({'owner_id': owner_id})
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        policy = _model(**data)
        session.begin(subtransactions=True)
        try:
            session.add(policy)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Created rule %s on %s: %s using data: %s" %
            (policy.id, owner_type, owner_id, data)
        )
        self._enqueue_rules_(owner_type, owner_id)
        return self.policy_info(owner_type, policy.id)

    def policy_info(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_info_("%sPolicy" % owner_type.capitalize(), _model, {'id': id})

    def policy_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_delete(self, owner_type, id):
        logger.debug("Deleting policy %s" % id)
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).get(id)
        if not ss:
            raise EntityNotFound('%sPolicy' % owner_type.capitalize(), id)
        owner_id = ss.owner_id
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Successful deletion of policy %s" % id)
        self._enqueue_rules_(owner_type, owner_id)
        return True

    def policy_list_by_owner(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_list_by_something_(
            "%sPolicy" % owner_type.capitalize(), _model, {'owner_id': id}
        )