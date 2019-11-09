#!/usr/bin/env python3

import os
import os.path
import re
import subprocess
import sys

from elftools.elf.elffile import ELFFile


def get_objdump(f):
    elf = ELFFile(open(f, "rb"))

    mach = elf["e_machine"]
    if mach in ("EM_X86_64", "EM_386"):
        return "objdump"
    elif mach == "EM_ARM":
        return "arm-none-eabi-objdump"
    else:
        raise ValueError("no objdump for {!r}!".format(mach))


def function_info(func, addr, last_line):
    last_pos, bytes_ = re.match(r"\s+([a-f0-9]+):\s+([a-f0-9]+)", last_line).groups()
    assert len(bytes_) % 2 == 0
    size = int(last_pos, 16) + int(len(bytes_) / 2) - int(addr, 16)
    print("'{}': {} bytes".format(func, size))


def process_objdump_outpuut(func, f, output):
    in_func = False
    last = None
    addr = None

    for l in output.splitlines():
        m = re.match(r"^([a-f0-9]+)\ <(\w*{}\w*)>:$".format(func), l)
        if m:
            addr = m.group(1)
            cur = m.group(2)
            in_func = True
            l += " " + f
        elif l == "" and in_func:
            # function ends in a blank
            in_func = False
            function_info(cur, addr, last)

        if in_func:
            print(l)
            last = l
    else:
        if in_func:
            function_info(cur, addr, last)


def objdump_file(func, f):
    objdump = get_objdump(f)
    output = subprocess.check_output([objdump, "-d", "-z", f])
    process_objdump_outpuut(func, f, output.decode())


def objdump_dir(func, d):
    for rootdir, subdirs, files in os.walk(d):
        for f in files:
            if not f.endswith(".o"):
                continue

            f = os.path.join(rootdir, f)
            if os.system("nm {} 2>/dev/null | grep {} >/dev/null".format(f, func)) == 0:
                objdump_file(func, f)


def main(argv):
    if len(sys.argv) < 2:
        print("usage: python3 {} func [files...]".format(sys.argv[0]))
        printf("if no files are given, search in current directory, recursively")
        sys.exit(1)

    func = sys.argv[1]
    if len(sys.argv) > 2:
        for f in sys.argv[2:]:
            if os.path.isfile(f):
                objdump_file(func, f)
            else:
                objdump_dir(func, f)
    else:
        objdump_dir(func, os.getcwd())


if __name__ == "__main__":
    main(sys.argv)
