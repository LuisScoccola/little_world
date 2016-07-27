from little_world.search import *


def main() :

    if len(sys.argv) is not 4 :
        print "Usage:\n\t\tsudo python pequeno_mundo_test.py interface maxHops number_of_traceroutes\n"
        sys.exit(1)


    interface = sys.argv[1]
    maxHops = int(sys.argv[2])
    num_traceroutes = int(sys.argv[3])

    search(interface, maxHops, num_traceroutes)



if __name__ == "__main__" :
    main()
