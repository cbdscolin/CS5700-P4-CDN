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
        for replica_ip in self.geo_ip_locator.replica_IPs:
            request = urllib.request.Request("http://" + replica_ip + ":40002/")
            request.add_header("Accept-Encoding", "utf-8")

            start_time = time.time()
            try:
                urllib.request.urlopen(request, timeout=self.REQUEST_TIMEOUT_SECONDS)
                continue
            except:
                pass
            end_time = time.time()

            self.initial_times.append((end_time - start_time))
            self.current_times.append((end_time - start_time))

        self.next_load_check_time = time.time() + self.load_check_interval_seconds

    def should_check_load(self):
        if self.geo_ip_locator.dns_location is None:
            return False
        now_time = time.time()
        if now_time >= self.next_load_check_time:
            return True
        return False

    def check_load_on_replicas(self):
        self.next_load_check_time = time.time() + self.load_check_interval_seconds
        for ii, replica_ip in enumerate(self.geo_ip_locator.replica_IPs):
            request = urllib.request.Request("http://" + replica_ip + ":40002/")
            request.add_header("Accept-Encoding", "utf-8")

            start_time = time.time()
            try:
                urllib.request.urlopen(request)
                continue
            except:
                pass
            end_time = time.time()

            time_taken = (end_time - start_time)

            # Lower request time than the initially recorded time means this replica can do better than when the load
            # was initially measured.
            if self.initial_times[ii] > time_taken:
                self.initial_times[ii] = time_taken

            self.current_times[ii] = time_taken

        self.update_bad_replicas()

    def is_load_higher_at_replica(self, replica_index):
        load_diff = float(self.current_times[replica_index] - self.initial_times[replica_index])
        if load_diff > 3.5 or self.current_times[replica_index] >= self.REQUEST_TIMEOUT_SECONDS:
            return True
        return False

    def update_bad_replicas(self):
        bad_replicas = []
        for ii in range(len(self.geo_ip_locator.replica_IPs)):
            if self.is_load_higher_at_replica(ii) is True:
                bad_replicas.append(ii)
        self.bad_replicas = bad_replicas

    def get_bad_replicas(self):
        if self.should_check_load() is True:
            self.check_load_on_replicas()

        return self.bad_replicas



