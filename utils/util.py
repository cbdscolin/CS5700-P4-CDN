class Utils:

    @staticmethod
    def print_logs(*log_lines):
        res = ""
        for log in log_lines:
            res += str(log)
        #print res

    @staticmethod
    def save_file(filename, contents):
        f = open(filename, "wb")
        f.write(contents)
        f.close()

    @staticmethod
    def get_file_contents(filename):
        f = open(filename, "rb")
        contents = f.read()
        return contents