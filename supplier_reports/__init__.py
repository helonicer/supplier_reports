import os,sys
from supplier_reports.python_script_common import set_logging, trace_call, info
from supplier_reports import conf as g
import logging
from openpyxl import load_workbook
import copy
import contextlib
import os
import csv
import traceback, pdb
from supplier_reports.gen_reports import gen_reports
from supplier_reports.webapi import app
import StringIO
from werkzeug.datastructures import FileStorage
#####################################################################
#Globals
_logger = logging.getLogger(__name__)

#####################################################################
# move to env utiliy funcs

def get_opts():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-v", "--verbose" , dest="verbose", action="count", default=0, help="set verbosity level, default is NOTICE")
    parser.add_option('--pdb', dest='pdb', action='store_true', default=False, help='enable pdb on exception')
    parser.add_option("-f", '--file', dest='file', action='store', help='file path for source report of suppliers reports')
    parser.add_option("-w", '--webapi', dest='webapi', action='store_true', default=False)
    # parser.add_option("-l", '--load-latest', dest='load_latest', action='store_false', default=True,
    #                   help='do not load latest state from db')
    # parser.add_option("-t", '--test-site', dest='test_site', action='store', default=None, help='test latest update via this url, also sets load_latest to False, and does not update db')

    return parser, parser.parse_args()


def process_config():
    parser, (options, args) = get_opts()
    if options.pdb:
        sys.excepthook = info
    set_logging(app_name="supplier_reports", app_path=g.config.root.app_path, verbose=options.verbose, file_handler=True)
    g.config.extend(dict(options=vars(options),args=args))
    return parser


def get_filename_from_path(filepath):
    dir, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    return name


def main():
    try:
        parser = process_config()
        #g.config.extend(dict(db_latest=db_latest))
        if g.config.root.options.file:
            assert os.path.isfile(g.config.root.options.file)
            fo = StringIO.StringIO()
            fo.write(open(g.config.root.options.file).read())
            fs = FileStorage(fo, filename=get_filename_from_path(g.config.root.options.file))
            for report in gen_reports(fs):
                if report:
                    report.save(g.config.root.reports_dir)
        elif g.config.root.options.webapi:
            webapi.app.main()
        else:
            parser.print_help()
    except Exception as e:
        _logger.exception("exception in main", exc_info=True)
        raise
    finally:
        pass


if __name__ == "__main__":
    main()