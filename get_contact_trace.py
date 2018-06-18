#!/usr/bin/env python

"""
Takes a list of atomic contacts as input and generates a "trace-figure" showing
the presence / absence of one or more interactions. This can be useful for
evaluating correlations between interactions or check for consistent behavior
within simulation replicates.

The input is at least one contact-file (see get_dynamic_contacts.py) and a set
of interactions specified as space-separated regular expressions, for example
the following string indicates hydrogen bonds between a specific hydrogen donor
on a HIS to any acceptor on a GLU:
  "A:HIS:172:NE2 A:GLU:143:(OE.|O)"
Note that the first part of the expression matches only a single atom while
the second matches both OE1, OE2, and the O-atoms of residue 143. Using this
syntax it's possible to get residue-level interactions, e.g.:
  "A:PHE:86:C[B-Z][0-9]* A:VAL:68:C[B-Z][0-9]*"
will match any carbon-carbon interaction between side-chains in residues 68 and
86.

The output is a stack of trace-plots that specify time-points at which each
interaction is present or absent.

Example
======
The GetContacts example folder shows how to generate a trajectory from 5xnd
in which two hydrophobic SC-SC interaction can be traced with the following
command:
    get_contact_trace.py \
        --input_contacts 5xnd_all-contacts.tsv \
        --interactions "A:ILE:51:CD1 A:PHE:103:C[GDEZ].*" \
                       "A:PHE:103.* A:PHE:48.*" \
        --labels "ILE51 - PHE103" \
                 "PHE48 - PHE103" \
        --trace_output 5xnd_hp_trace.png
"""

from contact_calc.transformations import *
import sys
import re


def main(argv=None):
    """
    Main function called once at the end of this module. Configures and parses command line arguments, parses input
    files and generates output files.
    """
    # Set up command line arguments
    import argparse as ap
    parser = ap.ArgumentParser(description=__doc__, formatter_class=ap.RawTextHelpFormatter)
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    parser._action_groups.append(optional)  # added this line

    required.add_argument('--input_contacts',
                          required=True,
                          nargs='+',
                          type=ap.FileType('r'),
                          help='A multi-frame contact-file generated by dynamic_contact.py')
    required.add_argument('--interactions',
                          required=True,
                          type=str,
                          nargs='+',
                          help='Interaction patterns, each a space-separated pair of regexes')
    required.add_argument('--trace_output',
                          required=True,
                          type=str,
                          help='An image file to write the trace-plot to (png and svg supported)')
    # required.add_argument('--correlation_output',
    #                       required=False,
    #                       type=str,
    #                       help='An image file to write the correlation-plot to (png and svg supported)')

    optional.add_argument('--labels',
                          required=False,
                          type=str,
                          nargs='+',
                          help='Interaction pattern labels. If not specified, the regexes will be used')

    args = parser.parse_args(argv)

    # Process arguments
    itypes = parse_itypes(['all'])
    interaction_patterns = parse_interaction_patterns(args.interactions)
    labels = parse_labels(args.labels, args.input_contacts, args.interactions)
    contact_lists = [parse_contacts(contact_file, itypes)[0] for contact_file in args.input_contacts]

    # Filter contacts and generate trace
    contact_frames = filter_contacts(contact_lists, interaction_patterns)
    write_trace(contact_frames, labels, args.trace_output)


def parse_interaction_patterns(ipatterns):
    ip_str_pairs = [ip.split() for ip in ipatterns]
    print(ip_str_pairs)
    if any([len(ip) != 2 for ip in ip_str_pairs]):
        sys.stderr.write("Error: Interactions must be valid space-separated regular expressions\n")
        sys.exit(-1)

    return [(re.compile(ip[0]), re.compile(ip[1])) for ip in ip_str_pairs]


def parse_labels(labels, input_files, interactions):
    if labels is not None:
        if len(labels) != len(interactions) * len(input_files):
            sys.stderr.write("Error: Only specified %d labels (should be %d) which doesn't match %d interaction "
                             "patterns across %d files\n" % (len(labels),
                                                             len(interactions) * len(input_files),
                                                             len(interactions),
                                                             len(input_files)))
            sys.exit(-1)
        return labels

    from itertools import product

    return [f.name + ": " + i.replace(" ", " - ") for i, f in product(interactions, input_files)]


def parse_itypes(itype_argument):
    """Parses the itype argument and returns a set of strings with all the selected interaction types """
    if "all" in itype_argument:
        return ["sb", "pc", "ps", "ts", "vdw", "hb", "lhb", "hbbb", "hbsb",
                "hbss", "wb", "wb2", "hls", "hlb", "lwb", "lwb2"]
    return set(itype_argument.split(","))


def filter_contacts(contact_lists, interaction_patterns):
    ret = []
    for ips in interaction_patterns:
        for contacts in contact_lists:
            ip0 = ips[0]
            ip1 = ips[1]

            ip_contact_frames = set()
            for c in contacts:
                frame = c[0]
                atom0 = c[2]
                atom1 = c[3]
                if (ip0.match(atom0) and ip1.match(atom1)) or (ip0.match(atom1) and ip1.match(atom0)):
                    ip_contact_frames.add(frame)

            ret.append(sorted(list(ip_contact_frames)))
    return ret


def write_trace(contact_frames, labels, output_file):
    """
    Generates a trace-plot from the contact frames and writes a figure to an image file.

    Parameters
    ==========
    contact_frames: list of int
        Indicates all frame numbers for which a certain interaction is present
    labels: list of str
        The labels to write next to each trace
    output_file: str
        Path to an image file supported by matplotlib
    """
    assert len(contact_frames) == len(labels)
    # TODO: Remove these print-statements
    print("contact_frames:")
    print(contact_frames)
    print("labels:")
    print(labels)
    print("output_file:")
    print(output_file)
    # TODO: Write trace plots here
    pass


if __name__ == "__main__":
    main()


__author__ = 'Rasmus Fonseca <fonseca.rasmus@gmail.com>, Jonas Kaindl <jkaindl@stanford.edu>'
__license__ = "Apache License 2.0"
