class ConfigError(Exception):
    """Error handling for the configuration data
    Raised for invalid config file of parsing """


class MazeWriteError(Exception):
    """Error due to error during the writting"""


class RenderError(Exception):
    """Redering Error to handle"""


class SolverError(Exception):
    """Solving Error : """
