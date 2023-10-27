class OctopusWFModuleInterface:
    """The routines that must be defined for an Octopus workflow"""

    @staticmethod
    def inp_string(*args, **kwargs) -> str:
        """Generate an Octopus input string from a dictionary"""
        ...

    def submission_script