import sys

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection


def main():
    if len(sys.argv) < 2:
        print("usage: python3 {} elf [data symbol]".format(sys.argv[0]))
        sys.exit(1)

    elf = sys.argv[1]
    item = sys.argv[2] if len(sys.argv) > 2 else ""

    counters = {}
    elf = ELFFile(open(elf, "rb"))

    for sec in elf.iter_sections():
        if not isinstance(sec, RelocationSection):
            continue

        symtab = elf.get_section(sec["sh_link"])
        for reloc in sec.iter_relocations():
            ref_sym = symtab.get_symbol(reloc["r_info_sym"])
            name = ref_sym.name

            if item in name:
                if name in counters:
                    counters[name] += 1
                else:
                    counters[name] = 1

    counters = [(v, k) for (k, v) in counters.items()]
    for count, name in sorted(counters, reverse=True):
        print("{}: {}".format(name, count))


if __name__ == "__main__":
    main()
