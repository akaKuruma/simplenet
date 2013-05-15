#!/bin/bash

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
set -o pipefail

function run_test(){
    local cmd="$1"
    local to_find="$2"
    simplenet="../src/sbin/simplenet-cli"
    echo "::  Running ${simplenet/*\//} $cmd"
    echo -n "::: Status ->  "
    result=$($simplenet $cmd 2>&1)
    if !( echo "$result" | grep -qw "$to_find" ) ; then
        echo -e "\033[01;31m[ FAIL ]\033[00m"
        echo "Unable to $cmd"
        echo "Expected: $to_find"
        echo "Got $result"
    else
        if [ "$to_find" == '' ] ; then
            echo -e "\033[01;32m[ OK ]\033[00m"
        else
            echo -e "\033[01;32m[ OK ]\033[00m Result: $to_find"
        fi
    fi
}

function run_firewall_test(){
    local action="$1"
    local rule_type="$2"
    local cmd="$1 $2 $3"
    local simplenet="../src/sbin/simplenet-cli"
    echo "::  Running ${simplenet/*\//} $cmd"
    echo -n "::: Status ->  "
    local result=$($simplenet $cmd 2>&1)
    local rule_id=$(echo "$result" | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
    if [ $(echo "$rule_id" | wc -c) != 37 ]; then
        echo -e "\033[01;31m[ FAIL ]\033[00m"
        echo "Unable to $cmd"
        echo "Got $result"
    else
        echo -e "\033[01;32m[ OK ]\033[00m Result: ${rule_id}"
        run_test "firewallrule info $rule_type ${rule_id}" '"id": "'${rule_id}'"'
        run_test "firewallrule delete $rule_type ${rule_id}" '"message": "Successful deletetion"'
    fi
}

echo "::::: Starting Datacenter Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "datacenter create datacenter01" '"message": "Datacenter:datacenter01 already exists Forbidden"'
run_test "datacenter info datacenter01" '"name": "datacenter01"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Zone Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_firewall_test "firewallrule create" "zone" "zone01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT"
run_test "zone info zone01" '"name": "zone01"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Firewall Device Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "firewall create firewall01 --zone zone01" '"name": "firewall01"'
run_test "firewall create firewall02 --zone zone01" '"name": "firewall02"'
run_test "firewall create firewall01 --zone zone01" '"message": "Firewall:firewall01 already exists Forbidden"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "firewall vlan_attach firewall01 --vlan vlan01" '"name": "firewall01"'
run_test "firewall vlan_attach firewall02 --vlan vlan01" '"name": "firewall02"'
run_test "firewall vlan_attach firewall01 --vlan vlan01" '"message": "Exception(FlushError(.*"'
run_test "firewall vlan_detach firewall01 --vlan vlan01" '"message": "Successful deletetion"'
run_test "firewall info firewall01" '"name": "firewall01"'
run_test "firewall info firewall02" '"name": "firewall02"'
run_test "firewall vlan_detach firewall02 --vlan vlan01" '"message": "Successful deletetion"'
run_test "firewall info firewall01" '"name": "firewall01"'
run_test "firewall info firewall02" '"name": "firewall02"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "firewall delete firewall01" '"message": "Successful deletetion"'
run_test "firewall delete firewall02" '"message": "Successful deletetion"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting DHCP Device Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "dhcp create dhcp01" '"name": "dhcp01"'
run_test "dhcp create dhcp02" '"name": "dhcp02"'
run_test "dhcp create dhcp01" '"message": "Dhcp:dhcp01 already exists Forbidden"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "dhcp vlan_attach dhcp01 --vlan vlan01" '"name": "dhcp01"'
run_test "dhcp vlan_attach dhcp02 --vlan vlan01" '"name": "dhcp02"'
run_test "dhcp vlan_attach dhcp01 --vlan vlan01" '"message": "Exception(FlushError(.*"'
run_test "dhcp vlan_detach dhcp01 --vlan vlan01" '"message": "Successful deletetion"'
run_test "dhcp info dhcp01" '"name": "dhcp01"'
run_test "dhcp info dhcp02" '"name": "dhcp02"'
run_test "dhcp vlan_detach dhcp02 --vlan vlan01" '"message": "Successful deletetion"'
run_test "dhcp info dhcp01" '"name": "dhcp01"'
run_test "dhcp info dhcp02" '"name": "dhcp02"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "dhcp delete dhcp01" '"message": "Successful deletetion"'
run_test "dhcp delete dhcp02" '"message": "Successful deletetion"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Switch Device Tests "
run_test "switch create sw01 --model_type openvswitch --address tcp:10.30.83.20:6640 --mac 10:1F:74:32:F7:49" '"name": "sw01"'
run_test "switch create sw01 --model_type openvswitch --address tcp:10.30.83.20:6640 --mac 10:1F:74:32:F7:49" '"message": "Switch:sw01 already exists Forbidden"'
run_test "switch info sw01" '"address": "tcp:10.30.83.20:6640"'
run_test "switch delete sw01" '"message": "Successful deletetion"'
run_test "switch delete sw01" '"error": "EntityNotFound"'

echo -e "\n::::: Starting Vlan Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"message": "Vlan:vlan01 already exists Forbidden"'
run_firewall_test "firewallrule create" "vlan" "vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT"
run_firewall_test "firewallrule create" "vlan" "vlan01 --dst_port 80 --proto tcp --table INPUT --policy ACCEPT"
run_firewall_test "firewallrule create" "vlan" "vlan01 --dst_port 443 --proto tcp --table INPUT --policy ACCEPT"
run_test "vlan info vlan01" '"name": "vlan01"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Subnet Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02 --type private_vlan" '"name": "vlan02"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"message": "Subnet:192.168.0.0/24 already exists Forbidden"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "subnet info 192.168.0.0/24" '"cidr": "192.168.0.0/24"'
run_test "subnet info 192.168.0.1/24" '"cidr": "192.168.0.1/24"'
run_test "subnet delete 192.168.0.0/24" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.1/24" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "vlan delete vlan02" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "zone delete zone02" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Anycast Tests "
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycast create 192.168.168.0/24" '"message": "Anycast:192.168.168.0/24 already exists Forbidden"'
run_test "anycast info 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycast delete 192.168.168.0/24" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Ip Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02 --type private_vlan" '"name": "vlan02"'
run_test "firewall create firewall01 --zone zone01" '"name": "firewall01"'
run_test "firewall vlan_attach firewall01 --vlan vlan01" '"name": "firewall01"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "ip create 192.168.0.1 --subnet 192.168.0.0/24" '"ip": "192.168.0.1"'
run_test "ip create 192.168.1.1 --subnet 192.168.0.1/24" '"message": "Ip:192.168.1.1 address must be contained in 192.168.0.1/24 Forbidden"'
run_firewall_test "firewallrule create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP"
run_firewall_test "firewallrule create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table FORWARD --policy DROP"
run_firewall_test "firewallrule create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP"
run_firewall_test "firewallrule create" "ip" "192.168.0.1 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP"
run_test "ip vlan_info 192.168.0.1" '"name": "vlan01"'
run_test "ip vlan_info 192.168.1.1" '"error": "EntityNotFound"'
run_test "ip info 192.168.0.1" '"ip": "192.168.0.1"'
run_test "ip delete 192.168.0.1" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.0/24" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.1/24" '"message": "Successful deletetion"'
run_test "firewall delete firewall01 --zone zone01" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "vlan delete vlan02" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "zone delete zone02" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Interface Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02 --type private_vlan" '"name": "vlan02"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "ip create 192.168.0.1 --subnet 192.168.0.0/24" '"ip": "192.168.0.1"'
run_test "ip create 192.168.1.1 --subnet 192.168.0.1/24" '"message": "Ip:192.168.1.1 address must be contained in 192.168.0.1/24 Forbidden"'
run_test "ip create 192.168.0.2 --subnet 192.168.0.0/24" '"ip": "192.168.0.2"'
run_test "interface create 84:2b:2b:00:96:22" '"id": "84:2b:2b:00:96:22"'
run_test "interface ip_attach 84:2b:2b:00:96:22 192.168.0.1" '"id": "84:2b:2b:00:96:22"'
run_test "interface ip_attach 84:2b:2b:00:96:22 192.168.0.1" '"message": "Exception(FlushError(.*"'
run_test "interface ip_attach 84:2b:2b:00:96:22 192.168.0.2" '"id": "84:2b:2b:00:96:22"'
run_test "interface ip_attach 84:2b:2b:00:96:22 192.168.0.3" '"error": "EntityNotFound"'
run_test "interface ip_attach 84:2b:2b:00:96:21 192.168.0.2" '"error": "EntityNotFound"'
run_test "switch create sw01 --model_type openvswitch --address tcp:10.30.83.20:6640 --mac 10:1F:74:32:F7:49" '"name": "sw01"'
run_test "switch int_attach sw01 --inter 84:2b:2b:00:96:22 --int_name vif0.1 --ofport 44" '"id": "84:2b:2b:00:96:22"'
run_test "switch int_attach sw01 --inter 84:2b:2b:00:96:21 --int_name vif1.1 --ofport 55" '"error": "EntityNotFound"'
run_test "ip delete 192.168.0.1" '"message": "Exception(IntegrityError'
run_test "interface ip_detach 84:2b:2b:00:96:22 192.168.0.2" '"message": "Successful deletetion"'
run_test "interface ip_detach 84:2b:2b:00:96:22 192.168.0.1" '"message": "Successful deletetion"'
run_test "interface ip_detach 84:2b:2b:00:96:22 192.168.0.2" '"message": "Exception(UnmappedInstanceError'
run_test "ip delete 192.168.0.1" '"message": "Successful deletetion"'
run_test "ip delete 192.168.0.2" '"message": "Successful deletetion"'
run_test "interface delete 84:2b:2b:00:96:22" '"message": "Successful deletetion"'
run_test "switch delete sw01" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.0/24" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.1/24" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "vlan delete vlan02" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "zone delete zone02" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting IpAnycast Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "firewall create firewall01 --zone zone01" '"name": "firewall01"'
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycastip create 192.168.168.3 --anycast 192.168.168.0/24" '"ip": "192.168.168.3"'
run_test "anycastip create 192.168.0.3 --anycast 192.168.168.0/24" '"message": "Ip:192.168.0.3 address must be contained in 192.168.168.0/24 Forbidden"'
run_firewall_test "firewallrule create" "anycast" "192.168.168.0/24 --dst 192.168.168.3 --proto tcp --table OUTPUT --policy DROP"
run_test "anycastip info 192.168.168.3" '"ip": "192.168.168.3"'
run_test "firewall anycast_attach firewall01 --anycast 192.168.168.0/24" '"name": "firewall01"'
run_test "firewall anycast_detach firewall01 --anycast 192.168.168.0/24" '"message": "Successful deletetion"'
run_test "anycastip delete 192.168.168.3" '"message": "Successful deletetion"'
run_test "anycast delete 192.168.168.0/24" '"message": "Successful deletetion"'
run_test "firewall delete firewall01" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting ipv6 Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "vlan create vlan01 --zone zone01 --type private_vlan" '"name": "vlan01"'
run_test "subnet create 2804:218::2001:c62c:3ff:fe02:adcd/64 --vlan vlan01" '"cidr": "2804:218::2001:c62c:3ff:fe02:adcd/64"'
run_test "ip create 2804:218::2001:c62c:3ff:fe02:1 --subnet 2804:218::2001:c62c:3ff:fe02:adcd/64" '"ip": "2804:218::2001:c62c:3ff:fe02:1"'
run_test "ip create 2804:218::2001:c62c:3ff:fe02:1 --subnet 2804:218::2001:c62c:3ff:fe02:adcd/64" '"message": "Ip:2804:218::2001:c62c:3ff:fe02:1 already exists Forbidden"'
run_firewall_test "firewallrule create" "subnet" "2804:218::2001:c62c:3ff:fe02:adcd/64 --dst 2804:218::2001:c62c:3ff:fe02:ffff --proto tcp --table OUTPUT --policy DROP"
run_firewall_test "firewallrule create" "ip" "2804:218::2001:c62c:3ff:fe02:1 --dst 2804:218::2001:c62c:3ff:fe02:ffff --proto tcp --table OUTPUT --policy DROP"
run_test "ip info 2804:218::2001:c62c:3ff:fe02:1" '"ip": "2804:218::2001:c62c:3ff:fe02:1"'
run_test "ip delete 2804:218::2001:c62c:3ff:fe02:1" '"message": "Successful deletetion"'
run_test "subnet delete 2804:218::2001:c62c:3ff:fe02:adcd/64" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'
