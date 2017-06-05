import os
import sys
import getopt
from tyr_client import resources
from tyr_client import client

def main():
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], resources.strings.OPTARGS)
    except getopt.GetoptError:
        sys.exit(-1)

    for opt, arg in opts:
        if opt == "-c":
            testconf = arg
    """
    testconf = os.path.join(os.getcwd(), "tyr.toml")
    if not os.path.isfile(testconf):
        print testconf
        print "ERROR"
        sys.exit(-1)
    else:
        tc = client.client(resources.strings.FS_TYRRC)
        controller = tc.getController()
        tc.initTest(controller, testconf)
