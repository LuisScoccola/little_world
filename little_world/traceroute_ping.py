import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)    # no muestra WARNINGS
from scapy.all import *
from time import clock, time

#def main() :
#
#    if len(sys.argv) not in range(3, 5) :
#        print "Usage:\n\t\tsudo python traceroute-ping.py interface ip_destiny maxHops[opcional]\n"
#        sys.exit(1)
#
#
#    interface = sys.argv[1]
#    destiny = sys.argv[2]
#    if len(sys.argv) is 4 :
#        maxHops = int(sys.argv[3])
#    else :
#        maxHops = 32
#
#    hops, arrived = traceroute( interface, destiny, maxHops )

def traceroute ( interface, destiny, maxHops, verbose=True, tries=4, timeo=5 ) :

    hops = defaultdict(list)
    cut = 4

    packages_to_send = []


    for ttl_count in range(1, maxHops+1) :
        for i in range(0, tries) :

            pkt = IP( dst=destiny, ttl=ttl_count ) / ICMP( seq=ttl_count ) 
            packages_to_send.append(pkt)


    responses, u = sr( packages_to_send, timeout=timeo, iface=interface, verbose=0 )

    for answered in responses :

        if ICMP in answered[1] :

            if answered[1][IP][ICMP].type == 0 :            #echo-reply
                hop = "DESTINY"
            elif answered[1][IP].src == destiny :
                # no es echo-reply pero responde el destiny
                # vimos que esto puede pasar
                hop = "DESTINY"
            elif answered[1][IP][ICMP].type == 11 :        # murio el ttl
                hop = answered[1][IP].src
        

            ttl_sended = int(answered[0][IP][ICMP].seq)
            if hop not in hops[ttl_sended] :
                hops[ttl_sended].append( hop )


    # limpio en dos casos:
    # si ya arrived, saco todos los de despues
    # si hubo 6 nodos seguidos que no respondieron lo saco
    #    esto es para evitar que un nodo se despierte
    #    mientras estoy haciendo el traceroute y me
    #    responda un mensaje con un ttl muy grande tardio

    arrived = False
    stop = False

    for key in sorted( hops.iterkeys() ) :
        if arrived or stop :
            del hops[key]
        elif isDestiny( hops[key] ) :
            if justWakeUp( hops, key ) :
                stop = True
                del hops[key]
            else :
                arrived = True


    if verbose :                # imprimir
        print "\ndestiny:\t", destiny
        print "reached:\t", arrived
        for key in sorted( hops.iterkeys() ) :
            print "hops", key, " have been\t", hops[key]
        sys.stdout.flush()



    return hops, arrived 


def isDestiny( ips ) :
    if len(ips) is 1 and 'DESTINY' in ips :
        return True
    else :
        return False


def justWakeUp( hops, key ) :

    tolerance = 11

    if key >= tolerance :
        for i in range(1, tolerance) :
            if key-i not in hops :
                continue    #sigo buscando
            else :
                return False    #no se desperto recien
        return True            #no me responden hace rato
                        #asumo que se acaba de despertar
    else :
        return False


#if __name__ == "__main__" :
#    main()
