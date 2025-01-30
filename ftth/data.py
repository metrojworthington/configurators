from ipaddress import IPv4Network, IPv4Address, IPv6Network, IPv6Address

def ip_input(version: int = 4, ip_type: str = 'public') -> str:
    RFC6598 = IPv4Network('100.64.0.0/10')
    METRO_V6 = IPv6Network('2607:5380::/32')
    METRO_V4 = [IPv4Network('104.219.32.0/21'), IPv4Network('108.59.176.0/20'), IPv4Network('162.255.8.0/21'), IPv4Network('192.35.200.0/22'),\
                IPv4Network('199.116.80.0/22'), IPv4Network('216.107.160.0/20')]
    MIKROTIK_V4 = [IPv4Address('108.59.178.219'), IPv4Address('108.59.177.106'), IPv4Address('104.219.32.226'), IPv4Address('104.219.32.62'),\
                   IPv4Address('108.59.176.150'), IPv4Address('108.59.176.62'), IPv4Address('108.59.178.38')]
    MIKROTIK_V6 = [IPv6Address('2607:5380:c001:16::3'), IPv6Address('2607:5380:c001:15::3'), IPv6Address('2607:5380:c001:e::3'),\
                   IPv6Address('2607:5380:c001:d::3'), IPv6Address('2607:5380:c001:12::3'), IPv6Address('2607:5380:c001:11::3'), IPv6Address('2607:5380:c001:1e::3')]

    if version == 4 and ip_type == 'public':
        prompt = 'Input public IPv4 subnet in CIDR notation: '
        subnet = input(prompt)
        try:
            subnet = IPv4Network(subnet)

            if subnet.subnet_of(RFC6598) or subnet.is_private:
                print('Public IPv4 subnet requested but RFC1918 or RFC6598 subnet input. Please input a public address.')
                return ip_input(version, ip_type)

            res = False
            for supernet in METRO_V4:
                if subnet.subnet_of(supernet):
                    res = True
            
            if not res:
                print('Input a subnet in Metro owned IPv4 space.')
                return ip_input(version, ip_type)

            return str(subnet)
        except ValueError:
            print('Invalid IPv4 subnet. Please input a valid CIDR subnet.')
            return ip_input(version, ip_type)
    
    if version == 4 and ip_type == 'RFC6598':
        prompt = 'Input RFC6598 IPv4 subnet in CIDR notation: '
        subnet = input(prompt)
        try:
            subnet = IPv4Network(subnet)

            if not subnet.subnet_of(RFC6598):
                print('RFC6598 subnet asked for but input not within range. Please input a valid RFC6598 subnet.')
                return ip_input(version, ip_type)
            
            return str(subnet)
        except ValueError:
            print('Invalid IPv4 subnet. Please input a valid CIDR subnet.')
            return ip_input(version, ip_type)
    
    if version == 4 and ip_type == 'gateway':
        prompt = 'Input IPv4 address of MikroTik: '
        gateway = input(prompt)

        try:
            gateway = IPv4Address(gateway)

            if gateway not in MIKROTIK_V4:
                print('Please input IPv4 address of MikroTik.')
                return ip_input(version, ip_type)

            return str(gateway)
        except ValueError:
            print('Input valid IPv4 address.')
            return ip_input(version, ip_type)
    
    if version == 6 and ip_type == 'pd':
        prompt = 'Input IPv6 prefix-delegation /44 network: '
        pd = input(prompt)

        try:
            pd = IPv6Network(pd)
            prefix = pd.prefixlen
            
            if prefix != 44:
                print('Input valid IPv6 /44 network.')
                return ip_input(version, ip_type)
            
            if not pd.subnet_of(METRO_V6):
                print('Input a valid Metro IPv6 /44 network.')
                return ip_input(version, ip_type)

            return str(pd)
        except ValueError:
            print('Input valid IPv6 subnet.')
            return ip_input(version, ip_type)
    
    if version == 6 and ip_type == 'slaac':
        prompt = 'Input IPv6 SLAAC /64 network for CPE MGMT: '
        slaac = input(prompt)

        try:
            slaac = IPv6Network(slaac)
            prefix = slaac.prefixlen

            if prefix != 64:
                print('Input valid IPv6 /64 network.')
                return ip_input(version, ip_type)

            if not slaac.subnet_of(METRO_V6):
                print('Input a valid Metro IPv6 /64 network.')
                return ip_input(version, ip_type)
            
            return str(slaac)
        except ValueError:
            print('Input valid IPv6 /64 network.')
            return ip_input(version, ip_type)
    
    if version == 6 and ip_type == 'gateway':
        prompt = 'Input IPv6 address of MikroTik: '
        gateway = input(prompt)

        try:
            gateway = IPv6Address(gateway)
        except ValueError:
            print('Input valid IPv6 address.')
            return ip_input(version, ip_type)
        
        if gateway not in MIKROTIK_V6:
            print('Input valid MikroTik IPv6 address.')
            return ip_input(version, ip_type)
        
        return str(gateway)

def get_vlan(vlan_type: str = 'cgnat') -> str:
    GATEWAY_VLANS = [110, 111, 592, 593]

    if vlan_type == 'cgnat':
        prompt = 'Input town VLAN number: '
    else:
        prompt = 'Input gateway VLAN number: '

    vlan = input(prompt)

    try:
        vlan = int(vlan)

        if vlan < 1 or vlan > 4094:
            print('Input number between 1 and 4094.')
            return get_vlan(vlan_type)
        if vlan_type != 'cgnat' and vlan not in GATEWAY_VLANS:
            print('Invalid gateway VLAN.')
            return get_vlan(vlan_type)
        return str(vlan)
    except ValueError:
        print('Input a number.')
        return get_vlan(vlan_type)

def get_towns() -> str:
    prompt = 'Input town(s): '
    return input(prompt)

def cisco_config(public: str, gateway4: str, slaac: str, pd: str, gateway6: str, vlan: str) -> str:
    config4 = \
'\n\nCisco Configuration:\n\
####################\n\
router static address-family ipv4 unicast\n\
  ' + public + ' ' + gateway4 + ' description CALIX-' + vlan + '\n\
!\n'

    config6 = \
'router static address-family ipv6 unicast\n\
  ' + pd + ' ' + gateway6 + ' description CALIX-' + vlan + '_PD\n\
  ' + slaac + ' ' + gateway6 + ' description CALIX-' + vlan + '_CPE\n\
!\n'
    return config4 + config6

def routeros_config(public: str, rfc6598: str, slaac: str, pd: str, vlan: str, towns: str, gw_vlan: str) -> str:
    DNS4 = '192.35.202.143,162.255.12.157'
    DNS6 = '2607:5380:c001:7::3,2607:5380:c001:8::3'
    option_set = 'calix-option43-spid'
    v4_leasetime = '3h'
    v6_leasetime = '31d'

    vlan_str = 'vlan.' + vlan
    gw_vlan_str = 'vlan.' + gw_vlan

    cgn_net = IPv4Network(rfc6598)
    cgn_addresses = list(cgn_net.hosts())
    cgn_gw = str(cgn_addresses[0])
    cgn_pool_start = str(cgn_addresses[1])
    cgn_pool_end = str(cgn_addresses[-1])
    cgn_netsize = str(cgn_net.prefixlen)
    cgn_pool = cgn_pool_start + '-' + cgn_pool_end
    pool_name = vlan_str + '-cgn-hosts'
    pd_pool_name = 'ipv6-pd-pool-' + vlan_str
    
    slaac_gw = slaac[:-3]+'1/64'

    config_header = \
'\n\
MikroTik Configuration:\n\
#######################\n\
'
    config_vlan = \
'/interface/ethernet/switch set 0 l3-hw-offloading=no\n\
/interface/vlan/add comment="' + towns + ' FTTH" interface=bridge-sw name='+ vlan_str + ' vlan-id=' + vlan +'\n\
/interface/bridge/vlan/add bridge=bridge-sw tagged=LAN-LAG-1 vlan-ids=' + vlan +'\n\
/interface/ethernet/switch set 0 l3-hw-offloading=yes\n\
'
    config_ipv4 = \
'\
/ip/address/add address=' + cgn_gw + '/' + cgn_netsize + ' comment="' + towns + ' CGN GW" interface=' + vlan_str + '\n\
/ip/address/add address=' + public + ' comment="' + towns + ' Metro Public IPs" interface=' + gw_vlan_str + '\n\
/ip/pool/add comment="' + towns + ' CGN" name=' + pool_name + ' ranges=' + cgn_pool + '\n\
/ip/dhcp-server/network/add address=' + str(cgn_net) + ' comment="' + towns + ' RFC6598" dns-server=' + DNS4 + ' gateway=' + cgn_gw +'\n\
/ip/dhcp-server/add address-pool=' + pool_name + ' comment="' + towns + ' CGN DHCP" dhcp-option-set=' + option_set + ' interface=' + vlan_str + ' lease-time=' + v4_leasetime + ' name=' + pool_name +'\n\
/ip/firewall/address-list/add address=' + str(cgn_net) + ' comment="' + towns + ' RFC6598 Addressing" list=' + pool_name +'\n\
/ip/firewall/nat/add action=src-nat chain=srcnat comment="NAT444 ' + towns + '" out-interface=' + gw_vlan_str + ' src-address-list=' + pool_name + ' to-addresses=' + public + '\n\
'

    config_ipv6 = \
'\
/ipv6/address/add address=' + slaac_gw + ' comment="MGMT for ' + towns + ' CPE" interface=' + vlan_str +'\n\
/ipv6/nd/add dns=' + DNS6 + ' interface=' + vlan_str +'\n\
/ipv6/pool/add comment="IPv6 prefix delegation pool for ' + towns + '" name=' + pd_pool_name + ' prefix=' + pd + ' prefix-length=56\n\
/ipv6/dhcp-server/add address-pool=' + pd_pool_name + ' interface=' + vlan_str + ' lease-time=' + v6_leasetime + ' name=' + pd_pool_name + ' comment="DHCPv6 for ' + towns + '"\n\
'
    return config_header + config_vlan + config_ipv4 + config_ipv6

if __name__ == '__main__':
    public = ip_input(4, 'public')
    rfc6598 = ip_input(4, 'RFC6598')
    gateway4 = ip_input(4, 'gateway')
    slaac = ip_input(6, 'slaac')
    pd = ip_input(6, 'pd')
    gateway6 = ip_input(6, 'gateway')
    vlan = get_vlan()
    towns = get_towns()
    gw_vlan = get_vlan('gateway')

    cisco = cisco_config(public, gateway4, slaac, pd, gateway6, vlan)
    routeros = routeros_config(public, rfc6598, slaac, pd, vlan, towns, gw_vlan)
    print(cisco + routeros)
    exit(0)