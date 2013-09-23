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
from simplenet.common.config import get_logger
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotImplemented, EntityNotFound,
    OperationNotPermited
)
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()

class Net(SimpleNet):

    def switch_list(self):
        return self._generic_list_("switches", models.Switch)

    def switch_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(models.Switch(name=data['name'], mac=data['mac'],
                                    address=data['address'], model_type=data['model_type']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Switch', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)

        return self.switch_info_by_name(data['name'])

    def switch_info(self, id):
        return self._generic_info_("switch", models.Switch, {'id': id})


    def switch_info_by_name(self, name):
        return self._generic_info_(
            "switch", models.Switch, {'name': name}
        )

    def switch_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def switch_delete(self, id):
        return self._generic_delete_("switch", models.Switch, {'id': id})

    def switch_add_interface(self, switch_id, data):
        logger.debug("Adding interface using data: %s" % data)

        interface = session.query(models.Interface).get(data['interface_id'])

        if not interface:
            raise EntityNotFound('Interface', data['interface_id'])

        if interface.switch_id:
            raise Exception("Interface already attached")

        session.begin(subtransactions=True)
        try:
            interface.switch_id = switch_id
            interface.name = data['int_name']
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        _data = interface.tree_dict()
        logger.debug("Successful adding Interface to Switch status: %s" % _data)
        _data['action'] = "plug"
        _data['ofport'] = data['ofport']
        event.EventManager().raise_event(_data['switch_id']['name'], _data)

        return _data

    def switch_remove_interface(self, switch_id, int_id):
        interface = session.query(models.Interface).get(int_id)
        if not interface:
            raise EntityNotFound('Interface', int_id)

        if not interface.switch_id:
            return
        elif interface.switch_id == switch_id:
            _data = interface.tree_dict()
            session.begin(subtransactions=True)
            try:
                interface.switch_id = None
                session.commit()
            except Exception, e:
                session.rollback()
                raise Exception(e)

            _data['action'] = "unplug"
            event.EventManager().raise_event(_data['switch_id']['name'], _data)

            return _data
        else:
            raise Exception("Interface not plugged into the switch")
