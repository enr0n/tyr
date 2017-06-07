import os
import sys
import paramiko
import random
import subprocess
import tarfile
import socket
import string
from termcolor import colored
from ConfigParser import SafeConfigParser

from tyr_client import resources

parser = SafeConfigParser()

CLR_ERR='red'
CLR_OK='green'

class controller(object):

    # Global
    localpath = os.getcwd()
    client = paramiko.SSHClient()

    def __gen_id(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def __init__(self, addr_srvr, port_srvr, user_srvr, path_srvr):
        self.addr_srvr = addr_srvr
        self.user_srvr = user_srvr
        self.path_srvr = path_srvr
        self.port_srvr = int(port_srvr)

        self.test_id = self.__gen_id()

        # Initiate ssh client
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        hosts = os.path.join(os.getenv(resources.strings.FS_HOME), resources.strings.FS_KNOWN_HOSTS)
        self.client.load_host_keys(hosts)


    def compress(self, path, tarname):
        """
        Compress the test directory before sending it to server

        """
        tar = tarfile.open(tarname + resources.strings.TAR_EXT, resources.strings.TAR_W)
        tar.add(path, tarname)
        tar.close()
        return os.path.join(self.localpath, tarname + resources.strings.TAR_EXT)

    def send(self):
        """
        Send the test directory to the server

        """
        #dir_path = os.path.join(self.localpath, dirname)
        dir_path = self.localpath
        if not os.path.isdir(dir_path):
            print "\n *" + colored(resources.strings.ERR_DIR_NOT_FOUND, CLR_ERR)
            exit(-3)

        # Compress the test dir_pathector
        tar_path = self.compress(dir_path, os.path.basename(self.localpath))
        tar_dest = os.path.join(self.path_srvr, self.test_id + resources.strings.TAR_EXT)
        err = ""

        # Handle sftp
        try:
            print "\n *" + colored(resources.strings.TEST_SEND, CLR_OK)
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(tar_path, tar_dest)

        except IOError:
            print colored(resources.strings.ERR_SFTP, CLR_ERR)
            os.remove(tar_path)
            self.client.close()
            exit(-3)

        # Remove the local copy of tarball
        os.remove(tar_path)

        # Close connections
        sftp.close()
        self.client.close()

        # Check for errors in decompress
        if err:
            print err
            exit(-1)

    def sendTestConf(self, testconf):
        # Format the path for remote server
        testconf_dest = os.path.join(self.path_srvr, os.path.basename(testconf))

        # Send the testconf
        try:
            print colored("Sending testconf.", CLR_OK)
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(testconf, testconf_dest)

        except IOError:
            print resources.strings.ERR_SFTP
            self.client.close()
            exit(-3)

        sftp.close()
        self.client.close()

    def waitForTest(self):
        # Open socket with the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Notify server of test init
        print
        print " *" + colored("Requesting queue for test: "+ self.test_id, CLR_OK)
        try:
            sock.connect((self.addr_srvr, self.port_srvr))
            sock.sendall(self.test_id)
            # Wait for the test output

            print "\n  Output"
            print "------------------"
            while True:
                print sock.recv(256)
                break
        except socket.error as serr:
            print resources.strings.ERR_SOCK_CONN_REFUSED
            sock.close()
            sys.exit(-1)

        finally:
            sock.close()


class client(object):

    def __init__(self):
        self.conf = resources.strings.FS_TYRRC

    def initController(self):
        parser.read(self.conf)
        address = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_ADDR)
        port = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_PORT)
        username = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_USER)
        remotepath = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_RPATH)
        self.controller = controller(address, port, username, remotepath)

    def initTest(self):
        self.controller.send()
        self.controller.waitForTest()
