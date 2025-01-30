from ipaddress import IPv4Address, IPv4Network

VOICE_SUPERNETS = [IPv4Network('10.80.0.0/16')]

def generate_cisco_config(vlan: str, subnet: IPv4Network, town_list: str) -> str:
    prefix = str(subnet.prefixlen)
    gateway = str(list(subnet.hosts())[0]) + '/' + prefix
    
    return_string = 'Cisco configuration:\n\n\
interface Bundle-Ether100.' + vlan +'\n\
 description Calix Voice - ' + town_list + '\n\
 bandwidth 100000\n\
 ipv4 address ' + gateway + '\n\
 flow ipv4 monitor kentik-monitor sampler netflowsampler ingress\n\
 encapsulation dot1q ' + vlan + '\n\
!\n\
dhcp ipv4\n\
 interface Bundle-Ether100.' + vlan + ' relay profile metro-kea-dhcp\n\
!'
    return return_string

def generate_kea_config(vlan: str, subnet: IPv4Network) -> str:
    address_list = list(subnet.hosts())
    subnet_string = str(subnet)
    gateway = str(address_list[0])
    first_address = str(address_list[1])
    last_address = str(address_list[-1])

    return_string = 'Kea configuration:\n\n\t\t  {\n\t\t\
        "id": ' + vlan + ',\n\t\t\
        "subnet": "' + subnet_string + '",\n\t\t\
        "pools": [ { "pool": "' + first_address + ' - ' + last_address + '" } ],\n\t\t\
        "option-data": [\n\t\t    \
            {\n\t\t\t\
                "name": "domain-name-servers",\n\t\t\t\
                "space": "dhcp4",\n\t\t\t\
                "csv-format": true,\n\t\t\t\
                "data": "192.35.202.143, 162.255.12.157"\n\t\t    \
            },\n\t\t    \
            {\n\t\t\t\
                "name": "routers",\n\t\t\t\
                "code": 3,\n\t\t\t\
                "space": "dhcp4",\n\t\t\t\
                "csv-format": true,\n\t\t\t\
                "data": "' + gateway + '"\n\t\t    \
            }\n\t\t\
        ]\n\t\t  \
},\n'
    

    return return_string

def get_vlan() -> str:
    vlan = input('VLAN ID: ')

    try:
        vlan = int(vlan)

        if vlan < 1 or vlan > 4094:
            print('Input number between 1 and 4094.')
            return get_vlan()
        return str(vlan)
    except ValueError:
        print('Input a number.')
        return get_vlan()
    
def get_subnet() -> IPv4Network:
    subnet = str(input('Subnet: '))

    try:
        subnet = IPv4Network(subnet)
    except ValueError:
        print('Input valid IPv4 subnet.')
        return get_subnet()
    
    res = False
    for super in VOICE_SUPERNETS:
        if subnet.subnet_of(super):
            res = True

    if not res:
        print('Invalid voice subnet. Please input subnet in one of the following supernets:')
        for super in VOICE_SUPERNETS:
            print(str(super))
        return get_subnet()

    return subnet

if __name__ == '__main__':
    vlan = get_vlan()
    subnet = get_subnet()
    towns = str(input('Town list: '))

    kea_conf = generate_kea_config(vlan, subnet)
    cisco_conf = generate_cisco_config(vlan, subnet, towns)
    print(kea_conf)
    print(cisco_conf)