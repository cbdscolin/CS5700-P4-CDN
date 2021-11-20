# CS5700-P4-CDN

Our high-level approach was to implement the DNS server and the HTTP server separately initially. For the DNS server, we researched dnslib, and implemented a basic DNS server with a DNS resolver. This DNS resolver is designed to take in requests for the origin server, cs5700cdnorigin.ccs.neu.edu, and respond with a round robin approach given the list of possible replica servers. 