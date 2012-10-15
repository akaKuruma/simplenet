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

import uuid

from ipaddr import IPv4Network, IPv4Address, IPv6Network, IPv6Address

from sqlalchemy import event, Column, String, create_engine, ForeignKey, Table, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from simplenet.common.config import config

Base = declarative_base()

class Datacenter(Base):

    __tablename__ = 'datacenters'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))

    def __init__(self, name, description=''):
        self.id = str(uuid.uuid4())
        self.name = name

    def __repr__(self):
       return "<Datacenter('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return { 'id': self.id, 'name': self.name }


class Zone(Base):

    __tablename__ = 'zones'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    datacenter_id = Column(String(255), ForeignKey('datacenters.id'))
    datacenter = relationship('Datacenter')

    def __init__(self, name, datacenter_id, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.datacenter_id = datacenter_id

    def __repr__(self):
       return "<Zone('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'datacenter': self.datacenter.name,
            'datacenter_id': self.datacenter_id,
        }


class Device(Base):

    __tablename__ = 'devices'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    zone_id = Column(String(255), ForeignKey('zones.id'))
    vlans_to_devices = relationship('Vlans_to_Device', cascade='all, delete-orphan')
    anycasts_to_devices = relationship('Anycasts_to_Device', cascade='all, delete-orphan')
    zone = relationship('Zone')

    def __init__(self, name, zone_id, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.zone_id = zone_id

    def __repr__(self):
       return "<Device('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'zone': self.zone.name,
            'zone_id': self.zone_id,
        }


class Vlan(Base):

    __tablename__ = 'vlans'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    zone_id = Column(String(255), ForeignKey('zones.id'))
    zone = relationship('Zone')

    def __init__(self, name, zone_id, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.zone_id = zone_id

    def __repr__(self):
       return "<Vlan('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'zone': self.zone.name,
            'zone_id': self.zone_id,
        }


class Vlans_to_Device(Base):

    __tablename__ = 'vlans_to_devices'

    vlan_id = Column(String(255), ForeignKey('vlans.id'), primary_key=True)
    device_id = Column(String(255), ForeignKey('devices.id'), primary_key=True)
    description = Column(String(255))
    vlan = relationship('Vlan')
    device = relationship('Device')

    def to_dict(self):
        return {
            'vlan_id': self.vlan_id,
            'device_id': self.device_id,
            'vlan': self.vlan.name,
            'device': self.device.name,
            'zone_id': self.device.zone_id,
        }

class Anycasts_to_Device(Base):

    __tablename__ = 'anycasts_to_devices'

    anycast_id = Column(String(255), ForeignKey('anycasts.id'), primary_key=True)
    device_id = Column(String(255), ForeignKey('devices.id'), primary_key=True)
    description = Column(String(255))
    anycast = relationship('Anycast')
    device = relationship('Device')

    def to_dict(self):
        return {
            'anycast_id': self.anycast_id,
            'anycast_cidr': self.anycast.cidr,
            'device_id': self.device_id,
            'device': self.device.name,
            'zone_id': self.device.zone_id,
        }

class Subnet(Base):

    __tablename__ = 'subnets'

    id = Column(String(255), primary_key=True)
    cidr = Column(String(255), unique=True)
    description = Column(String(255))
    vlan_id = Column(String(255), ForeignKey('vlans.id'))
    vlan = relationship('Vlan')

    def __init__(self, cidr, vlan_id, description=''):
        self.id = str(uuid.uuid4())
        self.cidr = cidr
        self.vlan_id = vlan_id

    def to_ip(self):
        try:
            return IPv4Network(self.cidr)
        except:
            return IPv6Network(self.cidr)

    def contains(self, ip):
        try:
            return self.to_ip().Contains(IPv4Address(ip))
        except:
            return self.to_ip().Contains(IPv6Address(ip))

    def __repr__(self):
       return "<Subnet('%s','%s')>" % (self.id, self.cidr)

    def to_dict(self):
        return {
            'id': self.id,
            'cidr': self.cidr,
            'vlan': self.vlan.name,
            'vlan_id': self.vlan_id,
        }


class Ip(Base):

    __tablename__ = 'ips'

    id = Column(String(255), primary_key=True)
    ip = Column(String(255), unique=True)
    description = Column(String(255))
    subnet_id = Column(String(255), ForeignKey('subnets.id'))
    subnet = relationship('Subnet')

    def __init__(self, ip, subnet_id, description=''):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.subnet_id = subnet_id

    def __repr__(self):
       return "<Ip('%s','%s')>" % (self.id, self.ip)

    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'subnet': self.subnet.cidr,
            'subnet_id': self.subnet_id,
        }


class Anycast(Base):

    __tablename__ = 'anycasts'

    id = Column(String(255), primary_key=True)
    cidr = Column(String(255), unique=True)
    description = Column(String(255))

    def __init__(self, cidr, description=''):
        self.id = str(uuid.uuid4())
        self.cidr = cidr

    def to_ip(self):
        return IPv4Network(self.cidr)

    def contains(self, ip):
        return self.to_ip().Contains(IPv4Address(ip))

    def __repr__(self):
       return "<Anycast('%s','%s')>" % (self.id, self.cidr)

    def to_dict(self):
        return {
            'id': self.id,
            'cidr': self.cidr,
        }


class Ipanycast(Base):

    __tablename__ = 'ipsanycast'

    id = Column(String(255), primary_key=True)
    ip = Column(String(255), unique=True)
    description = Column(String(255))
    anycast_id = Column(String(255), ForeignKey('anycasts.id'))
    anycast = relationship('Anycast')

    def __init__(self, ip, anycast_id, description=''):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.anycast_id = anycast_id

    def __repr__(self):
       return "<Ipanycast('%s','%s')>" % (self.id, self.ip)

    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'anycast': self.anycast.cidr,
            'anycast_id': self.anycast_id,
        }


class DatacenterPolicy(Base):

    __tablename__ = 'datacenter_policies'
    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('datacenters.id'))
    datacenter = relationship('Datacenter')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.datacenter.name }


class ZonePolicy(Base):

    __tablename__ = 'zone_policies'
    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('zones.id'))
    zone = relationship('Zone')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.zone.name }


class VlanPolicy(Base):

    __tablename__ = 'vlan_policies'

    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('vlans.id'))
    vlan = relationship('Vlan')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.vlan.name }


class AnycastPolicy(Base):

    __tablename__ = 'anycast_policies'

    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('anycasts.id'))
    anycast = relationship('Anycast')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.anycast.cidr }


class SubnetPolicy(Base):

    __tablename__ = 'subnet_policies'
    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('subnets.id'))
    subnet = relationship('Subnet')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.subnet.cidr }


class IpanycastPolicy(Base):

    __tablename__ = 'ipanycast_policies'
    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('ipsanycast.id'))
    ip = relationship('Ipanycast')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.ip.ip }


class IpPolicy(Base):

    __tablename__ = 'ip_policies'
    id = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=True)
    src = Column(String(255), nullable=True)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=True)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    owner_id = Column(String(255), ForeignKey('ips.id'))
    ip = relationship('Ip')

    def __init__(self, owner_id, proto, src, src_port, dst, dst_port, table, policy):
        self.id = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.table = table
        self.policy = policy
        self.owner_id = owner_id

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'owner': self.ip.ip }


database_type = config.get('server', 'database_type')
database_name = config.get('server', 'database_name')

engine = None
if 'sqlite' in database_type:
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    engine = create_engine('%s:///%s' % (database_type, database_name))
    event.listen(engine, 'connect', _fk_pragma_on_connect)
else:
    database_user = config.get('server', 'database_user')
    database_pass = config.get('server', 'database_pass')
    database_host = config.get('server', 'database_host')
    engine = create_engine("{database_type}://{database_user}:{database_pass}"
                           "@{database_host}/{database_name}").format(
                                database_type=database_type,
                                database_user=database_user,
                                database_pass=database_pass,
                                database_host=database_host,
                                database_name=database_name
                           )

Base.metadata.create_all(engine)
