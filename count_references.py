import sys

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from elftools.elf.descriptions import describe_reloc_type


def main():
    if len(sys.argv) < 2:
        print("usage: python3 {} elf [data symbol]".format(sys.argv[0]))
        sys.exit(1)

    elf = sys.argv[1]
    item = sys.argv[2] if len(sys.argv) > 2 else ""

    counters = {}
    reloc_types = {}
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
                    reloc_types[name] = {}

                reloc_type = describe_reloc_type(reloc["r_info_type"], elf)
                if reloc_type in reloc_types[name]:
                    reloc_types[name][reloc_type] += 1
                else:
                    reloc_types[name][reloc_type] = 1

    counters_list = [(v, k) for (k, v) in counters.items()]
    for count, name in sorted(counters_list, reverse=True):
        print("{}: {}".format(name, count))
        reloc_list = [(v, k) for (k, v) in reloc_types[name].items()]
        for count, reloc_type in sorted(reloc_list, reverse=True):
            print("\t{}: {}".format(reloc_type, count))


if __name__ == "__main__":
    main()
