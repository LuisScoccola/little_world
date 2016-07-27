import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)    # no muestra WARNINGS
from scapy.all import *
from time import clock, time

def main() :

    if len(sys.argv) not in range(3, 5) :
        print "Modo de uso:\n\t\tsudo python traceroute-ping.py interface ip_destiny maxHops[opcional]\n"
        sys.exit(1)


    interface = sys.argv[1]
    destiny = sys.argv[2]
    if len(sys.argv) is 4 :
        maxHops = int(sys.argv[3])
    else :
        maxHops = 32

    hops, arrived = traceroute( interface, destiny, maxHops )

def traceroute ( interface, destiny, maxHops, verbose=True, tries=4, timeo=5 ) :

    hops = defaultdict(list)
    cortar = 4

    packages_a_mandar = []


    for ttl_count in range(1, maxHops+1) :
        for i in range(0, tries) :

            pkt = IP( dst=destiny, ttl=ttl_count ) / ICMP( seq=ttl_count ) 
            packages_a_mandar.append(pkt)


    responses, u = sr( packages_a_mandar, timeout=timeo, iface=interface, verbose=0 )

    for respondido in responses :

        if ICMP in respondido[1] :

            if respondido[1][IP][ICMP].type == 0 :            #echo-reply
                hop = "DESTINO"
            elif respondido[1][IP].src == destiny :
                # no es echo-reply pero responde el destiny
                # vimos que esto puede pasar
                hop = "DESTINO"
            elif respondido[1][IP][ICMP].type == 11 :        # murio el ttl
                hop = respondido[1][IP].src
        

            ttl_enviado = int(respondido[0][IP][ICMP].seq)
            if hop not in hops[ttl_enviado] :
                hops[ttl_enviado].append( hop )


    # limpio en dos casos:
    # si ya llegue, saco todos los de despues
    # si hubo 6 nodos seguidos que no respondieron lo saco
    #    esto es para evitar que un nodo se despierte
    #    mientras estoy haciendo el traceroute y me
    #    responda un mensaje con un ttl muy grande tardio

    llegue = False
    noVaMas = False

    for key in sorted( hops.iterkeys() ) :
        if llegue or noVaMas :
            del hops[key]
        elif esDestino( hops[key] ) :
            if seAcabaDeDespertar( hops, key ) :
                noVaMas = True
                del hops[key]
            else :
                llegue = True


    if verbose :                # imprimir
        print "\ndestiny:\t", destiny
        print "alcanzado:\t", llegue
        for key in sorted( hops.iterkeys() ) :
            print "hops", key, " fueron\t", hops[key]
        sys.stdout.flush()



    return hops, llegue 


def esDestino( ips ) :
    if len(ips) is 1 and 'DESTINO' in ips :
        return True
    else :
        return False


def seAcabaDeDespertar( hops, key ) :

    tolerancia = 11

    if key >= tolerancia :
        for i in range(1, tolerancia) :
            if key-i not in hops :
                continue    #sigo buscando
            else :
                return False    #no se desperto recien
        return True            #no me responden hace rato
                        #asumo que se acaba de despertar
    else :
        return False


if __name__ == "__main__" :
    main()
