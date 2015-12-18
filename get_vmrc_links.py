#!/usr/bin/python


"""
Python program for listing the vms on an ESX / vCenter host with direct Virtual Machine Remote Console (vmrc)
links
"""

from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect

import argparse
import atexit
import getpass
import ssl


def get_args():
    """
   Supports the command-line arguments listed below.
   """
    parser = argparse.ArgumentParser(
            description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=False, default='172.17.9.52', action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=False, default='root', action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, default='sk35alu!65DC', action='store',
                        help='Password to use when connecting to host')
    args = parser.parse_args()
    return args


def print_vm_info(vm, args, depth=1):
    """
   Print information for a particular virtual machine or recurse into a folder
    with depth protection
    :param depth:
    :param args: arguments to compile vmrc link
    :param vm: Virtual Machine Object
   """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            print_vm_info(c, depth + 1)
        return

    summary = vm.summary
    print("Name       : ", summary.config.name)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("vmrc link  : ", "vmrc://" + args.user + "@" + args.host + ":" + str(args.port) + "/?moid=" + vm._moId)
    annotation = summary.config.annotation
    if annotation is not None and annotation != "":
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip = summary.guest.ipAddress
        if ip is not None and ip != "":
            print("IP         : ", ip)
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")


def main():
    """
   Simple command-line program for listing the virtual machines on a system.
   """

    args = get_args()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host, args.user))

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    si = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=password,
                      port=int(args.port),
                      sslContext=context)
    if not si:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vm_folder'):
            datacenter = child
            vm_folder = datacenter.vmFolder
            vm_list = vm_folder.childEntity
            for vm in vm_list:
                print_vm_info(vm, args)
    return 0


# Start program
if __name__ == "__main__":
    main()
