class Plugin(object):

    def __init__(self, context):
        if context is None:
            raise ValueError('Context must be set')

        self._context = context
        self._name = 'Name of your plugin'
        self._console_msg = 'Console message to display when your plugin is used'
        self._activated = False
        self._size = 0  # tc spend time: 0(t<10s); 1(10<=t<60); 2(60<=t<300); 9(t>=300)

    def get_name(self):
        """
        Returns the name of the plugin
        :return:
        """
        return self._name

    def get_console_msg(self):
        """
        Returns a message to be displayed in the console when the plugin is used
        :return: Plugin Name
        """
        return self._console_msg

    def is_activated(self):
        """
        Indicate if the plugin is enabled or not.
        :return: Plugin state
        """
        return self._activated

    def is_compatible_with(self, data):
        """
        Indicates whether the plugin is compatible with the given data.
        Each plugin can implement its own compatibility rules.
        :param data: data to check compatibility against
        :return:
        """
        return True
