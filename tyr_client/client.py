import os
import sys
import paramiko
import random
import subprocess
import tarfile
import socket
from ConfigParser import SafeConfigParser

from tyr_client import resources

parser = SafeConfigParser()

class controller(object):

    # Global
    localpath = os.getcwd()
    client = paramiko.SSHClient()

    def __init__(self, addr_srvr, port_srvr, user_srvr, path_srvr):
        self.addr_srvr = addr_srvr
        self.user_srvr = user_srvr
        self.path_srvr = path_srvr
        self.port_srvr = int(port_srvr)

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

    def send(self, dirname):
        """
        Send the test directory to the server

        """
        dir_path = os.path.join(self.localpath, dirname)
        if not os.path.isdir(dir_path):
            print resources.strings.ERR_DIR_NOT_FOUND
            exit(-3)

        # Compress the test dir_pathector
        dirname = os.path.basename(dirname)
        tar_path = self.compress(dir_path, dirname)
        tar_dest = os.path.join(self.path_srvr, dirname + resources.strings.TAR_EXT)
        err = ""

        # Handle sftp
        try:
            print resources.strings.TEST_SEND
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(tar_path, tar_dest)

            # Decompress the folder on srvr
            cmd = resources.strings.TAR_CMD + tar_dest + " -C " + self.path_srvr
            stdin, stdout, stderr = self.client.exec_command(cmd)
            err = stderr.read()

        except IOError:
            print resources.strings.ERR_SFTP
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
            print "Sending testconf."
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(testconf, testconf_dest)

        except IOError:
            print resources.strings.ERR_SFTP
            self.client.close()
            exit(-3)

        sftp.close()
        self.client.close()

    def waitForTest(self, testconf):
        # Open socket with the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Notify server of test init
        print "Requesting queue for test: ", testconf
        try:
            sock.connect((self.addr_srvr, self.port_srvr))
            sock.sendall(os.path.basename(testconf))
            # Wait for the test output
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

    def __init__(self, conf):
        self.conf = conf

    def getController(self):
        parser.read(self.conf)
        address = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_ADDR)
        port = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_PORT)
        username = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_USER)
        remotepath = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_RPATH)
        return controller(address, port, username, remotepath)

    def initTest(self, client, testconf):
        parser.read(testconf)
        dirname = parser.get(resources.strings.CONF_FILES, resources.strings.CONF_DIR)
        client.send(dirname)
        client.sendTestConf(testconf)
        client.waitForTest(testconf)
