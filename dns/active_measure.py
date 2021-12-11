import os
import time
import urllib

# Class that has logic to perform active measurements using scamper
class LoadMeasurer:

    # Unused
    REQUEST_TIMEOUT_SECONDS = 4

    def __init__(self, locator, load_check_interval_seconds):
        # Cache instance of geo ip locator.
        self.geo_ip_locator = locator
        # Interval between 2 scamper probes
        self.load_check_interval_seconds = load_check_interval_seconds
        # Unused
        self.initial_times = []
        self.current_times = []
        self.bad_replicas = []

        # Used to store ratings of the replicas based on their load.
        # 0 indicates normal load, -1 indicates high load, -2 indicates extremely high load.
        self.replica_ratings = {}
        # Check load initially.
        self.check_load()

        # Used to control when the load check has to happen.
        self.next_load_check_time = time.time() + self.load_check_interval_seconds

    def check_load(self):
        replica_ip_str = ""
        # Run scamper command to probe replica IPs
        for ip in self.geo_ip_locator.replica_IPs:
            replica_ip_str += " -i " + ip
        cmd = os.popen('timeout 7s scamper -c "trace -d 40002 -P TCP "' + replica_ip_str)
        out = cmd.read()
        cmd.close()
        # Parse scamper output
        ip_logs = out.split("traceroute")
        replica_ip_ratings_pairs = {}
        for single_ip_log in ip_logs:
            single_ip_log = single_ip_log.strip()
            if single_ip_log == "":
                continue
            ip_log_lines = single_ip_log.split("\n")
            # Parse replica ip
            replica_ip = ip_log_lines[0].split("to")[1].strip()
            ratings = 0
            if len(ip_log_lines) > 0:
                # last hop has star which means the replica was unreachable.
                if "*" in ip_log_lines[len(ip_log_lines) - 1]:
                    ratings = -2
                else:
                    # a star in one of the hops means the replica was reachable but some packets were probably lost.
                    for single_ip_log_line in ip_log_lines:
                        if "*" in single_ip_log_line:
                            ratings = -1
                            break

            replica_ip_ratings_pairs[replica_ip] = ratings

        # Handle the case when scamper output has missing information about some replicas. This might have happened due
        # to timeout.
        for rep_index, rep_id in enumerate(self.geo_ip_locator.replica_IPs):
            if rep_id not in replica_ip_ratings_pairs:
                # If there is no distance information between dns and replica then assume the replica is working
                if rep_index >= len(self.geo_ip_locator.distance_to_replicas):
                    replica_ip_ratings_pairs[rep_id] = 0
                # If the replica is far away from the dns server then assume its up and running
                elif self.geo_ip_locator.distance_to_replicas[rep_index] > 12000:
                    replica_ip_ratings_pairs[rep_id] = 0
                # If the replica is close by and there is no output in scamper assume its down.
                else:
                    replica_ip_ratings_pairs[rep_id] = -2

        # Check load again after this time
        self.next_load_check_time = time.time() + self.load_check_interval_seconds
        # Cache replica ratings.
        self.replica_ratings = replica_ip_ratings_pairs

    # Function to check if scamper should be run or not
    def should_check_load(self):
        now_time = time.time()
        if now_time >= self.next_load_check_time:
            return True
        return False

    # Unused function.
    def is_load_higher_at_replica(self, replica_index):
        load_diff = float(self.current_times[replica_index] - self.initial_times[replica_index])
        if load_diff > 3.5 or self.current_times[replica_index] >= self.REQUEST_TIMEOUT_SECONDS:
            return True
        return False

    # Return cached replica ratings.
    def get_replica_ratings(self):
        if self.should_check_load() is True:
            self.check_load()

        return self.replica_ratings



