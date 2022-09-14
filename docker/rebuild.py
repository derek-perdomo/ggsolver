import os


class BColors:
    """
    # Reference: https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ColoredMsg:
    @staticmethod
    def ok(msg):
        return f"{BColors.OKCYAN}{msg}{BColors.ENDC}"

    @staticmethod
    def warn(msg):
        return f"{BColors.WARNING}{msg}{BColors.ENDC}"

    @staticmethod
    def success(msg):
        return f"{BColors.OKGREEN}{msg}{BColors.ENDC}"

    @staticmethod
    def error(msg):
        return f"{BColors.FAIL}{msg}{BColors.ENDC}"

    @staticmethod
    def header(msg):
        return f"{BColors.HEADER}{msg}{BColors.ENDC}"


if __name__ == '__main__':
    # Update ggsolver:latest image.
    code = os.system(f"docker build -t abhibp1993/ggsolver:latest docker\latest")
    if code == 0:
        print(ColoredMsg.success(f"SUCCESS!! updated ggsolver:latest image"))
    else:
        print(ColoredMsg.error(f"PROBLEMS!! Did NOT update ggsolver:latest image"))

    # Update ggsolver:devel image.
    print(os.system(f"docker build -t abhibp1993/ggsolver:devel docker\devel"))
    if code == 0:
        print(ColoredMsg.success(f"SUCCESS!! updated ggsolver:devel image"))
    else:
        print(ColoredMsg.error(f"PROBLEMS!! Did NOT update ggsolver:devel image"))

    # Push ggsolver:latest image.
    print(os.system(f"docker push abhibp1993/ggsolver:devel"))
    if code == 0:
        print(ColoredMsg.success(f"SUCCESS!! Pushed ggsolver:latest image"))
    else:
        print(ColoredMsg.error(f"PROBLEMS!! Did NOT push ggsolver:latest image"))

    # Push ggsolver:devel image.
    print(os.system(f"docker push abhibp1993/ggsolver:latest"))
    if code == 0:
        print(ColoredMsg.success(f"SUCCESS!! Pushed ggsolver:devel image"))
    else:
        print(ColoredMsg.error(f"PROBLEMS!! Did NOT push ggsolver:devel image"))
