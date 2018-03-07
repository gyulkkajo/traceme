#!/usr/bin/python3

import argparse
import subprocess
import os
import sys
import json



ENTRY_PREFIX = 'UP_ENTRY'
EXIT_PREFIX = 'UP_EXIT'


def register_funcs(func):
    pass

def get_func_list(bin_path):

    if not os.path.exists(bin_path):
        print('Does not exist %s' % bin_path)
        return None

    try:
        raw_funcs = subprocess.check_output(['perf', 'probe', '-x', bin_path, '--funcs']).decode('utf-8')
    except CalledProcessError as e:
        print('Error while perf : %s' % e)
        return None

    if raw_funcs.startswith('Failed'):
        return None

    funcs = set()
    for i in raw_funcs.split():

        if i.endswith('@plt'):
            #i = i[:-len('@plt')]
            continue

        idx_dot = i.find('.')
        if idx_dot != -1:
            i = i[:idx_dot]

        funcs.add(i)

    return list(funcs)


def parse_into_event(s):

    words = s.strip().split(None, 4)

    if len(words) < 5:
        print('Ignore :', s)
        return None

    exe = words[0].rsplit('-', 1)[0]
    pid = int(words[0].rsplit('-', 1)[1])
    cpuid = int(words[1][1:-1])
    #ts = int(float(words[2][:-1]) * 1000000)
    ts = int(words[2].replace('.', '')[:-1])

    etype = 'B' if words[3].startswith(ENTRY_PREFIX) else 'E'
    func = words[3][len(ENTRY_PREFIX)+1:-1] if etype == 'B' else words[3][len(EXIT_PREFIX)+1:-1]

    # DEBUGGGG
    print(ts, etype, func, pid)

    end_idx = words[4].find(')')
    ip = words[4][1:end_idx]

    args = words[4][end_idx+1:].split()

    event = {
        'name': func,
        'ph': etype,
        'pid': pid,
        'tid': pid,
        'ts': ts,
        'cat': 'UP',
        'args': {}
    }

    if etype is 'B':
        event['args']['entry ip'] = ip
        event['args']['arguments'] = args
    else:
        event['args']['exit ip'] = ip

    return event

def export_to_json(output, raw_lines):
    events = []

    for i in raw_lines:

        e = parse_into_event(i)

        if e is not None:
            events.append(e)

    print("Total nr events: %d" % len(events))

    with open(output, 'w') as fp:
        json.dump(events, fp)



if __name__ == '__main__':
    desc = '''
        An example of how to use argparse

        ./CMD SUBCOMMAND [options...]

        SUB COMMANDS:
            record
            report
            ...
        '''

    arg_parser = argparse.ArgumentParser(description=desc)

    sub_parser = arg_parser.add_subparsers(dest='sub_cmd')

    sub_add = sub_parser.add_parser('add',
            help='Add probe points')
    sub_add.add_argument('-f', '--file',
            action='store',
            required=True,
            help='Executable binary')
    sub_add.add_argument('-a', '--all',
            action='store_true',
            help='Register every functions')
    sub_add.add_argument('-l', '--listfile',
            action='store',
            help='Load function list and register')

    sub_list = sub_parser.add_parser('list',
            help='List up funcs to be registered')
    sub_list.add_argument('-f', '--file',
            action='store',
            required=True,
            help='Executable binary')

    sub_parse = sub_parser.add_parser('parse',
            help='''
Parse into catapult json format
Usage: trace-cmd report | vtrace.py parse -o output.json''')
    sub_parse.add_argument('-o', '--output',
            action='store',
            default='output.json',
            help='Specify output name.')

    args = arg_parser.parse_args()

    # If subcommand doesn't exist?
    if not args.sub_cmd:
        arg_parser.print_help()
        exit(0)

    if args.sub_cmd == 'add':
        print('Remove previous registered probes')
        cmd = 'perf probe -d *'
        subprocess.call(cmd.split())

        probe_funcs = []

        if args.all:
            probe_funcs = get_func_list(args.file)

        elif args.listfile:
            with open(args.listfile) as fp:
                for func in fp.readlines():
                    func = func.strip()

                    if func != '':
                        probe_funcs.append(func)

        for func in probe_funcs:
            cmd = 'perf probe --max-probes=1 -x {0} {1}_{2}={2}'.format(args.file, ENTRY_PREFIX, func)

            try:
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print('Failed to register %s : %s' % (func, e))
                continue

            cmd = 'perf probe --max-probes=1 -x {0} {1}_{2}={2}%return'.format(args.file, EXIT_PREFIX, func)
            try:
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print('Failed to register %s : %s' % (func, e))

                cmd = 'perf probe -x {0} -d {1}_{2}'.format(args.file, ENTRY_PREFIX, func)
                print('Ungiester priv : %s' % cmd)
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
                continue

    elif args.sub_cmd == 'list':
        funcs = get_func_list(args.file)

        for i in funcs:
            print(i)

    elif args.sub_cmd == 'parse':
        export_to_json(args.output, sys.stdin.readlines())
