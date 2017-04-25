#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import re
import codecs

def help ():
    print ""
    print "Syntax:"
    print "thes_convert.py filename"


def indexCreation (thfilename):
    # This method is a modified Python transcription of a Perl script (th_gen_idx.pl) 
    # made by Kevin B. Hendricks (see MyThes-1.0)
    """
    /*
     * Copyright 2003 Kevin B. Hendricks, Stratford, Ontario, Canada
     * And Contributors.  All rights reserved.
     *
     * Redistribution and use in source and binary forms, with or without
     * modification, are permitted provided that the following conditions
     * are met:
     *
     * 1. Redistributions of source code must retain the above copyright
     *    notice, this list of conditions and the following disclaimer.
     *
     * 2. Redistributions in binary form must reproduce the above copyright
     *    notice, this list of conditions and the following disclaimer in the
     *    documentation and/or other materials provided with the distribution.
     *
     * 3. All modifications to the source code must be clearly marked as
     *    such.  Binary redistributions based on modified source code
     *    must be clearly marked as modified versions in the documentation
     *    and/or other materials provided with the distribution.
     *
     * THIS SOFTWARE IS PROVIDED BY KEVIN B. HENDRICKS AND CONTRIBUTORS 
     * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
     * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
     * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL 
     * KEVIN B. HENDRICKS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
     * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
     * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
     * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
     * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
     * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
     * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
     * SUCH DAMAGE.
     *
     */
    """

    print("Creating the index file for the thesaurus ...")
    # we read the thesaurus
    entries = []
    pattern = re.compile('^[^|]+\|[1-9][0-9]*$')
    sourcefile = open(thfilename, 'r')
    encodingline = sourcefile.readline() # encoding
    fileOffset = len(encodingline)
    line = sourcefile.readline()
    i = 2
    while line != "" :
        while not re.search(pattern, line) :
            try:
                print(u"## Error at line %d. This line is not a new entry:\n%s" % (i, line))
            except:
                print(u"## Error at line %d. This line is not a new entry." % i)
            line = sourcefile.readline()
            i = i + 1
        offset = len(line)
        line = line.rstrip()
        entry, nbclass = line.split('|')
        nbcl = int(nbclass)
        for k in range(nbcl) :
            line = sourcefile.readline()
            offset = offset + len(line)
            i = i + 1
        entries.append((entry, fileOffset))
        fileOffset = fileOffset + offset
        line = sourcefile.readline()
        i = i + 1
    sourcefile.close()
    
    # we create the index
    entries.sort(elemsort)
    idxfilenames = thfilename.rsplit('.', 1)
    idxfilename = idxfilenames[0] + ".idx"
    destfile = open(idxfilename, 'w')
    destfile.write(encodingline)
    destfile.write("%d\n" % len(entries))
    for entry in entries :
        destfile.write("%s|%d\n" % (entry[0], entry[1]))
    destfile.close()
    print("Done.")


def main ():
    if len(sys.argv) != 2:
        help()
        return False
    
    indexCreation(sys.argv[1])

    
if __name__ == "__main__" :
    main()
