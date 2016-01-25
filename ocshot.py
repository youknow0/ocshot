#!/usr/bin/python

import config
import traceback
import sys
import os
import modes.base
from argparse import ArgumentParser
from clients.ocwrap import get_occlient

parser = ArgumentParser()
parser.add_argument("--confdir", help="configuration directory",
                    default="")
parser.add_argument("--mode", help="operation mode. pass 'help' for "
                    + "details.", type=str, default="screenshot",
                    choices=["help", "screenshot", "screenshot_region"])
parser.add_argument("--no-gui", help="do not show any GUI",
                    action="store_true", dest="no_gui")
args = parser.parse_args()

# take default config dir if none given
if args.confdir == "":
    homedir = os.path.expanduser("~")
    confdir = os.path.join(homedir, ".config", "ocshot")
else: 
    confdir = args.confdir

try:
    myconf = config.Config(confdir)
    myconf.read()
except OSError as e:
    print "Could not read the configuration from the directory '%s': %s" % (confdir, str(e))

oc = get_occlient(args.no_gui, myconf.conf)

exitcode = 0
mode = modes.base.factory(args.mode, None)
try:
    mode.prepare()
    filepath = mode.get_filepath()
    print oc.share(filepath)
except:
    print "Error!"
    traceback.print_exc()
    exitcode = 1

mode.cleanup()

sys.exit(exitcode)
