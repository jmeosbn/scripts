#!/usr/bin/env python

# Decode From and Subject lines spammers encode in other charsets
# to try to hide them from spam filters. (RFC 2047 encoding.)
# Use in conjunction with programs like procmail or spamassassin,
# instead of something like formail

import sys, os
import email

progname = os.path.basename(sys.argv[0])
Usage = """Usage: %s [-a] headername [filename]

Find a line matching the given header name (Subject:, From:, etc.)
and decode it according to RFC 2047.
Without a filemame, will read standard input.
Adding -a will print all matches within the given file, not just the first.

Example: %s -a Subject: /var/mail/yourname""" % (progname, progname)

def decode_file(filename, header_wanted) :
    if filename == '-' :
        fil = sys.stdin
    else :
        fil = open(filename)

    output = ''
    found_something = False
    for line in fil :
        # If it matches the header we seek, or if we've already started
        # matching the header and we're looking for continuation lines,
        # build up our string:
        if (not output and line.startswith(header_wanted)) \
          or (output and (line.startswith(' ') or line.startswith('\t'))) :
            # We have a match! But we may need to read multiple lines,
            # since one header can be split over several lines.
            # print "Original:", line
            found_something = True
            for part in email.Header.decode_header(line) :
                output += part[0]
                # Special case: the header itself comes out with charset None
                # and decode doesn't add a space between it and the next part,
                # even though there was a space in the original. So add one.
                # I'm taking a wild guess that the relevant factor here is
                # the None charset rather than the fact that it matched
                # the header, but keep an eye open for counterexamples.
                if not part[1] :
                    output += ' '

        elif output :
            # if we've already matched the header, and this isn't a
            # continuation line, then we're done. Print and exit.

            #sys.stdout.write("<<" + part[0] + '>>')
            print output.strip()
            if all :
                output = ''
            else :
                sys.exit(0)

    # If we get here, we never matched a header, or ended with a continuation line.
    if not found_something :
        print "No such header", header_wanted, "in", filename
        return

if sys.argv[1] == '-h' or sys.argv[1] == '--help' :
    print Usage
    sys.exit(1)

# A -a argument means don't stop at the first header,
# decode all matching headers in the file.
if sys.argv[1] == '-a' :
    all = True
    sys.argv = sys.argv[1:]
else :
    all = False

header_wanted = sys.argv[1]

try :
    if len(sys.argv) > 2 :
        for filename in sys.argv[2:] :
            decode_file(filename, sys.argv[1])
    else :
        fil = sys.stdin
        decode_file('-', sys.argv[1])
except KeyboardInterrupt :
    sys.exit(1)

