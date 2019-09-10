from modules.logs import Logs
from modules.plugin import Plugin
#from modules.report import ReportManager
from modules.requirements import Requires

@Requires()
class SoftPlugin(Plugin):
    """Base plugin for Software Analysis, does nothing."""

    # Define a plugin type
    ISSUE_TYPE = "SOFT_ISSUE_TYPE"

    def __init__(self, context):
        super(SoftPlugin, self).__init__(context)
        self._name = 'Software Analysis Plugin'
        self._console_msg = 'Name of your Software Analysis Plugin'
        self._activated = False
        self._size = 0

    def analyse(self, software, install_packages):
        """
        Start software analysis.

        :param software: Software information (retrieve by adb shell getprop)
        :param install_packages: installed packages list of the software
        :return: None
        """

      #  report_manager = ReportManager(self._context.get_root_path())
        Logs.instance().warning("\tImplement your SCA Plugin algorithm here!")
