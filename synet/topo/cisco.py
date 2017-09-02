#!/usr/bin/env python
"""
Cisco specific configurations generator
Tested with IOS 15.2
"""

from ipaddress import IPv4Interface
from ipaddress import IPv6Interface
from ipaddress import IPv4Network
from ipaddress import IPv6Network
from ipaddress import ip_network
from ipaddress import ip_address
from ipaddress import ip_interface

from synet.topo.graph import NetworkGraph
from synet.topo.bgp import Access
from synet.topo.bgp import ActionSetCommunity
from synet.topo.bgp import ActionSetLocalPref
from synet.topo.bgp import ActionString
from synet.topo.bgp import ActionASPathPrepend
from synet.topo.bgp import CommunityList
from synet.topo.bgp import RouteMap
from synet.topo.bgp import RouteMapLine
from synet.topo.bgp import MatchCommunitiesList
from synet.topo.bgp import MatchIpPrefixListList
from synet.topo.bgp import IpPrefixList


__author__ = "Ahmed El-Hassany"
__email__ = "a.hassany@gmail.com"


class CiscoConfigGen(object):
    """Generate Cisco specific configurations"""
    def __init__(self, g, prefix_map=None):
        assert isinstance(g, NetworkGraph)
        self.g = g
        self.prefix_map = prefix_map or {}
        self.nettype = (IPv4Network, IPv6Network)
        self._next_announced_prefix = int(ip_address(u'128.0.0.0'))

    def prefix_lookup(self, prefix):
        if isinstance(prefix, self.nettype):
            return prefix
        if prefix in self.prefix_map:
            return self.prefix_map[prefix]
        ip = ip_address(self._next_announced_prefix)
        net = ip_network(u"%s/24" % ip)
        self._next_announced_prefix += 256
        self.prefix_map[prefix] = net
        return net

    def gen_community_list(self, community_list):
        """
        Generate config lines for community list
        :param community_list:
        :return: configs string
        """
        assert isinstance(community_list, CommunityList)
        config = ''
        list_id = community_list.list_id
        access = community_list.access.value
        communities = ' '.join([c.value for c in community_list.communities])
        config += "ip community-list %d %s %s\n" % (list_id, access, communities)
        return config

    def gen_ip_prefix_list(self, node, prefix_list):
        """
        Generate config lines for ip prefix-list
        :param prefix_list:
        :return: configs string
        """
        assert isinstance(prefix_list, IpPrefixList)
        config = ''
        access = prefix_list.access.value
        networks = prefix_list.networks
        name = prefix_list.name
        for i, network in enumerate(networks):
            config += "ip prefix-list %s seq %d %s %s/%d\n" % (
            name, (i + 1) * 10, access, str(network.network_address), network.prefixlen)
        return config

    def gen_iface_config(self, iface_name, addr, description=None, isloop=False):
        """
        Generate configuration for a given interface
        :param iface_name: the name of the interface, e.g. Fa0/0 or lo0
        :param addr: instance of ip_interface
        :param description: optional text description
        :return: string config
        """
        assert isinstance(addr, (IPv4Interface, IPv6Interface))
        config = ''
        config += 'interface %s\n' % iface_name
        config += " ip address %s %s\n" % (addr.ip, addr.netmask)
        if description:
            config += ' description "{}"\n'.format(description)
        if not isloop:
            config += " speed auto\n"
            config += " duplex auto\n"
        config += "!\n"
        return config

    def gen_all_interface_configs(self, node):
        """
        Iterate over all interfaces (including loopbacks) to generate their configs
        :param node: router name
        :return: string configs
        """
        config = ''
        for neighbor in self.g.neighbors(node):
            iface = self.g.get_edge_iface(node, neighbor)
            #addr = self.g.get_edge_addr(node, neighbor)
            addr = self.g.get_iface_addr(node, iface)
            desc = self.g.get_edge_iface_description(node, neighbor)
            config += self.gen_iface_config(iface, addr, desc, False)

        # Loop back interface
        for lo in sorted(self.g.get_loopback_interfaces(node)):
            addr = self.g.get_loopback_addr(node, lo)
            desc = self.g.get_loopback_description(node, lo)
            config += self.gen_iface_config(lo, addr, desc, True)
        return config

    def gen_all_communities_lists(self, node):
        """
        Get all communities list defined for the router
        :param node: router
        :return: config string
        """
        config = ""
        comm_lists = self.g.get_bgp_communities_list(node)
        for num in comm_lists:
            comm_list = comm_lists[num]
            config += self.gen_community_list(comm_list)
            config += "!\n"
        config += "!\n"
        return config

    def gen_all_ip_prefixes(self, node):
        """
        Generate all the ip prefixes lists
        :param node:
        :return:
        """
        config = ''
        lists = self.g.get_ip_preflix_lists(node)
        for l in lists:
            prefix_list = lists[l]
            config += self.gen_ip_prefix_list(node, prefix_list)
            config += "!\n"
        return config

    def gen_route_map_match(self, node, match):
        config = ''
        if isinstance(match, MatchCommunitiesList):
            config += 'match community %d' % match.match.list_id
        elif isinstance(match, MatchIpPrefixListList):
            assert match.match.name in self.g.get_ip_preflix_lists(node)
            config += 'match ip address prefix-list %s' % match.match.name
        else:
            raise ValueError('Unknow match type %s' % match)
        return config

    def gen_route_map_action(self, action):
        config = ''
        if isinstance(action, ActionSetLocalPref):
            config += 'set local-preference %d' % action.value
        elif isinstance(action, ActionSetCommunity):
            comms = ' '.join([c.value for c in action.communities])
            config += 'set community %s' % comms
            if action.additive == True:
                config += ' additive'
        elif isinstance(action, ActionASPathPrepend):
            config += 'set as-path prepend %s' % ' '.join([str(x) for x in action.value])
        elif isinstance(action, ActionString):
            config = '%s' % action.value
        else:
            raise ValueError('Unknow action type %s' % action)
        return config

    def gen_route_map(self, node, routemap):
        assert isinstance(routemap, RouteMap)
        config = ''
        name = routemap.name
        for line in routemap.lines:
            no = line.lineno
            access = line.access.value
            config += "route-map %s %s %s\n" % (name, access, no)
            for match in line.matches:
                config += " %s\n" % self.gen_route_map_match(node, match)
            for action in line.actions:
                config += " %s\n" % self.gen_route_map_action(action)
        return config

    def gen_all_route_maps(self, node):
        config = ''
        maps = self.g.get_route_maps(node)
        for name in sorted(maps):
            routemap = maps[name]
            config += self.gen_route_map(node, routemap)
            config += "!\n"
        return config

    def gen_bgp_config(self, node):
        """
        Generates the BGP specific configurations
        :param node: router
        :return: configs string
        """
        config = ""
        asn = self.g.get_bgp_asnum(node)
        config += "router bgp %d\n" % asn
        config += ' no synchronization\n'
        config += ' bgp log-neighbor-changes\n'
        config += ' bgp additional-paths send receive\n'
        announcements = self.g.get_bgp_announces(node)
        for ann in announcements:
            net, mask, route_map = None, None, None
            if hasattr(ann, 'network'):
                net = ann.network.ip
                mask = ann.netmask
            elif ann in self.g.get_loopback_interfaces(node):
                addr = self.g.get_loopback_addr(node, ann)
                net = addr.network.network_address
                mask = addr.netmask
            elif self.g.has_node(ann) and self.g.is_network(ann):
                iface = self.g.get_edge_iface(node, ann)
                addr = self.g.get_edge_iface(node, iface)
                net = addr.network.network_address
                mask = addr.netmask
            route_map = announcements[ann].get('route_map', None)
            if route_map:
                config += ' network %s mask %s route-map %s\n' % (net, mask, route_map)
            else:
                config += ' network %s mask %s\n' % (net, mask)
        for neighbor in sorted(self.g.get_bgp_neighbors(node)):
            if not self.g.is_router(neighbor): continue
            neighbhor_asn = self.g.get_bgp_asnum(neighbor)
            iface = self.g.get_edge_iface(neighbor, node)
            neighboraddr = self.g.get_iface_addr(neighbor, iface)
            assert neighbhor_asn is not None, 'AS Num is not set for %s' % neighbor
            assert neighboraddr is not None
            config += " neighbor %s remote-as %s\n" % (neighboraddr.ip, neighbhor_asn)
            description = self.g.get_bgp_neighbor_description(node, neighbor)
            if description:
                config += " neighbor %s description \"%s\"\n" % (neighboraddr.ip, description)
            config += " neighbor %s advertisement-interval 0\n" % neighboraddr.ip
            config += " neighbor %s soft-reconfiguration inbound\n" % neighboraddr.ip
            config += " neighbor %s send-community\n" % neighboraddr.ip
            import_map = self.g.get_bgp_import_route_map(node, neighbor)
            export_map = self.g.get_bgp_export_route_map(node, neighbor)
            if import_map:
                config += " neighbor %s route-map %s in\n" % (neighboraddr.ip, import_map)
            if export_map:
                config += " neighbor %s route-map %s out\n" % (neighboraddr.ip, export_map)
        return config

    def gen_tracker_configs(self, node):
        """Generate configurations for various trackers"""
        config = ""

        def get_applet(tracker_id, iface, addr, rmap, on):
            from_state, to_state = ('Down', 'Up') if on else ('Up', 'Down')
            applet_name = 'Track%s_%s' % (iface.replace('/', '_'), to_state)
            match = "%%TRACKING-5-STATE: %d interface %s line-protocol %s->%s" % (tracker_id, iface, from_state, to_state)
            applet = "!\n"
            applet += "event manager applet %s\n" % applet_name
            applet += ' event syslog pattern "%s"\n' % match
            applet += ' action 0.0 cli command "en"\n'
            applet += ' action 1.0 cli command "config t"\n'
            applet += ' action 2.0 cli command "router bgp %s"\n' % self.g.get_bgp_asnum(node)
            adv = 'network %s mask %s route-map %s' % (addr.network.network_address, addr.netmask, rmap)
            if on:
                applet += ' action 3.0 cli command "%s"\n' % adv
            else:
                applet += ' action 3.0 cli command "no %s"\n' % adv
            applet += ' action 4.0 cli command "end"\n'
            applet += '!\n'
            return applet

        for tracker_id in self.g.node[node].get('trackers', {}):
            data =self.g.node[node]['trackers'][tracker_id]
            iface = data['iface']
            addr = data['addr']
            rmap = data['route_map']
            config += "track %s interface %s line-protocol\n" % (tracker_id, iface)
            config += "!\n"
            config += "!\n"
            config += get_applet(tracker_id, iface, addr, rmap, True)
            config += get_applet(tracker_id, iface, addr, rmap, False)

        return config

    def gen_external_announcemetns(self, node):
        assert self.g.is_peer(node)
        next_lo = 0
        ifaces = []
        lines = []
        lineno = 5
        for ann in self.g.get_bgp_advertise(node):
            net = self.prefix_lookup(ann.prefix)
            addr = ip_interface(u"%s/%d" % (net.hosts().next(), net.prefixlen))
            iface = "lo%s" % next_lo
            desc = "For %s" % ann.prefix

            self.g.set_loopback_addr(node, iface, addr)
            self.g.set_loopback_description(node, iface, desc)

            iplist = IpPrefixList(name="L_%s" % next_lo, access=Access.permit, networks=[net])
            self.g.add_ip_prefix_list(node, iplist)
            match = MatchIpPrefixListList(iplist)
            action = ActionASPathPrepend(ann.as_path)
            line = RouteMapLine(matches=[match],
                                actions=[action],
                                access=Access.permit,
                                lineno=lineno)
            self.g.add_bgp_announces(node, iface)
            lines.append(line)
            ifaces.append(iface)
            lineno += 5
            next_lo += 1

        rmap = RouteMap(name="Export_%s" % node, lines=lines)
        self.g.add_route_map(node, rmap)
        for neighbor in self.g.get_bgp_neighbors(node):
            err = "External peers cannot have predefined export route-maps (Peer %s)" % node
            assert not self.g.get_bgp_export_route_map(node, neighbor), err
            self.g.add_bgp_export_route_map(node, neighbor, rmap.name)

    def gen_all_ospf(self, node):
        if not self.g.is_local_router(node):
            return ""
        config = ""
        config += "router ospf 100\n"
        config += " network 0.0.0.0 255.255.255.255 area 0.0.0.0\n"
        return config

    def gen_router_config(self, node):
        """
        Get the router configs
        :param node: router
        :return: configs string
        """
        if self.g.is_peer(node):
            self.gen_external_announcemetns(node)

        preamble = ["version 15.2",
                    "service timestamps debug datetime msec",
                    "service timestamps log datetime msec",
                    "boot-start-marker",
                    "boot-end-marker",
                    "no aaa new-model",
                    "ip cef",
                    "no ipv6 cef",
                    "multilink bundle-name authenticated",
                    "ip forward-protocol nd",
                    "no ip http server",
                    "no ip http secure-server",
                    "ip bgp-community new-format",
                    "ip community-list expanded PrimList permit 10:*",
                    "ip community-list expanded SecList permit 20:*"
                    ]
        end = ['!', '!', 'control-plane', '!', '!', 'line con 0', ' stopbits 1',
               'line aux 0', ' stopbits 1', 'line vty 0 4', ' login', '!', 'end']

        config = ""
        config += "\n!\nhostname {node}\n!\n".format(node=node)
        config += "!\n"
        config += self.gen_all_interface_configs(node)
        config += "!\n"
        config += self.gen_all_communities_lists(node)
        config += "!\n"
        config += self.gen_all_ip_prefixes(node)
        config += "!\n"
        config += self.gen_all_route_maps(node)
        config += "!\n"
        config += self.gen_bgp_config(node)
        config += "!\n"
        config += self.gen_all_ospf(node)
        config += "!\n"
        config += self.gen_tracker_configs(node)
        config += "!\n"
        configs = "!\n" + "\n!\n".join(preamble) + config + "\n".join(end)
        configs += "\n"
        return configs
