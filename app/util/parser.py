import argparse
import re


def parse_args(args):
    parser = argparse.ArgumentParser(add_help=True)
    # E.g., python main.py --profile prod --host 0.0.0.0 --port 5000
    #                     --db_url mysql://username:password@host:port/db)

    parser.add_argument('--profile',
                        action='store',
                        default=None,
                        help='the profile to choose from the YAML configurtion file')

    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Run in the Flask App in the debug mode')

    parser.add_argument('--log-level',
                        action='store',
                        default='INFO',
                        help='Specify the log level of the application')

    parser.add_argument('--host',
                        action='store',
                        default=None,
                        help='The hostname to listen on.')

    parser.add_argument('--port',
                        action='store',
                        type=int,
                        default=None,
                        help='The port to listen on.')

    parser.add_argument('--db-url',
                        default=None,
                        action='store',
                        help='mysql db url (mysql://username:password@host:port/db)')

    parser.add_argument('--create-fmus',
                        action='store_true',
                        default=False,
                        help='whether to create FMUs on disk or not')

    return parser.parse_args(args)


def parse_modelica_file(file_path):
    package_name = None
    models = []

    # ignore comments (lines begining with //)
    pattern = re.compile("^\s*//.*")

    with open(file_path, 'r') as fil:
        for line in fil:
            if pattern.match(line):  # ignore if comment
                continue
            if "package" in line:
                package_name = line.split()[1]
            if "extends" in line:
                models.append(line.split()[1])
    return package_name, models
