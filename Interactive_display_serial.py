#!/usr/bin/python3

"""
Command line interface for ChinaDisplayControllerSerial_Class

@author Simon Francklin
@license MIT
@status Alpha
@version 0.1
@date 2019/07/24

@Note Tabs are used.

@change v0.1 : Release to wild. Basic testing done.
@change v0.1.1 : Make command parameters required, with tacks.
"""

import argparse
from ChinaDisplayControllerSerial_Class import ChinaDisplayControllerSerial

def IndexOf(searchstr:str, listvals : list, insensitive : bool = True):
    retval=-1
    for item in listvals:
        if (insensitive == True):
            if (searchstr.lower() == item.lower()):
                    return listvals.index(item)
        else:
            if (searchstr == item):
                    return listvals.index(item)
    return retval

parser = argparse.ArgumentParser()
tables = list(ChinaDisplayControllerSerial.CodeTable.keys())
parser.description = 'Sends commands to China sourced RS232 panels.'
# create the top-level parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help',dest ='command')
# create the parser for the "showtables" command
parser_showtables = subparsers.add_parser('showtables')
parser_showtables.description = 'Shows the command tables available to use.'
# create the parser for the "showkeys" command
parser_showkeys = subparsers.add_parser('showkeys')
parser_showkeys.description = 'Shows the command keys available in the selected table.'
parser_showkeys.add_argument('--table','-t',
                             required=True,
                             type=str.lower,
                             choices=[item.lower() for item in tables],
                             help=": Table to use."
                            )

parser_sendkey = subparsers.add_parser('sendkey')
parser_sendkey.add_argument('--verbose','-v',
                            action='store',
                            metavar='LEVEL',
                            default=0,
                            type=int,
                            help=": How verbose to debug"
                           )
parser_sendkey.add_argument('--port','-p',
                             required=True,
                             type=str,
                             help=": Port to use."
                            )
parser_sendkey.add_argument('--speed','-s',
                            action='store',
                            metavar='N',
                            type=int,
                            default=38400,
                            help=": Baud rate"
                           )
parser_sendkey.add_argument('--table','-t',
                             required=True,
                             type=str.lower,
                             metavar='table',
                             choices=[item.lower() for item in tables],
                             help=": Table to use."
                            )
parser_sendkey.add_argument('--key','-k',
                             required=True,
                             type=str.upper,
                             help=": key to send."
                            )

args = parser.parse_args()
if ('verbose' in args):
    if (args.verbose > 0):
        print(args)
        vars(args)

if (args.command is not None):
    #print("Executing: %s" %args.command)
    if (args.command == 'showtables'):
        print("Tables: ", tables)
    if (args.command == 'showkeys') or (args.command == 'sendkey'):
        lookupTable = tables[ IndexOf(searchstr=args.table, listvals=tables, insensitive=True) ]
        if (hasattr(args, 'verbose')):
            if (args.verbose > 0):
                print("Using table:",lookupTable)
    if (args.command == 'sendkey'):
        if (IndexOf(args.key,list(ChinaDisplayControllerSerial.CodeTable[lookupTable])) == -1):
            print("Invalid key")
            args.command='showkeys'
        else:
            #print("Sending:")
            display = ChinaDisplayControllerSerial ( comm_port = args.port,
                                                        comm_speed = args.speed,
                                                        display_type = lookupTable,
                                                        debugLevel = args.verbose
                                                    )
            display.sendKey(args.key)
    if (args.command == 'showkeys'):
        print("Keys for %s:" %lookupTable)
        print(list(ChinaDisplayControllerSerial.CodeTable[lookupTable]))
else:
    parser.parse_args(['--help'])
