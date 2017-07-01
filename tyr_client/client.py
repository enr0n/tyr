import os
import sys
import paramiko
import random
import subprocess
import tarfile
import socket
import string
from ConfigParser import SafeConfigParser

from tyr_client import resources

parser = SafeConfigParser()

class controller(object):

    # Global
    localpath = os.getcwd()
    client = paramiko.SSHClient()

    def _gen_id(self):
        """ generate a tag for request """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def __init__(self, addr_srvr, port_srvr, user_srvr, path_srvr):
        self.addr_srvr = addr_srvr
        self.user_srvr = user_srvr
        self.path_srvr = path_srvr
        self.port_srvr = int(port_srvr)

        self.test_id = self._gen_id()

        # Initiate ssh client
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        hosts = os.path.join(os.getenv(resources.strings.FS_HOME), resources.strings.FS_KNOWN_HOSTS)
        self.client.load_host_keys(hosts)

    def compress(self, path, tarname):
        """ compress folder to send to server """
        tar = tarfile.open(tarname + resources.strings.TAR_EXT, resources.strings.TAR_W)
        tar.add(path, tarname)
        tar.close()
        return os.path.join(self.localpath, tarname + resources.strings.TAR_EXT)

    def send(self):
        """ send source to server """
        dir_path = self.localpath
        if not os.path.isdir(dir_path):
            resources.print_err(resources.strings.ERR_DIR_NOT_FOUND)
            exit(-3)

        tar_path = self.compress(dir_path, os.path.basename(self.localpath))
        tar_dest = os.path.join(self.path_srvr, self.test_id + resources.strings.TAR_EXT)
        err = ""

        # Handle sftp
        try:
            resources.print_ok(resources.strings.TEST_SEND)
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(tar_path, tar_dest)

        except IOError:
            resources.print_err(resources.strings.ERR_SFTP)
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
        """ send test conf file """
        # Format the path for remote server
        testconf_dest = os.path.join(self.path_srvr, os.path.basename(testconf))

        # Send the testconf
        try:
            resources.print_ok("Sending testconf.")
            self.client.connect(self.addr_srvr, username=self.user_srvr)
            sftp = self.client.open_sftp()
            sftp.put(testconf, testconf_dest)

        except IOError:
            print resources.strings.ERR_SFTP
            self.client.close()
            exit(-3)

        sftp.close()
        self.client.close()

    def wait_for_test(self):
        """ wait for the server to finish request """
        # Open socket with the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Notify server of test init
        print
        resources.print_ok("Requesting queue for test: "+ self.test_id)
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

    def init_controller(self):
        """ initiate a controller """
        parser.read(self.conf)
        address = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_ADDR)
        port = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_PORT)
        username = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_USER)
        remotepath = parser.get(resources.strings.CONF_LOKI, resources.strings.CONF_RPATH)
        self.controller = controller(address, port, username, remotepath)

    def init_test(self):
        """ initiate request with server """
        self.controller.send()
        self.controller.wait_for_test()
