import os
import subprocess
import atexit
import signal

from django.contrib.staticfiles.management.commands.runserver import Command\
    as StaticfilesRunserverCommand

from core.settings.utils import absolute_path


class Command(StaticfilesRunserverCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.grunt_process = None

    def inner_run(self, *args, **options):
        self.start_grunt()
        return super(Command, self).inner_run(*args, **options)

    def start_grunt(self):
        self.stdout.write('>>> Starting grunt')
        self.grunt_process = subprocess.Popen(
            ['grunt --gruntfile={0}/Gruntfile.js --base=.'.format(absolute_path())],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        self.stdout.write('>>> Grunt process on pid {0}'.format(self.grunt_process.pid))

        def kill_grunt_process(pid):
            self.stdout.write('>>> Closing grunt process')
            os.kill(pid, signal.SIGTERM)

        atexit.register(kill_grunt_process, self.grunt_process.pid)
