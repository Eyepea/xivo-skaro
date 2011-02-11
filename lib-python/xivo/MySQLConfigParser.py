__version__ = "$Revision: 7 $ $Date: 2009-04-21 11:24:43 +0200 (Tue, 21 Apr 2009) $"
__license__ = """
    Copyright (C) 2009  Proformatique <technique@proformatique.com>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re
from ConfigParser import ConfigParser, Error, NoSectionError, DuplicateSectionError, \
        NoOptionError, InterpolationError, InterpolationMissingOptionError, \
        InterpolationSyntaxError, InterpolationDepthError, ParsingError, \
        MissingSectionHeaderError

class MySQLConfigParser(ConfigParser):
    if os.name == 'nt':
        RE_INCLUDE_FILE = re.compile(r'^[^\.]+(?:\.ini|\.cnf)$').match
    else:
        RE_INCLUDE_FILE = re.compile(r'^[^\.]+\.cnf$').match

    @staticmethod
    def valid_filename(filename):
        if isinstance(filename, basestring) and MySQLConfigParser.RE_INCLUDE_FILE(filename):
            return True

        return False

    def getboolean(self, section, option, retint=False):
        ret = ConfigParser.getboolean(self, section, option)

        if not retint:
            return ret

        return(int(ret))

    def read(self, filenames):
        if isinstance(filenames, basestring):
            filenames = [filenames]

        file_ok = []
        for filename in filenames:
            if self.valid_filename(os.path.basename(filename)):
                file_ok.append(filename)

        return ConfigParser.read(self, file_ok)

    def readfp(self, fp, filename=None):
        return ConfigParser.readfp(self, MySQLConfigParserFilter(fp), filename)


class MySQLConfigParserFilter:
    RE_INCLUDE_OPT = re.compile(r'^\s*!\s*(?:(include|includedir)\s+(.+))$').match

    def __init__(self, fp):
        self.fp = fp
        self._lines = []

    def readline(self):
        if self._lines:
            line = self._lines.pop(0)
        else:
            line = self.fp.readline()

        sline = line.lstrip()

        if not sline or sline[0] != '!':
            return line

        mline = self.RE_INCLUDE_OPT(sline)

        if not mline:
            raise ParsingError("Unable to parse the line: %r." % line)
            return "#%s" % line

        opt = mline.group(2).strip()

        if not opt:
            raise ParsingError("Empty path for include or includir option (%r)." % line)
            return "#%s" % line

        if mline.group(1) == 'include':
            if not MySQLConfigParser.RE_INCLUDE_FILE(opt):
                raise ParsingError("Wrong filename for include option (%r)." % line)
                return "#%s" % line

            self._add_lines(opt)
        else:
            dirname = os.path.dirname(opt)
            for xfile in os.listdir(opt):
                if MySQLConfigParser.RE_INCLUDE_FILE(xfile):
                    self._add_lines(os.path.join(dirname, xfile))

        return self.readline()

    def _add_lines(self, xfile):
        if not os.path.isfile(xfile) or not os.access(xfile, os.R_OK):
            return

        xfilter = MySQLConfigParserFilter(open(xfile))
        lines = xfilter.fp.readlines()
        xfilter.fp.close()
        lines.extend(self._lines)
        self._lines = lines
