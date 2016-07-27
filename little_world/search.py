import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)    # do not show warnings
from traceroute_ping import *
from random import randint


def search(interface, maxHops, num_traceroutes) :

    paths = defaultdict(int)
    reached = defaultdict(list)
    num_reached = 0
    
    tried_num = 0
    trying_num = 1


    while num_reached < num_traceroutes :

        tried_num += 500
        destinies_tentative = []

        for i in range(0, 500) :
            destinies_tentative.append( randIP() )

        sys.stderr.write( "searching alive IPs...\n" )
        destinies = reachable( destinies_tentative, interface )

        for destiny in destinies :

            sys.stderr.write( str(trying_num) + "\tdestiny:\t" + destiny + "\n" )
            trying_num += 1

            hops, arrived = traceroute( interface, destiny, maxHops, verbose=True, tries=2 )

            if arrived :        #solo considero significativos los casos en que me responde el nodo que busco
                length_path = max( hops.keys() )
                paths[length_path] += 1
                num_reached += 1
                reached[length_path].append(destiny)
                sys.stderr.write( "\t\tReached in " + str(length_path) + " hops\n" )

    print num_reached, "\t", tried_num 
    
    print "----------------------------------------------\n"
    
    for key in sorted( paths.iterkeys() ):
        print key, "\t", paths[key]



def randIP() :

    octet1 = randint(0,224)
    while octet1 in (0, 10, 127, 169, 172, 192, 198, 203) :
        octet1 = randint(0,224)

    octet2 = randint(0,255)
    octet3 = randint(0,255)
    octet4 = randint(0,255)
    
    return str(octet1)+"."+str(octet2)+"."+str(octet3)+"."+str(octet4)



def reachable( destinies, interface ) :

    packages = []
    active = []

    for destiny in destinies :
        pkt = IP( dst=destiny ) / ICMP()
        packages.append(pkt)

    ans, u = sr( packages, iface=interface, timeout=3, verbose=0 )

    for response in ans :
        if response[1][IP][ICMP].type is 0 :    #le arrived
            active.append(response[1][IP].src)
    
    return active
