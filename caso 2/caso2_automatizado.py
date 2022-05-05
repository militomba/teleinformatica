#from enum import IntFlag
#from sys import prefix
from mininet.net import Mininet
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class Redes:
    def __init__(self, cantidadRedes):
        self.cantidadRedes = cantidadRedes
        self.net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')
        self.r_central = None

    #crecaion de la ip de red
    def redes(self):
        IPs = 8
        ip = '192.168.100'
        list_redes=[]
        for r in range(self.cantidadRedes):
            list_redes.append(ip + '.' + str(int(IPs * r)))
        return list_redes 
            #el ultimo host va a ser 8 * 0, despues 8 * 1 
            # y asi dependiendo de la cantidad de redes que tengamos
    
    #creacion de switches
    def generateSwitch (self):
        info('*Add Switch\n')
        for s in range(0, self.cantidadRedes):
            wan = "s_wan" + str(s + 1)
            lan = "s_lan" + str(s + 1)
            self.net.addSwitch(wan, cls=OVSKernelSwitch, failMode='standalone')
            self.net.addSwitch(lan, cls=OVSKernelSwitch, failMode='standalone')

    #Creacion de routers
    def generateRouter(self):
        info('*Add router\n')
        #router central
        self.r_central = self.net.addHost('r_central', cls=Node, defaultRoute=None)
        self.r_central.cmd('sysctl -w net.ipv4.ip_forward=1')
        #router de cada sucursal
        for router in range (0, self.cantidadRedes):
            name_router = 'r' + str(router+1) #Le pongo +1 porque sino empezaria con router 0
            rout = self.net.addHost(name_router, cls=Node)
            rout.cmd('sysctl -w net.ipv4.ip_forward=1')

    #creacion de host
    def generateHost(self):
        info('*Add Host\n')
        for h in range(0, self.cantidadRedes):
            ip = '10.0' + str(h+1)
            IPh = ip + '254/24'  #ip final
            nameHost = 'h' + str(h+1)
            self.net.addHost(nameHost, cls=Host, ip=IPh, defaultRoute=None)

    #creacion de links
    def generateLinks(self):
        info('*Add links\n')
        for l in range(0, self.cantidadRedes):
            s_wan = self.net.get('s_wan' + str(l+1))
            s_lan = self.net.get('s_lan' + str(l+1))
            router = self.net.get('r' + str(l+1))
            host= self.net.get('h' + str(l+1))
            self.net.addLink(self.r_central, s_wan)
            self.net.addLink(s_wan, router)
            self.net.addLink(router, s_lan)
            self.net.addLink(s_lan, host)
    
    def generateNetwork(self, list_redes):
        info('* Starting network\n')
        self.net.build()
        #info( '*Starting controllers\n')
        # for controller in self.net.controllers:
        #     controller.start()
        info('* Starting switches\n')
        for switch in self.net.switches:
            switch.start([])
        info('*Setting switches and host')
        for i in range(0, self.cantidadRedes):
            router = self.net.get('r'+ str(i + 1))
            host = self.net.get('h'+ str(i + 1))
            red = list_redes[i].rsplit('.',1)
            ip = red[0] + '.' + str(int(red[1]) + 6)
            eth = 'r_central-eth' + str(i)
            self.r_central.setIP(ip, prefixLen=29, intf=eth)
            ip1 = red[0] + '.' + str(int(red[1]) + 1)
            ip_interna = '10.0.' + str(i + 1) + '.1'
            ip_host = '10.0.' + str(i + 1) + '.0/24'
            eth0 = 'r' + str(i + 1) + '-eth0'
            router.setIP(ip1, prefixLen=29, intf=eth0)
            router.setIP(ip_interna, prefixLen=24, intf=eth0)
            cmd = 'ip route add' + ip_host + 'via' + ip1
            self.r_central.cmd(cmd)
            cmd1 = 'ip route add 10.0.0.0/18 via ' + ip
            router.cmd(cmd1)
            cmd2 = 'ip route add 192.168.100.0/24 via ' + ip
            router.cmd(cmd2)
            cmd3 = 'ip route add 10.0.0.0/18 via ' + ip_interna
            host.cmd(cmd3)
            cmd4 = 'ip route add 192.168.100.0/24 via ' + ip_interna
            host.cmd(cmd4)
    
    def generateRed(self):
        list_redes = self.redes()
        self.generateSwitch()
        self.generateRouter()
        self.generateHost()
        self.generateLinks()
        self.generateNetwork(list_redes)
        CLI(self.net)
        self.net.stop()

def main():
    while True:
        while True:
            cantidadRedes = int(input('Cuantas redes queres crear (menor a 32 o 32)? '))
            break
        if cantidadRedes > 0 and cantidadRedes < 33:
            break
        else:
            print("\nPuede crear hasta 32 redes! ELIJA OTRO NUMERO")
    caso2 = Redes(cantidadRedes)
    caso2.generateRed()


if __name__ == '__main__':
    setLogLevel('info')
    main()






        


