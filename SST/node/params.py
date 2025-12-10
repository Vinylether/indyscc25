from sst import UnitAlgebra
import random

## Allowed params and their definitions
arg_cores = {32 : "6x6", 64 : "8x8"}
arg_speed = {"slow" : ["1.8GHz", "1.2GHz", 12], # Core, uncore, mem reqs @ L1
             "medium" : ["2.5GHz", "1.8GHz", 16], 
             "fast" : ["3.8GHz", "2.2GHz", 24]}
arg_smt = {"no" : 1, "yes" : 2}
arg_l1size = { "small" : ["32KiB", 8, 1], "big" : ["48KiB", 16, 4] }
arg_l2size = { "small" : ["128KiB", 8, 5], "big" : ["512KiB", 16, 7]}
arg_l3size = { "small" : ["1MiB", 16, 10], "big" : ["2MiB", 32, 14]}
arg_l2org = ["private","shared"]
arg_noc = { "slow" : "1.6GHz","fast" : "2.2GHz" }
arg_memchan = [6,8]
arg_memtype = { 
    "basic" : { "max_requests_per_cycle" : 1, 
                "cycle_time" : "3200MHz", 
                "banks" : 16,
                "tCAS" : 48, "tRCD" : 30, "tRP" : 21 },
    "bw" : { "max_requests_per_cycle" : 2,
             "cycle_time" : "3200MHz",
             "banks" : 32,
             "tCAS" : 48, "tRCD" : 30, "tRP" : 21 },
}

# Memories are located on the mesh edges
memory_layouts = {
    32 : {
        6 : [ 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0 ],
        8 : [ 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
              1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0 ]
    },
    64 : {
        6 : [ 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
              0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0 ],
        8 : [ 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0 ]
    }
}

# Costs
arg_core_cost = { "slow" : 30, "medium" : 48, "fast" : 96 }
arg_smt_cost = { "no" : 1.0, "yes" : 1.7 }
arg_l1_cost = { "small" : 22, "big" : 28 }
arg_l2_cost = { "small" : 14, "big" : 20 }
arg_l3_cost = { "small" : 20, "big" : 36 }
arg_l2o_cost = { "private" : 0, "shared" : 4 }
arg_noc_cost = { "slow" : 6, "fast" : 16 }
arg_mem_cost = { "basic" : 110, "bw" : 200 }


###########################################
# Helper functions for configuration

# Removes the 'count' indices from connection_map. 
# Seed random before calling to make this deterministic.
def mask(connection_map : list, count : int, info=""):
    total = sum(connection_map)
    mask_set = random.sample(range(0,total), count)
    mask_set.sort()
    if info != "":
        print("Masked set for {}: {}".format(info, mask_set))

    index = 0
    value = connection_map[index]
    for x in mask_set:
        while x > value:
            index += 1
            value += connection_map[index]
        
        connection_map[index] -= 1
            
    return connection_map

# Class containing meta parameters for SST configuration
# This can be modified by passing parameters to the constructor
class ChipConfig:
    # Init simply sets the 'meta' parameters
    def __init__(self, core_count, core_type, smt, l1size, l2size, l3size, 
                 l2org, noc, memchan, memtype):
        
        # --------------------------------------------#
        ### Cost Model                              ###
        # --------------------------------------------#
        self.per_core_cost = arg_core_cost[core_type] * arg_smt_cost[smt]
        self.per_core_cost += (arg_l1_cost[l1size] + arg_l2_cost[l2size] + arg_l3_cost[l3size] + arg_l2o_cost[l2org] + arg_noc_cost[noc])
        self.per_mem_cost = arg_mem_cost[memtype]        
        
        # --------------------------------------------#
        ### General System                          ###
        # --------------------------------------------#
        self.core_count = core_count
        self.memtype = memtype
        self.core_frequency = arg_speed[core_type][0]
        self.uncore_frequency = arg_noc[noc]
        self.cache_coherence = "mesi"
        self.cache_line_size = UnitAlgebra("64B")
        self.memory_capacity = UnitAlgebra("192GiB")
        self.mem_count = memchan
        self.page_size = UnitAlgebra("4096B")
        self.layout = arg_cores[core_count]
        self.line_header_size = "8B" # sizeof the header (address + metadata) for a request/response
        self.debug_addresses = []    # No impact unless SST configured with --enable-debug
                                     # Leave empty to debug all addresses

        # --------------------------------#
        ### Network-on-chip (NoC)       ###
        # --------------------------------#
        self.noc_buffer_depth = 2 # 2 is minimum
        self.noc_bandwidth = arg_noc[noc]
        self.noc_link_width = "256b"

        # --------------------------------#
        ### Cores                       ###
        # --------------------------------#
        self.core_hw_threads = arg_smt[smt]
        self.core_reorder_slots = 64
        self.core_physical_integer_registers = 128 # default
        self.core_physical_fp_registers = 128 # default
        self.core_integer_arith_units = 2 # default
        self.core_integer_arith_cycles = 2 #default
        self.core_integer_div_units = 1 #default
        self.core_integer_div_cycles = 4 #default
        self.core_fp_arith_units = 2 #default
        self.core_fp_arith_cycles = 5
        self.core_fp_div_units = 1 #default
        self.core_fp_div_cycles = 80 #default
        self.core_branch_units = 1
        self.core_branch_unit_cycles = self.core_integer_arith_cycles
        self.core_branch_entries = 64
        self.core_issues_per_cycle = 2
        self.core_fetches_per_cycle = 2
        self.core_retires_per_cycle = 2
        self.core_decodes_per_cycle = 2
        self.core_uop_entries = 128
        self.core_predecode_cache_entries = 4
        self.core_lsq_stores = 10 # max_stores in store queue
        self.core_lsq_loads = 20 # max_loads in load queue
        self.core_lsq_issues_per_cycle = 2 # Number of loads and stores issued per cycle
        self.core_data_tlb_hit_latency = 0.5 # In ns
        self.core_data_tlb_set_size = 4
        self.core_data_tlb_entries_per_thread = 64
        self.core_insn_tlb_hit_latency = 0.5 # In ns
        self.core_insn_tlb_set_size = 4
        self.core_insn_tlb_entries_per_thread = 64
        self.core_min_virtual_address = 4096
        self.core_max_virtual_address = 0x80000000

        # The rest is for debugging if needed
        self.core_verbose = 0
        self.core_dbg_mask = 0
        self.core_start_verbose_when_issue_address = ""
        self.core_stop_verbose_when_retire_address = 0 # 0=None
        self.core_pause_when_retire_address = 0 # 0=None
        self.core_pipeline_trace_file = ""
        self.core_exit_after_cycles = -1 # Exit after this many cycles (< 0 means ignore parameter)
        self.core_print_retire_tables = False
        self.core_print_issue_tables = False
        self.core_print_int_reg = False
        self.core_print_fp_reg = False
        self.core_print_rob = False

        # --------------------------------#
        ### L1 I-Cache                  ###
        # --------------------------------#
        self.l1icache_size = arg_l1size[l1size][0]
        self.l1icache_banks = 4
        self.l1icache_associativity = arg_l1size[l1size][1]
        self.l1icache_tag_latency = 1
        self.l1icache_latency = arg_l1size[l1size][2]
        self.l1icache_requests_per_cycle = 6
        self.l1icache_request_bytes_per_cycle = "0B" # Let requests_per_cycle be the limiter
        self.l1icache_response_bytes_per_cycle = "0B" # No limit on responses
        self.l1icache_fill_buffers = arg_speed[core_type][2]
        self.l1icache_fill_buffer_latency = 1
        self.l1icache_replacement = "lru"
        # These are for debug/error reporting
        self.l1icache_timeout = 0 # No timeout
        self.l1icache_debug_level = 0 # No impact unless SST configured with --enable-debug
        self.l1icache_verbose = 1 # Basic warnings enabled

        # --------------------------------#
        ### L1 I-Cache                  ###
        # --------------------------------#
        self.l1dcache_size = arg_l1size[l1size][0]
        self.l1dcache_banks = 4
        self.l1dcache_associativity = arg_l1size[l1size][1]
        self.l1dcache_tag_latency = 1
        self.l1dcache_latency = arg_l1size[l1size][2]
        self.l1dcache_requests_per_cycle = 4
        self.l1dcache_request_bytes_per_cycle = "0B" # Let requests_per_cycle be the limiter
        self.l1dcache_response_bytes_per_cycle = "0B" # No limit on response throughput
        self.l1dcache_fill_buffers = arg_speed[core_type][2]
        self.l1dcache_fill_buffer_latency = 1
        self.l1dcache_replacement = "lru"
        # A LL will cause the cache to stall competing accesses for this many cycles
        # or until an SC is executed (whichever is first)
        # Reduces chance of livelock
        self.l1dcache_llsc_wait_cycles = 100
        # These are for debug/error reporting
        self.l1dcache_timeout = 0 # No timeout
        self.l1dcache_debug_level = 0 # No impact unless SST configured with --enable-debug
        self.l1dcache_verbose = 1 # Basic warnings enabled

        # --------------------------------#
        ### L2 Cache                    ###
        # --------------------------------#
        self.l2cache_size = arg_l2size[l2size][0]
        self.l2cache_banks = 4
        self.l2cache_associativity = arg_l2size[l2size][1]
        self.l2cache_tag_latency = 2
        self.l2cache_latency = arg_l2size[l2size][2]
        self.l2cache_requests_per_cycle = 4
        self.l2cache_request_bytes_per_cycle = "0B" # Let requests_per_cycle be the limiter
        self.l2cache_response_bytes_per_cycle = "0B" # No limit on response throughput
        self.l2cache_fill_buffers = self.l1dcache_fill_buffers
        self.l2cache_fill_buffer_latency = 1
        self.l2cache_replacement = "lru"
        # These are for debug/error reporting
        self.l2cache_debug_level = 0 # No impact unless SST configured with --enable-debug
        self.l2cache_verbose = 1 # Basic warnings enabled

        # --------------------------------#
        ### L3 Cache                    ###
        # --------------------------------#
        self.l3cache_count = core_count
        self.l3cache_size = arg_l3size[l3size][0]
        self.l3cache_banks = 8
        self.l3cache_associativity = arg_l3size[l3size][1]
        self.l3cache_latency = arg_l3size[l3size][2]
        self.l3cache_tag_latency = 6
        self.l3cache_requests_per_cycle = 8
        self.l3cache_request_bytes_per_cycle = "0B" # Let requests_per_cycle be the limiter
        self.l3cache_response_bytes_per_cycle = "0B" # No limit on response throughput
        self.l3cache_fill_buffers = self.l2cache_fill_buffers + (self.l2cache_fill_buffers // 2) # 50% extra
        self.l3cache_fill_buffer_latency = 1
        self.l3cache_replacement = "lru"
        # These are for debug/error reporting
        self.l3cache_debug_level = 0 # No impact unless SST configured with --enable-debug
        self.l3cache_verbose = 1 # Basic warnings enabled

        # --------------------------------#
        ### Directory                   ###
        # --------------------------------#
        # In this config, the directory is co-located with L3
        self.l3cache_dir_entries = (UnitAlgebra(self.l3cache_size) + UnitAlgebra(self.l2cache_size) + UnitAlgebra("512KB")) / self.cache_line_size
        self.l3cache_dir_replacement = "lru"
        self.l3cache_dir_associativity = 16

        # --------------------------------#
        ### Memory                      ###
        # --------------------------------#
        self.memory_controller_clock = self.uncore_frequency
        self.memory_backing = "malloc" # Allocate memory to hold simulated data on-demand
        self.memory_initialize_to_zero = True

        ########################################################################
        ############################### STOP ###################################
        #### Remaining parameters are generated and should not be modified. ####
        ########################################################################
    
        ###########################################
        # Parameter sets for each component type
        # Most parameters are determined using the variables above
        self.noc_x, self.noc_y = map(int, self.layout.split('x'))
        self.mesh_stops = self.noc_x * self.noc_y

        self.noc_bisection_links = max(self.noc_x, self.noc_y)
        self.noc_link_bandwidth = UnitAlgebra(self.noc_bandwidth) / UnitAlgebra(self.noc_bisection_links)
        # For 256b channel, data flit will be 36B (64B or 256b data + 4B of the header)
        byte_convert = UnitAlgebra("8b/B")
        if UnitAlgebra(self.noc_link_width).hasUnits("b"):
            self.noc_link_width_bytes = UnitAlgebra(self.noc_link_width) / byte_convert
        else:
            self.noc_link_width_bytes = UnitAlgebra(self.noc_link_width)
        self.data_flits_per_line = self.cache_line_size / self.noc_link_width_bytes
        self.header_per_data_flit = UnitAlgebra(self.line_header_size) / self.data_flits_per_line
        self.noc_data_flit = self.noc_link_width_bytes + self.header_per_data_flit
        self.noc_size = self.layout # Do not change without also modifying structures in example.py

    def getCoreParams(self):
        return { 
            "hardware_threads": self.core_hw_threads,
            "clock" : self.core_frequency,
            "reorder_slots" : self.core_reorder_slots,
            "physical_integer_registers" : self.core_physical_integer_registers,
            "physical_fp_registers" : self.core_physical_fp_registers,
            "integer_arith_units" : self.core_integer_arith_units,
            "integer_arith_cycles" : self.core_integer_arith_cycles,
            "integer_div_units" : self.core_integer_div_units,
            "integer_div_cycles" : self.core_integer_div_cycles,
            "fp_arith_units" : self.core_fp_arith_units,
            "fp_arith_cycles" : self.core_fp_arith_cycles,
            "fp_div_units" : self.core_fp_div_units,
            "fp_div_cycles" : self.core_fp_div_cycles,
            "branch_units": self.core_branch_units,
            "branch_unit_cycles": self.core_branch_unit_cycles,
            "issues_per_cycle": self.core_issues_per_cycle,
            "fetches_per_cycle": self.core_fetches_per_cycle,
            "retires_per_cycle": self.core_retires_per_cycle,
            "decodes_per_cycle": self.core_decodes_per_cycle,
            "dcache_line_width": self.cache_line_size.getRoundedValue(),
            "icache_line_width": self.cache_line_size.getRoundedValue(),
            "print_retire_tables": self.core_print_retire_tables,
            "print_issue_tables": self.core_print_issue_tables,
            "print_int_reg": self.core_print_int_reg,
            "print_fp_reg": self.core_print_fp_reg,
            "print_rob": self.core_print_rob,
            "enable_simt": False, # This parameter is not yet available in Vanadis
            "verbose": self.core_verbose,
            "dbg_mask": self.core_dbg_mask,
            "start_verbose_when_issue_address": self.core_start_verbose_when_issue_address,
            "stop_verbose_when_retire_address": self.core_stop_verbose_when_retire_address,
            "pause_when_retire_address": self.core_pause_when_retire_address,
            "pipeline_trace_file": self.core_pipeline_trace_file,
            "max_cycle": self.core_exit_after_cycles
        }
    
    def getOSParams(self):
        return { 
            "hardwareThreadCount" : self.core_hw_threads,
            "physMemSize" : self.memory_capacity,
            "page_size" : self.page_size.getRoundedValue(),
            "useMMU" : True,
        }

    def getBranchParams(self):
        return { "branch_entries" : self.core_branch_entries }

    def getDecoderParams(self):
        return {
            "icache_line_width" : self.cache_line_size.getRoundedValue(),
            "uop_cache_entries" : self.core_uop_entries,
            "predecode_cache_entries" :  self.core_predecode_cache_entries, # Number of cache lines to store
            "decode_max_ins_per_cycle" : self.core_decodes_per_cycle,
            "loader_mode" : 0 # Use LRU instead of infinite cache
        }
    
    def getLSQParams(self):
        return {
            "max_stores" : self.core_lsq_stores,
            "max_loads" : self.core_lsq_loads,
            "issues_per_cycle" : self.core_lsq_issues_per_cycle,
            "cache_line_width" : self.cache_line_size.getRoundedValue()
        }

    def getDTLBParams(self):
        return {
            "hitLatency" : self.core_data_tlb_hit_latency,
            "num_hardware_threads" : self.core_hw_threads,
            "num_tlb_entries_per_thread" : self.core_data_tlb_entries_per_thread,
            "tlb_set_size" : self.core_data_tlb_set_size,
            "minVirtAddr" : self.core_min_virtual_address,
            "maxVirtAddr" : self.core_max_virtual_address
        }

    def getITLBParams(self):
        return {
            "hitLatency" : self.core_insn_tlb_hit_latency,
            "num_hardware_threads" : self.core_hw_threads,
            "num_tlb_entries_per_thread" : self.core_insn_tlb_entries_per_thread,
            "tlb_set_size" : self.core_insn_tlb_set_size,
            "minVirtAddr" : self.core_min_virtual_address,
            "maxVirtAddr" : self.core_max_virtual_address
        }

    def getL1ICacheParams(self):
        if self.l1icache_debug_level > 0:
            l1icache_do_debug = 1
        else:
            l1icache_do_debug = 0
        return {
            "L1" : 1,
            "cache_type" : "inclusive", # All L1s must be inclusive
            "cache_size" : self.l1icache_size,
            "cache_line_size" : self.cache_line_size.getRoundedValue(),
            "banks" : self.l1icache_banks,
            "associativity" : self.l1icache_associativity,
            "coherence_protocol" : self.cache_coherence,
            "cache_frequency" : self.core_frequency,
            "access_latency_cycles" : self.l1icache_latency,
            "tag_access_latency_cycles" : self.l1icache_tag_latency,
            "max_requests_per_cycle" : self.l1icache_requests_per_cycle,
            "request_link_width" : self.l1icache_request_bytes_per_cycle,
            "response_link_width" : self.l1icache_response_bytes_per_cycle,
            "mshr_num_entries": self.l1icache_fill_buffers,
            "mshr_latency_cycles" : self.l1icache_fill_buffer_latency,
            "min_packet_size" : self.line_header_size,
            "maxRequestDelay" : self.l1icache_timeout,
            "debug" : l1icache_do_debug,
            "debug_level" : self.l1icache_debug_level,
            "debug_addr" : self.debug_addresses,
            "verbose" : self.l1icache_verbose,
            # Don't have a prefetcher, but if we did, should enable these
            #"prefetch_delay_cycles" : l1icache_prefetch_latency,
            #"max_outstanding_prefetch" : l1icache_max_concurrent_prefetches,
            #"drop_prefetch_mshr_level" : l1icache_max_prefetch_fill_buffers,   
        }

    def getL1DCacheParams(self):
        if self.l1dcache_debug_level > 0:
            l1dcache_do_debug = 1
        else:
            l1dcache_do_debug = 0
        return {
            "L1" : 1,
            "cache_type" : "inclusive", # All L1s must be inclusive
            "cache_size" : self.l1dcache_size,
            "banks" : self.l1dcache_banks,
            "cache_line_size" : self.cache_line_size.getRoundedValue(),
            "associativity" : self.l1dcache_associativity,
            "coherence_protocol" : self.cache_coherence,
            "cache_frequency" : self.core_frequency,
            "access_latency_cycles" : self.l1dcache_latency,
            #"tag_access_latency_cycles" : self.l1dcache_tag_latency,
            "max_requests_per_cycle" : self.l1dcache_requests_per_cycle, 
            "mshr_num_entries" : self.l1dcache_fill_buffers,
            "mshr_latency_cycles" : self.l1dcache_fill_buffer_latency,
            "llsc_block_cycles" : self.l1dcache_llsc_wait_cycles,
            "min_packet_size" : self.line_header_size,
            "max_requests_per_cycle" : self.l1dcache_requests_per_cycle,
            "request_link_width" : self.l1dcache_request_bytes_per_cycle,
            "response_link_width" : self.l1dcache_response_bytes_per_cycle,
            "maxRequestDelay" : self.l1dcache_timeout,
            "debug" : l1dcache_do_debug,
            "debug_level" : self.l1dcache_debug_level,
            "debug_addr" : self.debug_addresses,
            "verbose" : self.l1dcache_verbose,
            # Don't have a prefetcher, but if we did, should enable these
            #"prefetch_delay_cycles" : self.l1dcache_prefetch_latency,
            #"max_outstanding_prefetch" : self.l1dcache_max_concurrent_prefetches,
            #"drop_prefetch_mshr_level" : self.l1dcache_max_prefetch_fill_buffers,   
        }

    def getL2CacheParams(self):
        if self.l2cache_debug_level > 0:
            l2cache_do_debug = 1
        else:
            l2cache_do_debug = 0
        return {
            "cache_type" : "inclusive",
            "cache_size" : self.l2cache_size,
            "banks" : self.l2cache_banks,
            "cache_line_size" : self.cache_line_size.getRoundedValue(),
            "associativity" : self.l2cache_associativity,
            "coherence_protocol" : self.cache_coherence,
            "cache_frequency" : self.core_frequency,
            "access_latency_cycles" : self.l2cache_latency,
            #"tag_access_latency_cycles" : self.l2cache_tag_latency,
            "max_requests_per_cycle" : self.l2cache_requests_per_cycle, 
            "mshr_num_entries" : self.l2cache_fill_buffers,
            "mshr_latency_cycles" : self.l2cache_fill_buffer_latency,
            "min_packet_size" : self.line_header_size,
            "max_requests_per_cycle" : self.l2cache_requests_per_cycle,
            "request_link_width" : self.l2cache_request_bytes_per_cycle,
            "response_link_width" : self.l2cache_response_bytes_per_cycle,
            "debug" : l2cache_do_debug,
            "debug_level" : self.l2cache_debug_level,
            "debug_addr" : self.debug_addresses,
            "verbose" : self.l2cache_verbose,
            # Don't have a prefetcher, but if we did, should enable these
            #"prefetch_delay_cycles" : self.l2cache_prefetch_latency,
            #"max_outstanding_prefetch" : self.l2cache_max_concurrent_prefetches,
            #"drop_prefetch_mshr_level" : self.l2cache_max_prefetch_fill_buffers,  
        }

    def getL3CacheParams(self):
        if self.l3cache_debug_level > 0:
            l3cache_do_debug = 1
        else:
            l3cache_do_debug = 0
        return {
            "cache_type" : "noninclusive_with_directory",
            "cache_size" : self.l3cache_size,
            "banks" : self.l3cache_banks,
            "cache_line_size" : self.cache_line_size.getRoundedValue(),
            "associativity" : self.l3cache_associativity,
            "noninclusive_directory_entries" : self.l3cache_dir_entries,
            "noninclusive_directory_associativity": self.l3cache_dir_associativity,
            "coherence_protocol" : self.cache_coherence,
            "cache_frequency" : self.uncore_frequency,
            "access_latency_cycles" : self.l3cache_latency,
            #"tag_access_latency_cycles" : self.l3cache_tag_latency,
            "max_requests_per_cycle" : self.l3cache_requests_per_cycle, 
            "mshr_num_entries" : self.l3cache_fill_buffers,
            "mshr_latency_cycles" : self.l3cache_fill_buffer_latency,
            "min_packet_size" : self.line_header_size,
            "max_requests_per_cycle" : self.l3cache_requests_per_cycle,
            "request_link_width" : self.l3cache_request_bytes_per_cycle,
            "response_link_width" : self.l3cache_response_bytes_per_cycle,
            "debug" : l3cache_do_debug,
            "debug_level" : self.l3cache_debug_level,
            "debug_addr" : self.debug_addresses,
            "verbose" : self.l3cache_verbose,
            # Don't have a prefetcher, but if we did, should enable these
            #"prefetch_delay_cycles" : self.l3cache_prefetch_latency,
            #"max_outstanding_prefetch" : self.l3cache_max_concurrent_prefetches,
            #"drop_prefetch_mshr_level" : self.l3cache_max_prefetch_fill_buffers,  
        }

    def getMemoryControllerParams(self):
        return {
            "clock" : self.memory_controller_clock,
            "backing" : self.memory_backing,
            "initBacking" : self.memory_initialize_to_zero
        }
    
    def getMemoryModel(self):
        return "memHierarchy.SimpleDRAM"
    
    def getMemoryParams(self):
        params = {
            "request_width" : 64,
            "cycle_time" : "3200MHz",
            "banks" : 16,
            "bank_interleave_granularity" : "1KiB",
            "row_size": "1KiB",
            "row_policy" : "open"
        }
        return params | arg_memtype[self.memtype]

    def getMemoryConnectionMap(self):
        return memory_layouts[self.core_count][self.mem_count]
    
    def getCost(self):
        cost = self.per_core_cost * self.core_count
        cost += (self.per_mem_cost * self.mem_count)
        return round(cost,2)

