import os
import sys
import getopt
from tyr_client import resources
from tyr_client import client

def main():
    testconf = os.path.join(os.getcwd(), "tyr.toml")
    if not os.path.isfile(testconf):
        sys.exit(-1)
    else:
        tc = client.client()
        tc.init_controller()
        tc.init_test()
