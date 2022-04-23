#!/usr/bin/env python3
import io
from multiprocessing.sharedctypes import Value
from pprint import PrettyPrinter
import urllib3
#import sys

from ansi2html import Ansi2HTMLConverter
from asyncio import InvalidStateError
from datetime import datetime
from prettytable import PrettyTable
from termcolor import colored

def colourise_age(age):
    if age.days < 7:
        return colored(age, 'green')
    elif 7 < age.days < 14:
        return colored(age, 'yellow')
    elif age.days > 14:
        return colored(age, 'red')
    
    return age

arches=[
    "amd64",
    "alpha",
    "arm64",
    "arm",
    "hppa",
    "mips",
    "m68k",
    "hppa",
    "ia64",
    "ppc",
    "riscv",
    "sparc",
    "s390",
    "x86"
]

mirror="https://gentoo.osuosl.org/releases/{0}/autobuilds/"

http = urllib3.PoolManager()

status = PrettyTable()
status.field_names = ["Arch", "stage3", "Age"]

for arch in arches:
    path = mirror.format(arch)
    req = http.request("GET", "{0}/latest-stage3.txt".format(path), preload_content=False)
    req.auto_close = False

    if not req.status == 200:
        print(req)
        continue

    for line in io.TextIOWrapper(req):
        if not line or line.startswith("#"):
            continue   

        line = line.strip()
        line = line.split(" ")
        print(line)

        entry, size = line[0], line[1]
        date, stage3 = entry.split("/", 1)

        # Convert the date from e.g. 20220417T171236Z into a datetime we can understand
        try:
            date = datetime.strptime(date, '%Y%m%dT%H%M%SZ')
        except ValueError:
            print(f"Could not parse %{date=} %{arch=} %{stage3=}")
            #sys.exit(1)
            continue

        age = datetime.now() - date

        #print(f"{stage3=} from {date=} with {age=}")
        status.add_row([arch, stage3, colourise_age(age)])

print(status)

with open("archstatus.html", "w") as results:
    conv = Ansi2HTMLConverter()
    ansi = str(status)
    html = conv.convert(ansi)
    results.write(html)