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
# @author: Thiago Morello (morellon), Locaweb.
# @author: Willian Molinari (PotHix), Locaweb.
# @author: Juliano Martinez (ncode), Locaweb.

from bottle import HTTPError

class SimpleNetError(HTTPError):
    def __init__(self, code, message):
        super(SimpleNetError, self).__init__(
            code, None, None, None, {"Content-Type": "application/json"}
        )
        self.output = {
            "error": self.__class__.__name__,
            "message": message
        }


class FeatureNotAvailable(SimpleNetError):
    def __init__(self):
        simplenet_error = super(FeatureNotAvailable, self)
        simplenet_error.__init__(
            501, "The selected network_appliance doesn't implement this feature"
        )


class EntityNotFound(SimpleNetError):
    def __init__(self, entity_type, entity_id):
        simplenet_error = super(EntityNotFound, self)
        simplenet_error.__init__(
            404, "%s:%s not found" % (entity_type, entity_id)
        )


class OperationNotPermited(SimpleNetError):
    def __init__(self, forbidden_type, forbidden_id):
        simplenet_error = super(OperationNotPermited, self)
        simplenet_error.__init__(
            403, "%s:%s Forbidden" % (forbidden_type, forbidden_id)
        )


class OperationFailed(SimpleNetError):
    def __init__(self, msg):
        simplenet_error = super(OperationFailed, self)
        simplenet_error.__init__(
            500, msg
        )


class DuplicatedEntryError(SimpleNetError):
    def __init__(self, forbidden_type, forbidden_id):
        simplenet_error = super(DuplicatedEntryError, self)
        simplenet_error.__init__(
            403, "%s:%s Duplicated" % (forbidden_type, forbidden_id)
        )
