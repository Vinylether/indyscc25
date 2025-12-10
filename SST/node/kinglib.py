import sst
from sst import UnitAlgebra
from mhlib import *
from vanadislib import *

### Note: This module is being used to prototype a set of python utilities
###  for more easily generating and configuring simulations using kingsley.
###  Feel free to use the utilities available here but be aware that this file
###  may change without warning in the SST-Elements repository.
###
### Eventually, a python module with convenience functions for memHierarchy will be released
###  and that module will be fully supported by the project (provide backwards compatibility,
###  deprecation notices, stability testing).
###


# Needed parameters
# frequency, flit size, cycles per hop (x, y, local)
# Defaults:
# - Frequency most likely to change
# - ctrl_flit_size : 8B for address, type, a few bits of info
# - router_buffer_entries: 2 is minimum
# - nic_input_buffer_entries: 2 is minimum
# - nic_output_buffer_entries: 2 is minimum
# - route_y_first: some networks to x-first, others y-first
# - equal_port_priority: by default, local ports have higher priority than network
# - link_bandwidth (data) =  frequency * data_flit_size (72GB/s default)
class KingsleyMesh:
    def __init__(self, prefix, xdim, ydim, 
                 x_hop_cycles=1, y_hop_cycles=1, local_hop_cycles=1,
                 frequency="2GHz", ctrl_flit_size="8B", data_flit_size="36B",
                 router_buffer_entries=2, nic_input_buffer_entries=2, nic_output_buffer_entries=2,
                 route_y_first=False, equal_port_priority=False):
        
        self.prefix = prefix
        self.xdim = xdim
        self.ydim = ydim
        self.req_net = []   # Routers on request network
        self.ack_net = []   # Routers on ack network
        self.data_net = []  # Routers on data network
        self.fwd_net = []   # Routers on forward network
        self.local_ports = [] # Count of local ports used on each router
        self.groups = []   # Track which cache level groups exist on the network
        self.dir_nics = [] # Keep list of directory NICs for finalize()
        self.mem_nics = [] # Keep list of memory NICs for finalize()
        self.linknum = 0 # Used to generate unique link names

        # Compute link latency based on mesh frequency and cycles per hop
        frequa = UnitAlgebra(frequency)
        self.local_hop_latency = UnitAlgebra(str(local_hop_cycles)) * frequa
        x_hop_latency = UnitAlgebra(str(x_hop_cycles)) * frequa
        y_hop_latency = UnitAlgebra(str(y_hop_cycles)) * frequa

        # Compute mesh bandwidths based on frequency and flit size
        ctrl_link_bw = frequa * UnitAlgebra(ctrl_flit_size)
        data_link_bw = frequa * UnitAlgebra(data_flit_size)

        ctrl_net_params = {
            "link_bw" : ctrl_link_bw,
            "flit_size" : ctrl_flit_size,
            "input_buf_size" : UnitAlgebra(str(router_buffer_entries)) * UnitAlgebra(ctrl_flit_size),
            "port_priority_equal" : equal_port_priority,
            "route_y_first" : route_y_first
        }
        data_net_params = {
            "link_bw" : data_link_bw,
            "flit_size" : data_flit_size,
            "input_buf_size" : UnitAlgebra(str(router_buffer_entries)) * UnitAlgebra(data_flit_size),
            "port_priority_equal" : equal_port_priority,
            "route_y_first" : route_y_first
        }
        self.ctrl_nic_params = {
            "link_bw" : ctrl_link_bw,
            "in_buf_size" : UnitAlgebra(str(nic_input_buffer_entries)) * UnitAlgebra(ctrl_flit_size),
            "out_buf_size" : UnitAlgebra(str(nic_output_buffer_entries)) * UnitAlgebra(ctrl_flit_size),
        }
        self.data_nic_params = {
            "link_bw" : data_link_bw,
            "in_buf_size" : UnitAlgebra(str(nic_input_buffer_entries)) * UnitAlgebra(data_flit_size),
            "out_buf_size" : UnitAlgebra(str(nic_output_buffer_entries)) * UnitAlgebra(data_flit_size),
        }

        # Build routers row by row
        for y in range (0, ydim):
            for x in range (0, xdim):
                node_num = len(self.req_net)
                self.req_net.append(sst.Component(prefix + "_req" + str(node_num), "kingsley.noc_mesh"))
                self.req_net[-1].addParams(ctrl_net_params)
                self.ack_net.append(sst.Component(prefix + "_ack" + str(node_num), "kingsley.noc_mesh"))
                self.ack_net[-1].addParams(ctrl_net_params)
                self.fwd_net.append(sst.Component(prefix + "_fwd" + str(node_num), "kingsley.noc_mesh"))
                self.fwd_net[-1].addParams(ctrl_net_params)
                self.data_net.append(sst.Component(prefix + "_data" + str(node_num), "kingsley.noc_mesh"))
                self.data_net[-1].addParams(data_net_params)
                self.local_ports.append(0)

                # North-south connections
                if y != 0:
                    req_ns = sst.Link(prefix + "rns" + str(node_num))
                    req_ns.connect( (self.req_net[node_num - xdim], "south", x_hop_latency), (self.req_net[node_num], "north", x_hop_latency) )
                    ack_ns = sst.Link(prefix + "ans" + str(node_num))
                    ack_ns.connect( (self.ack_net[node_num - xdim], "south", x_hop_latency), (self.ack_net[node_num], "north", x_hop_latency) )
                    fwd_ns = sst.Link(prefix + "fns" + str(node_num))
                    fwd_ns.connect( (self.fwd_net[node_num - xdim], "south", x_hop_latency), (self.fwd_net[node_num], "north", x_hop_latency) )
                    data_ns = sst.Link(prefix + "dns" + str(node_num))
                    data_ns.connect( (self.data_net[node_num - xdim], "south", x_hop_latency), (self.data_net[node_num], "north", x_hop_latency) )
                
                # East-west connections
                if x != 0:
                    req_ew = sst.Link(prefix + "rew" + str(node_num))
                    req_ew.connect( (self.req_net[node_num - 1], "east", y_hop_latency), (self.req_net[node_num], "west", y_hop_latency) )
                    ack_ew = sst.Link(prefix + "aew" + str(node_num))
                    ack_ew.connect( (self.ack_net[node_num - 1], "east", y_hop_latency), (self.ack_net[node_num], "west", y_hop_latency) )
                    fwd_ew = sst.Link(prefix + "few" + str(node_num))
                    fwd_ew.connect( (self.fwd_net[node_num - 1], "east", y_hop_latency), (self.fwd_net[node_num], "west", y_hop_latency) )
                    data_ew = sst.Link(prefix + "dew" + str(node_num))
                    data_ew.connect( (self.data_net[node_num - 1], "east", y_hop_latency), (self.data_net[node_num], "west", y_hop_latency) )

    def connectCache(self, cachelevel : CacheLevel, port : str, connectivity, debug=0):
        if port != "highlink" and port != "lowlink":
            raise Exception("Error: In connectCache(), the port must be either 'highlink' or 'lowlink'.\n"
                  "To connect caches that have no direct connections to other memory or core/accelerator components, use 'highlink'\n"
                  "To connect caches that are directly connected to cores or upper-level caches, use 'lowlink' (e.g., a private L2 that is connected directly to an L1)\n"
                  "To connect caches that are directly connected to lower-level caches, directories, or memories, use 'highlink' (e.g., an L3 that is directly connected to memory)\n"
                  "In the above descriptions, 'directly connected' means connected via a bus or a dedicated channel - not over a network\n")

        if isinstance(connectivity, int):
            connectivity_map = [0] * len(self.data_net)
            connectivity_map[connectivity] = 1
        else:
            connectivity_map = connectivity

        if len(connectivity_map) != len(self.data_net):
            raise Exception("Error: The length of the connectivity map does not equal the size (number of routers) of the network. "
                            "Ensure that the map has an entry for each network router so that len(connectivity) = {}.".format(self.xdim * self.ydim))
        
        if sum(connectivity_map) != len(cachelevel.caches):
            raise Exception("Error: The number of connections in the connectivity map ({}) does not match the number of caches in the cachelevel ({}). "
                            "Ensure sum(connectivity) == len(cachelevel.caches).".format(sum(connectivity_map), len(cachelevel.caches)))


        # Connect network subcomponents according to connectivity map
        # Update local_port count
        rtr = 0
        rtr_slots = connectivity_map[rtr]
        self.groups.append(cachelevel.level) # In finalize, we'll make sure the last level dir and/or mem have the right level
        
        for cache in cachelevel.caches:
            # Install network subcomponents on each cache
            nic = cache.setSubComponent(port, "memHierarchy.MemNICFour")
            nic.addParam("group", cachelevel.level)
            if debug > 0:
                nic.addParam("debug", 1)
                nic.addParam("debug_level", debug)
            data_chan = nic.setSubComponent("data", "kingsley.linkcontrol")
            data_chan.addParams(self.data_nic_params)
            req_chan = nic.setSubComponent("req", "kingsley.linkcontrol")
            req_chan.addParams(self.ctrl_nic_params)
            ack_chan = nic.setSubComponent("ack", "kingsley.linkcontrol")
            ack_chan.addParams(self.ctrl_nic_params)
            fwd_chan = nic.setSubComponent("fwd", "kingsley.linkcontrol")
            fwd_chan.addParams(self.ctrl_nic_params)

            # Update rtr to point to the router we need to populate
            while rtr_slots == 0:
                rtr += 1
                rtr_slots = connectivity_map[rtr]

            # Connect linkcontrols according to connectivity_map
            dlink = sst.Link( self.prefix + str(self.linknum) )
            rlink = sst.Link( self.prefix + str(self.linknum + 1) )
            alink = sst.Link( self.prefix + str(self.linknum + 2) )
            flink = sst.Link( self.prefix + str(self.linknum + 3) )
            self.linknum += 4
            local_port = "local" + str(self.local_ports[rtr])
            dlink.connect( (self.data_net[rtr], local_port, self.local_hop_latency), 
                           (data_chan, "rtr_port", self.local_hop_latency) )
            rlink.connect( (self.req_net[rtr], local_port, self.local_hop_latency), 
                           (req_chan, "rtr_port", self.local_hop_latency) )
            alink.connect( (self.ack_net[rtr], local_port, self.local_hop_latency), 
                           (ack_chan, "rtr_port", self.local_hop_latency) )
            flink.connect( (self.fwd_net[rtr], local_port, self.local_hop_latency), 
                           (fwd_chan, "rtr_port", self.local_hop_latency) )
            self.local_ports[rtr] += 1
            rtr_slots -= 1
    
    def connectVanadisCores(self, cores : Vanadis, connectivity, os_router=0, debug=0):
        if isinstance(connectivity, int):
            connectivity_map = [0] * len(self.data_net)
            connectivity_map[connectivity] = 1
        else:
            connectivity_map = connectivity       

        if cores.l2:
            # Connect L2
            self.connectCache(cores.l2, "lowlink", connectivity_map)
        else:
            # Connect L1I and L1D to network, connect OS at rtr 0
            if len(connectivity_map) != len(self.data_net):
                raise Exception("Error: The length of the connectivity map does not equal the size (number of routers) of the network. "
                                "Ensure that the map has an entry for each network router so that len(connectivity) = {}.".format(self.xdim * self.ydim))

            if cores.l1d == None or cores.l1i == None:
                raise Exception("Error: Either L1D or L1I caches do not exist; cannot connect them")
            if sum(connectivity_map) != len(cores.l1d):
                raise Exception("Error: The number of connections in the connectivity map ({}) does not match the number of caches in the cachelevel ({}). "
                                "Ensure sum(connectivity) == len(cachelevel.caches).".format(sum(connectivity_map), len(cores.l1d)))

            # Connect network subcomponents according to connectivity map
            # Update local_port count
            rtr = 0
            rtr_slots = connectivity_map[rtr]
            self.groups.append(cores.l1d.level)
        
            for num in range(0, len(cores.l1d)):
                # Install network subcomponents on each cache
                nic_l1d = cores.l1d.caches[num].setSubComponent("lowlink", "memHierarchy.MemNICFour")
                nic_l1i = cores.l1i.caches[num].setSubComponent("lowlink", "memHierarchy.MemNICFour")
                nic_l1d.addParam("group", cores.l1d.level)
                nic_l1i.addParam("group", cores.l1i.level)
                if debug > 0:
                    nic_l1d.addParam("debug", 1)
                    nic_l1d.addParam("debug_level", debug)
                    nic_l1i.addParam("debug", 1)
                    nic_l1i.addParam("debug_level", debug)
                data_chan_l1d = nic_l1d.setSubComponent("data", "kingsley.linkcontrol")
                data_chan_l1d.addParams(self.data_nic_params)
                req_chan_l1d = nic_l1d.setSubComponent("req", "kingsley.linkcontrol")
                req_chan_l1d.addParams(self.ctrl_nic_params)
                ack_chan_l1d = nic_l1d.setSubComponent("ack", "kingsley.linkcontrol")
                ack_chan_l1d.addParams(self.ctrl_nic_params)
                fwd_chan_l1d = nic_l1d.setSubComponent("fwd", "kingsley.linkcontrol")
                fwd_chan_l1d.addParams(self.ctrl_nic_params)
                data_chan_l1i = nic_l1i.setSubComponent("data", "kingsley.linkcontrol")
                data_chan_l1i.addParams(self.data_nic_params)
                req_chan_l1i = nic_l1i.setSubComponent("req", "kingsley.linkcontrol")
                req_chan_l1i.addParams(self.ctrl_nic_params)
                ack_chan_l1i = nic_l1i.setSubComponent("ack", "kingsley.linkcontrol")
                ack_chan_l1i.addParams(self.ctrl_nic_params)
                fwd_chan_l1i = nic_l1i.setSubComponent("fwd", "kingsley.linkcontrol")
                fwd_chan_l1i.addParams(self.ctrl_nic_params)

                # Update rtr to point to the router we need to populate
                while rtr_slots == 0:
                    rtr += 1
                    rtr_slots = connectivity_map[rtr]

                # Connect linkcontrols according to connectivity_map
                dlink_l1d = sst.Link( self.prefix + str(self.linknum) )
                rlink_l1d = sst.Link( self.prefix + str(self.linknum + 1) )
                alink_l1d = sst.Link( self.prefix + str(self.linknum + 2) )
                flink_l1d = sst.Link( self.prefix + str(self.linknum + 3) )
                dlink_l1i = sst.Link( self.prefix + str(self.linknum + 4) )
                rlink_l1i = sst.Link( self.prefix + str(self.linknum + 5) )
                alink_l1i = sst.Link( self.prefix + str(self.linknum + 6) )
                flink_l1i = sst.Link( self.prefix + str(self.linknum + 7) )
                self.linknum += 8
                local_port_l1d = "local" + str(self.local_ports[rtr])
                local_port_l1i = "local" + str(self.local_ports[rtr] + 1)
                dlink_l1d.connect( (self.data_net[rtr], local_port_l1d, self.local_hop_latency), 
                                   (data_chan_l1d, "rtr_port", self.local_hop_latency) )
                rlink_l1d.connect( (self.req_net[rtr], local_port_l1d, self.local_hop_latency), 
                           (req_chan_l1d, "rtr_port", self.local_hop_latency) )
                alink_l1d.connect( (self.ack_net[rtr], local_port_l1d, self.local_hop_latency), 
                           (ack_chan_l1d, "rtr_port", self.local_hop_latency) )
                flink_l1d.connect( (self.fwd_net[rtr], local_port_l1d, self.local_hop_latency), 
                           (fwd_chan_l1d, "rtr_port", self.local_hop_latency) )
                dlink_l1i.connect( (self.data_net[rtr], local_port_l1i, self.local_hop_latency), 
                           (data_chan_l1i, "rtr_port", self.local_hop_latency) )
                rlink_l1i.connect( (self.req_net[rtr], local_port_l1i, self.local_hop_latency), 
                           (req_chan_l1i, "rtr_port", self.local_hop_latency) )
                alink_l1i.connect( (self.ack_net[rtr], local_port_l1i, self.local_hop_latency), 
                           (ack_chan_l1i, "rtr_port", self.local_hop_latency) )
                flink_l1i.connect( (self.fwd_net[rtr], local_port_l1i, self.local_hop_latency), 
                           (fwd_chan_l1i, "rtr_port", self.local_hop_latency) )
                self.local_ports[rtr] += 2
                rtr_slots -= 1
        
        # Connect OS cache
        self.connectCache(cores.l1_os, "lowlink", os_router)

    def connectDistributedCache(self, cachelevel : CacheLevel, connectivity_map, debug=0): 
        if len(connectivity_map) != len(self.data_net):
            raise Exception("Error: The length of the connectivity map does not equal the size (number of routers) of the network. "
                            "Ensure that the map has an entry for each network router so that len(connectivity) = {}.".format(self.xdim * self.ydim))
        
        if sum(connectivity_map) != len(cachelevel.caches):
            raise Exception("Error: The number of connections in the connectivity map ({}) does not match the number of caches in the cachelevel ({}). "
                            "Ensure sum(connectivity) == len(cachelevel.caches).".format(sum(connectivity_map), len(cachelevel.caches)))

        # Connect network subcomponents according to connectivity map
        # Update local_port count
        rtr = 0
        rtr_slots = connectivity_map[rtr]
        self.groups.append(cachelevel.level)
        
        for cache in cachelevel.caches:
            # Install network subcomponents on each cache
            nic = cache.setSubComponent("highlink", "memHierarchy.MemNICFour")
            nic.addParam("group", cachelevel.level)
            if debug > 0:
                nic.addParam("debug", 1)
                nic.addParam("debug_level", debug)
            data_chan = nic.setSubComponent("data", "kingsley.linkcontrol")
            data_chan.addParams(self.data_nic_params)
            req_chan = nic.setSubComponent("req", "kingsley.linkcontrol")
            req_chan.addParams(self.ctrl_nic_params)
            ack_chan = nic.setSubComponent("ack", "kingsley.linkcontrol")
            ack_chan.addParams(self.ctrl_nic_params)
            fwd_chan = nic.setSubComponent("fwd", "kingsley.linkcontrol")
            fwd_chan.addParams(self.ctrl_nic_params)

            # Update rtr to point to the router we need to populate
            while rtr_slots == 0:
                rtr += 1
                rtr_slots = connectivity_map[rtr]

            # Connect linkcontrols according to connectivity_map
            dlink = sst.Link( self.prefix + str(self.linknum) )
            rlink = sst.Link( self.prefix + str(self.linknum + 1) )
            alink = sst.Link( self.prefix + str(self.linknum + 2) )
            flink = sst.Link( self.prefix + str(self.linknum + 3) )
            self.linknum += 4
            local_port = "local" + str(self.local_ports[rtr])
            dlink.connect( (self.data_net[rtr], local_port, self.local_hop_latency), 
                           (data_chan, "rtr_port", self.local_hop_latency) )
            rlink.connect( (self.req_net[rtr], local_port, self.local_hop_latency), 
                           (req_chan, "rtr_port", self.local_hop_latency) )
            alink.connect( (self.ack_net[rtr], local_port, self.local_hop_latency), 
                           (ack_chan, "rtr_port", self.local_hop_latency) )
            flink.connect( (self.fwd_net[rtr], local_port, self.local_hop_latency), 
                           (fwd_chan, "rtr_port", self.local_hop_latency) )
            self.local_ports[rtr] += 1
            rtr_slots -= 1   


    def connectMemory(self, memories : Memory, connectivity, debug=0):
        if isinstance(connectivity, int):
            connectivity_map = [0] * len(self.data_net)
            connectivity_map[connectivity] = 1
        else:
            connectivity_map = connectivity

        if len(connectivity_map) != len(self.data_net):
            raise Exception("Error: The length of the connectivity map does not equal the size (number of routers) of the network. "
                            "Ensure that the map has an entry for each network router so that len(connectivity) = {}.".format(self.xdim * self.ydim))
        
        if sum(connectivity_map) != len(memories.controllers):
            raise Exception("Error: The number of connections in the connectivity map ({}) does not match the number of memories ({}). "
                            "Ensure sum(connectivity) == len(memories.controllers).".format(sum(connectivity_map), len(memories.controllers)))

        # Connect network subcomponents according to connectivity map
        # Update local_port count
        rtr = 0
        rtr_slots = connectivity_map[rtr]

        for controller in memories.controllers:
            # Install network subcomponents on each memory
            nic = controller.setSubComponent("highlink", "memHierarchy.MemNICFour")
            self.mem_nics.append(nic)
            if debug > 0:
                nic.addParam("debug", 1)
                nic.addParam("debug_level", debug)
            data_chan = nic.setSubComponent("data", "kingsley.linkcontrol")
            data_chan.addParams(self.data_nic_params)
            req_chan = nic.setSubComponent("req", "kingsley.linkcontrol")
            req_chan.addParams(self.ctrl_nic_params)
            ack_chan = nic.setSubComponent("ack", "kingsley.linkcontrol")
            ack_chan.addParams(self.ctrl_nic_params)
            fwd_chan = nic.setSubComponent("fwd", "kingsley.linkcontrol")
            fwd_chan.addParams(self.ctrl_nic_params)

            # Update rtr to point to the router we need to populate
            while rtr_slots == 0:
                rtr += 1
                rtr_slots = connectivity_map[rtr]

            # Connect linkcontrols according to connectivity_map
            dlink = sst.Link( self.prefix + str(self.linknum) )
            rlink = sst.Link( self.prefix + str(self.linknum + 1) )
            alink = sst.Link( self.prefix + str(self.linknum + 2) )
            flink = sst.Link( self.prefix + str(self.linknum + 3) )
            self.linknum += 4
            port = "local" + str(self.local_ports[rtr])
            dlink.connect( (self.data_net[rtr], port, self.local_hop_latency), 
                           (data_chan, "rtr_port", self.local_hop_latency) )
            rlink.connect( (self.req_net[rtr], port, self.local_hop_latency), 
                           (req_chan, "rtr_port", self.local_hop_latency) )
            alink.connect( (self.ack_net[rtr], port, self.local_hop_latency), 
                           (ack_chan, "rtr_port", self.local_hop_latency) )
            flink.connect( (self.fwd_net[rtr], port, self.local_hop_latency), 
                           (fwd_chan, "rtr_port", self.local_hop_latency) )
            self.local_ports[rtr] += 1
            rtr_slots -= 1
        

    # Final call to finish construction network
    def finalize(self):
        local_ports = max(self.local_ports)
        for i in range(0, len(self.req_net)):
            self.req_net[i].addParam("local_ports", local_ports)
            self.ack_net[i].addParam("local_ports", local_ports)
            self.fwd_net[i].addParam("local_ports", local_ports)
            self.data_net[i].addParam("local_ports", local_ports)
        
        max_level = max(self.groups) + 1
        if len(self.dir_nics) > 0:
            for nic in self.dir_nics:
                nic.addParam("group", max_level)
            max_level += 1
        
        if len(self.mem_nics) > 0:
            for nic in self.mem_nics:
                nic.addParam("group", max_level)
