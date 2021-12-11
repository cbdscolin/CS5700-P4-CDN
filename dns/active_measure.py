import os
import time
import urllib

class LoadMeasurer:

    REQUEST_TIMEOUT_SECONDS = 4

    def __init__(self, locator, load_check_interval_seconds):
        self.geo_ip_locator = locator
        self.load_check_interval_seconds = load_check_interval_seconds
        self.initial_times = []
        self.current_times = []
        self.bad_replicas = []

        self.replica_ratings = {}
        self.check_load()

        self.next_load_check_time = time.time() + self.load_check_interval_seconds

    def check_load(self):
        replica_ip_str = ""
        for ip in self.geo_ip_locator.replica_IPs:
            replica_ip_str += " -i " + ip
        cmd = os.popen('timeout 7s scamper -c "trace -d 40002 -P TCP "' + replica_ip_str)
        out = cmd.read()
        cmd.close()
        ip_logs = out.split("traceroute")
        replica_ip_ratings_pairs = {}
        for single_ip_log in ip_logs:
            single_ip_log = single_ip_log.strip()
            if single_ip_log == "":
                continue
            ip_log_lines = single_ip_log.split("\n")
            replica_ip = ip_log_lines[0].split("to")[1].strip()
            ratings = 0
            if len(ip_log_lines) > 0:
                # last hop has star
                if "*" in ip_log_lines[len(ip_log_lines) - 1]:
                    ratings = -2
                else:
                    for single_ip_log_line in ip_log_lines:
                        if "*" in single_ip_log_line:
                            ratings = -1
                            break

            replica_ip_ratings_pairs[replica_ip] = ratings

        for rep_ip in self.geo_ip_locator.replica_IPs:
            if rep_ip not in replica_ip_ratings_pairs:
                replica_ip_ratings_pairs[rep_ip] = -2

        self.next_load_check_time = time.time() + self.load_check_interval_seconds

        self.replica_ratings = replica_ip_ratings_pairs

    def should_check_load(self):
        now_time = time.time()
        if now_time >= self.next_load_check_time:
            return True
        return False

    def is_load_higher_at_replica(self, replica_index):
        load_diff = float(self.current_times[replica_index] - self.initial_times[replica_index])
        if load_diff > 3.5 or self.current_times[replica_index] >= self.REQUEST_TIMEOUT_SECONDS:
            return True
        return False

    def get_replica_ratings(self):
        if self.should_check_load() is True:
            self.check_load()

        return self.replica_ratings



