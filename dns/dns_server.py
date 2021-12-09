from dnslib import RR, A
from dnslib.server import BaseResolver

# The resolver used to translate names into IP addresses
class DNSResolver(BaseResolver):

    # Constructor
    def __init__(self, geo_ip_locator, name):
        # Index used for round robin algorithm
        self.curr_address = 0
        self.geo_ip_locator = geo_ip_locator
        self.name = name

    def resolve(self, request, handler):
        """
        Try to get the closest IP to the client. If the request succeeds use this IP to redirect the client.
        If we fail to find the closest IP then redirect client towards the replica based on round-robin algorithm.
        """
        try:
            closest_ip = self.geo_ip_locator.get_closest_ip(handler.client_address[0])
        except Exception as ex:
            print("Resolve exception: ", ex)
            closest_ip = self.geo_ip_locator.replica_IPs[self.curr_address]
            # Increment the index to mimic round robin algorithm.
            self.curr_address = (self.curr_address + 1) % len(self.geo_ip_locator.replica_IPs)

        reply = request.reply()
        a = RR(self.name, rdata=A(closest_ip), ttl=0)
        reply.add_answer(a)
        return reply
