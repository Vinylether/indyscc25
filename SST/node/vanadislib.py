import sst
from mhlib import *

### Note: This module is being used to prototype a set of python utilities
###  for more easily generating and configuring simulations using vanadis.
###  Feel free to use the utilities available here but be aware that this file
###  may change without warning in the SST-Elements repository.
###
### Eventually, a python module with convenience functions for vanadis will be released
###  and that module will be fully supported by the project (provide backwards compatibility,
###  deprecation notices, stability testing).
###

## Parameters
"""
NodeOS
         cores: Number of cores that can request OS services via a link.  [<required>]
         dbgLevel: Debug level (verbosity) for OS debug output  [0]
         dbgMask: Mask for debug output  [0]
         node_id: If specificied as > 0, this id will be used to tag stdout/stderr files.  [-1]
         hardwareThreadCount: Number of hardware threads pert core  [1]
         osStartTimeNano: 'Epoch' time added to simulation time for syscalls like gettimeofday  [1000000000]
         program_header_address: Program header address  [0x60000000]
         processDebugLevel: Debug level (verbosity) for process debug output  [0]
         physMemSize: Size of available physical memory in bytes, with units. Ex: 2GiB  [<required>]
         page_size: Size of a page, in bytes  [4096]
         useMMU: Whether an MMU subcomponent is being used.  [False]
         process%(processnum)d.env_count: Number of environment variables to pass to the process  [0]
         process%(processnum)d.env%(argnum)d: Environment variable to pass to the process. Example: 'OMPNUMTHREADS=64'. 'argnum' should be contiguous starting at 0 and ending at env_count-1  []
         proccess%(processnum)d.exe: Name of executable, including path  [<required>]
         process%(processnum)d.argc: Number of arguments to the executable (including arg0)  [1]
         process%(processnum)d.arg0: Name of the executable (path not needed)  [<required>]
         process%(processnum)d.arg%(argnum)d: Arguments for the executable. Each argument should be specified in a separate parameter and 'argnum' should be contigous starting at 1 to argc-1  []


CPU
         verbose: Set the level of output verbosity, 0 is no output, higher is more output  [0]
         dbg_mask: Mask for output. Default is to not mask anything out (0) and defer to 'verbose'.  [0]
         start_verbose_when_issue_address: Set verbose to 0 until the specified instruction address is issued, then set to 'verbose' parameter  []
         stop_verbose_when_retire_address: When the specified instruction address is retired, set verbose to 0  []
         pause_when_retire_address: If specified, the simulation will stop when this address is retired.  [0]
         pipeline_trace_file: If specified, a trace of the pipeline activity will be generated to this file.  []
         max_cycle: Maximum number of cycles to execute. The core will halt after this many cycles.  [std::numeric_limits<uint64_t>::max()]
         node_id: Identifier for the node this core belongs to. Each node in the system needs a unique ID between 0 and (number of nodes) - 1. Used to tag output.  [0]
         core_id: Identifier for this core. Each core in the system needs a unique ID between 0 and (number of cores) - 1.  [<required>]
         hardware_threads: Number of hardware threads in this core  [1]
         clock: Core clock frequency  [1GHz]
         reorder_slots: Number of slots in the reorder buffer  [64]
         physical_integer_registers: Number of physical integer registers per hardware thread  [128]
         physical_fp_registers: Number of physical floating point registers per hardware thread  [128]
         integer_arith_units: Number of integer arithemetic units  [2]
         integer_arith_cycles: Cycles per instruction for integer arithmetic  [2]
         integer_div_units: Number of integer division units  [1]
         integer_div_cycles: Cycles per instruction for integer division  [4]
         fp_arith_units: Number of floating point arithmetic units  [2]
         fp_arith_cycles: Cycles per floating point arithmetic  [8]
         fp_div_units: Number of floating point division units  [1]
         fp_div_cycles: Cycles per floating point division  [80]
         branch_units: Number of branch units  [1]
         branch_unit_cycles: Cycles per branch  [int_arith_cycles]
         issues_per_cycle: Number of instruction issues per cycle  [2]
         fetches_per_cycle: Number of instruction fetches per cycle  [2]
         retires_per_cycle: Number of instruction retires per cycle  [2]
         decodes_per_cycle: Number of instruction decodes per cycle  [2]
         dcache_line_width: Width of a line for the data cache, in bytes. (Currently not used but may be in the future).  [64]
         icache_line_width: Width of a line for the instruction cache, in bytes  [64]
         print_retire_tables: Print registers during retirement step (default is yes)  [true]
         print_issue_tables: Print registers during issue step (default is yes)  [true]
         print_int_reg: Print integer registers true/false, auto set to true if verbose > 16  [false]
         print_fp_reg: Print floating-point registers true/false, auto set to true if verbose > 16  [false]
         print_rob: Print reorder buffer state during issue and retire  [true]
         enable_simt: Implement SIMT pipeline for multithread kernels  [false]

3 subcomponents - where IS DECODER????
lsq
decoder
rocc
mem_interface

Three links:
    icache_link
    dcache_link
    os_link

SubComponents (7 total)
   SubComponent 0: VanadisBasicBranchUnit
         branch_entries: Sets the number of entries in the underlying cache of branch directions  [64]

   SubComponent 1: VanadisBasicLoadStoreQueue
         verbose: Set the verbosity of output for the LSQ  [0]
         verboseMask: Mask bits for masking output  [-1]
         dbgInsAddrs: Comma-separated list of instruction addresses to debug  []
         dbgAddrs: Comma-separated list of addresses to debug  []
         max_stores: Set the maximum number of stores permitted in the queue  [8]
         max_loads: Set the maximum number of loads permitted in the queue  [16]
         address_mask: Can mask off address bits if needed during construction of a operation  [0xFFFFFFFFFFFFFFFF]
         issues_per_cycle: Maximum number of issues the LSQ can attempt per cycle.  [2]
         cache_line_width: Number of bytes in a (L1) cache line  [64]
      Ports (1 total)
         dcache_link: Connects the LSQ to the data cache
      SubComponent Slots (1 total)
         memory_interface: Set the interface to memory [SST::Interfaces::StandardMem]

   SubComponent 2: VanadisMIPSDecoder
      Parameters (6 total)
         icache_line_width: Number of bytes in an icache line  [64]
         uop_cache_entries: Number of instructions to cache in the micro-op cache (this is full instructions, not microops but usually 1:1 ratio  [128]
         predecode_cache_entries: Number of cache lines to store in the local L0 cache for instructions pending decoding.  [4]
         loader_mode: Operation of the loader, 0 = LRU (more accurate), 1 = INFINITE cache (faster simulation)  [0]
         decode_max_ins_per_cycle: Maximum number of instructions that can be decoded and issued per cycle  [2]
         entry_point: Starting instruction pointer; if not specified (set to 0), falls back to the core's ELF reader to discover  [0]
      SubComponent Slots (2 total)
         os_handler: Handler for SYSCALL instructions [SST::Vanadis::VanadisCPUOSHandler]
         branch_unit: Branch prediction unit [SST::Vanadis::VanadisBranchUnit]

   SubComponent 3: VanadisMIPSOSHandler

   SubComponent 4: VanadisRISCV64Decoder
      Description: Implements a RISCV64-compatible decoder for Vanadis CPU processing.
      ELI version: 0.9.0
      Compiled using file: ./decoder/vriscv64decoder.h
      Interface: SST::Vanadis::VanadisDecoder
      Parameters (7 total)
         icache_line_width: Number of bytes in an icache line  [64]
         uop_cache_entries: Number of instructions to cache in the micro-op cache (this is full instructions, not microops but usually 1:1 ratio  [128]
         predecode_cache_entries: Number of cache lines to store in the local L0 cache for instructions pending decoding.  [4]
         loader_mode: Operation of the loader, 0 = LRU (more accurate), 1 = INFINITE cache (faster simulation)  [0]
         decode_max_ins_per_cycle: Maximum number of instructions that can be decoded and issued per cycle  [2]
         halt_on_decode_fault: Fatal error if a decode fault occurs, used for debugging and not recommmended default is 0 (false)  [0]
         entry_point: Starting instruction pointer; if not specified (set to 0), falls back to the core's ELF reader to discover  [0]
      SubComponent Slots (2 total)
         os_handler: Handler for SYSCALL instructions [SST::Vanadis::VanadisCPUOSHandler]
         branch_unit: Branch prediction unit [SST::Vanadis::VanadisBranchUnit]

   SubComponent 5: VanadisRISCV64OSHandler

   SubComponent 6: VanadisRoCCBasic
      Description: Implements a basic example of a RoCC accelerator
      ELI version: 0.9.0
      Compiled using file: ./rocc/vbasicrocc.h
      Interface: SST::Vanadis::VanadisRoCCInterface
      Parameters (3 total)
         verbose: Set the verbosity of output for the RoCC Accelerator Interface  [0]
         max_instructions: Set the maximum number of RoCC instructions permitted in the queue  [8]
         clock: Clock frequency for component TimeConverter. MMIOTile is Unclocked but subcomponents use the TimeConverter  [1Ghz]
      SubComponent Slots (1 total)
         memory_interface: Set the interface to memory [SST::Interfaces::StandardMem]

Modules (2 total)
   Module 0: AppRuntimeMemory32

   Module 1: AppRuntimeMemory64

"""


class VanadisCore:

    """
    This sets up the skeleton of the core and assigns known/default parameters
    Parameters can be overridden later
    """
    def __init__(self, prefix, core_num, node_num, isa, hw_threads, os, mmu, link_latency):
        self.prefix = prefix
        self.isa = isa  # Error checked by Vanadis()
        self.hw_threads = hw_threads # Error checked by Vanadis()
        self.link_latency = link_latency
        
        # Create core component
        self.comp = sst.Component(prefix + str(core_num), "vanadis.dbg_VanadisCPU")
        self.comp.addParam("core_id", core_num)
        self.comp.addParam("node_id", node_num)
        self.lsq = self.comp.setSubComponent( "lsq", "vanadis.VanadisBasicLoadStoreQueue" )
        
        # Add decoder, os interface, branch unit
        self.decoder = []
        self.os_handler = []
        self.branch_unit = []
        for thr in range(hw_threads):
            self.decoder.append(self.comp.setSubComponent("decoder", "vanadis.Vanadis" + isa + "Decoder", thr))
            self.os_handler.append(self.decoder[-1].setSubComponent( "os_handler", "vanadis.Vanadis" + isa + "OSHandler"))
            self.branch_unit.append(self.decoder[-1].setSubComponent( "branch_unit", "vanadis.VanadisBasicBranchUnit" ))

        # Data and instruction interfaces (to TLBs)
        self.data_if = self.lsq.setSubComponent( "memory_interface", "memHierarchy.standardInterface" )
        self.insn_if = self.comp.setSubComponent("mem_interface_inst", "memHierarchy.standardInterface") 
        
        # TLBs
        self.data_tlb_wrapper = sst.Component(prefix + str(core_num) + ".dtlb", "mmu.tlb_wrapper") 
        self.insn_tlb_wrapper = sst.Component(prefix + str(core_num) + ".itlb", "mmu.tlb_wrapper")
        self.data_tlb = self.data_tlb_wrapper.setSubComponent( "tlb", "mmu.simpleTLB" )
        self.insn_tlb = self.insn_tlb_wrapper.setSubComponent( "tlb", "mmu.simpleTLB" )
        self.insn_tlb_wrapper.addParam("exe", True) # Indicate this is the instruction TLB
        
        # Core needs to be connected to: TLBs, OS
        # TLBs need to be connected to: MMU
        # Connect core ports to TLBs
        dtlblink = sst.Link(prefix + str(core_num) + ".dtlb")
        dtlblink.connect( (self.data_if, "lowlink", self.link_latency), (self.data_tlb_wrapper, "cpu_if", self.link_latency) )
        dtlblink.setNoCut() # Never cut the link between core & TLB
        
        itlblink = sst.Link(prefix + str(core_num) + ".itlb")
        itlblink.connect( (self.insn_if, "lowlink", self.link_latency), (self.insn_tlb_wrapper, "cpu_if", self.link_latency) )
        itlblink.setNoCut() # Never cut the link between core & TLB

        # Connect core's OS port
        oslink = sst.Link(prefix + str(core_num) + ".os")
        oslink.connect( (self.comp, "os_link", self.link_latency), (os, "core" + str(core_num), self.link_latency) )

        # Connect TLB/mmu ports
        dmmulink = sst.Link(prefix + str(core_num) + ".dmmu")
        dmmulink.connect( (self.data_tlb, "mmu", self.link_latency), (mmu, "core" + str(core_num) + ".dtlb", self.link_latency) )
        immulink = sst.Link(prefix + str(core_num) + ".immu")
        immulink.connect( (self.insn_tlb, "mmu", self.link_latency), (mmu, "core" + str(core_num) + ".itlb", self.link_latency) )


    def enableStats(self):
        self.comp.enableAllStatistics()
        for x in self.decoder:
            self.decoder[x].enableAllStatistics()
        # decode.os_handler has no stats

    ### Functions to override default parameters on core + any subcomponents
    def configureCore(self, params):
        self.comp.addParams(params)

    def configureDecoder(self, params, thr = -1):
        if thr == -1:
            for decoder in self.decoder:
                decoder.addParams(params)
        else:
            self.decoder[thr].addParams(params)
    
    def configureBranchUnit(self, params, thr = -1):
        if thr == -1:
            for branch_unit in self.branch_unit:
                branch_unit.addParams(params)
        else:
            self.branch_unit[thr].addParams(params)
    
    def configureLSQ(self, params):
        self.lsq.addParams(params)
    
    def configureOSHandler(self, params, thr = -1):
        if thr == -1:
            for handler in self.os_handler:
                handler.addParams(params)
        else:
            self.os_handler[thr].addParams(params)

    def configureTLB(self, params, dtlb=True):
        if dtlb:
            self.data_tlb.addParams(params)
        else:
            self.insn_tlb.addParams(params)

    ### Functions to get links - returns a tuple with optionally overridden latency
    def getDataPort(self, link_latency=None):
        if ( link_latency == None):
            return (self.data_tlb_wrapper, "cache_if", self.link_latency)
        else:
            return (self.data_tlb_wrapper, "cache_if", link_latency)
    
    def getInstructionPort(self, link_latency=None):
        if ( link_latency == None):
            return (self.insn_tlb_wrapper, "cache_if", self.link_latency)
        else:
            return (self.insn_tlb_wrapper, "cache_if", link_latency)

""" 
    Vanadis instance with convenience functions for connecting a memory subsystem
    Required arguments:
        prefix = unique prefix to use for all SST names within this instance
        cores  = number of cores to generate
        link_latency = default latency to use anytime a link is created
        isa = 'riscv64', 'rv', 'riscv' OR 'mipsel', 'mips'. default = 'riscv64'
        hw_threads = number of HW threads per core. default = 1

    Usage:
        1. Create a VanadisCPU instance
        2. 

        Optional: enable statistics by calling enableStats()
"""
class Vanadis:
    # Class variables - can globally set these
    isa = "RISCV64"
    hw_threads = 1
    node_count = 0
    process = 0

    def __init__(self, prefix, cores, link_latency, isa='RISCV64', hw_threads=1):
        """
            Members are:
                prefix  = string prefix for names
                link_latency = latency to use for links
                isa     = which isa (mipsel or riscv64)
                os      = vanadis os component (1)
                cores   = vanadis core components (vector: 1 per core)
                decoders = vanadis decoder subcomponents (vector: 1 per hw thread)
        """
        self.prefix = prefix             # Unique name prefix to avoid name clashes
        self.link_latency = link_latency # Default link latency
        self.caches_configured = False   # Private caches have not been configured yet

        # isa: Accept common short terms for mips/riscv
        self.isa = isa
        if isa == "mips" or isa == "mipsel":
            self.isa = "MIPS"
        elif isa == "rv" or isa == "riscv" or isa == "riscv64" or isa == "RISCV" or isa == "RV":
            self.isa = "RISCV64"
        
        if isa != "RISCV64" and isa != "MIPS":
            raise Exception("Error: Vanadis ISA must be 'MIPS' (mips/mipsel also accepted) or 'RISCV64' (rv/riscv/riscv64/RV/RISCV also accepted). Argument was '{}'".format(isa))
        
        # hw_threads: can be updated later
        self.hw_threads = hw_threads
        if hw_threads < 1:
            raise Exception("Error: 'hw_threads' must be at least 1. Argument was '{}'".format(hw_threads))

        # ---------------------------------------------------------------------------------------- #

        # Create OS
        self.os = sst.Component(prefix + "_os", "vanadis.VanadisNodeOS")
        self.mmu = self.os.setSubComponent("mmu", "mmu.simpleMMU")
        self.os.addParam("useMMU", True)
        self.mmu.addParams({
            "num_cores" : cores,
            "num_threads" : hw_threads,
        })
        
        # Create cores
        self.cores = []
        for x in range(0, cores):
            core = VanadisCore(prefix, x, Vanadis.node_count, isa, hw_threads, self.os, self.mmu, link_latency)
            self.cores.append(core)
            
        # Placeholders for caches
        self.l1i = None
        self.l1d = None
        self.l2 = None

        # Increment node_count
        Vanadis.node_count = Vanadis.node_count + 1
         
    
    ## Enable stats
    def enableStats(self, core=-1):
        if core == -1:
            for core in self.cores:
                core.enableStats()
        else:
            self.cores[core].enableStats()
    

    ## Getters for generated components
    def getCore(self, num=0):
        return self.cores[num]

    def getOS(self):
        return self.os

    # Can only call one of the following private cache construction functions

    # Add private L1 and L2 to each core and private L1 to OS
    def addPrivateL1L2(self, l1i_params, l1d_params, l2_params, bus_params = None, os_cache_params = None):
        if self.caches_configured:
            raise Exception("Error: calling addPrivateL1L2() on vanadis with prefix {}, but caches are already configured!".format(self.prefix))

        self.caches_configured = True
        
        self.l1i = PrivateCache(self.prefix + "_l1i", 1, len(self.cores), l1i_params)
        self.l1d = PrivateCache(self.prefix + "_l1d", 1, len(self.cores), l1d_params)
        self.l2  = PrivateCache(self.prefix + "_l2", 2, len(self.cores), l2_params)

        if bus_params is None:
            bus_params = { "bus_frequency" : self.link_latency }

        # Connect L1s to L2s
        for x in range(0, len(self.cores)):
            bus = Bus(self.prefix + "_bus" + str(x), bus_params, self.link_latency, [self.l1i.get(x), self.l1d.get(x)], [self.l2.get(x)])

            link0 = sst.Link(self.prefix + str(x) + "c1i")
            link0.connect( (self.cores[x].insn_tlb_wrapper, "cache_if", self.link_latency), (self.l1i.get(x), "highlink", self.link_latency) )
            link1 = sst.Link(self.prefix + str(x) + "c1d")
            link1.connect( (self.cores[x].data_tlb_wrapper, "cache_if", self.link_latency), (self.l1d.get(x), "highlink", self.link_latency) )
            link0.setNoCut()
            link1.setNoCut()

        # Create OS cache - treat as an L2 for level purposes
        if os_cache_params == None:
            os_cache_params = l1d_params
        self.l1_os = PrivateCache(self.prefix + "_l1os", 2, 1, os_cache_params)
        link = sst.Link(self.prefix + "l1os")
        link.connect( (self.os.setSubComponent("mem_interface", "memHierarchy.standardInterface"), "lowlink", self.link_latency), 
                      (self.l1_os.get(0), "highlink", self.link_latency) )
        
        # For error checking
        self.l1i.setHighConnected()
        self.l1d.setHighConnected()
        self.l2.setHighConnected()
        self.l1_os.setHighConnected() 
        self.l1i.setLowConnected()
        self.l1d.setLowConnected()

    def addPrivateL1(self, l1i_params, l1d_params, os_cache_params = None):
        if self.caches_configured:
            raise Exception("Error: calling addPrivateL1() on vanadis with prefix {}, but caches are already configured!".format(self.prefix))

        self.caches_configured = True
        
        self.l1i = PrivateCache(self.prefix + "_l1i", 1, len(self.cores), l1i_params)
        self.l1d = PrivateCache(self.prefix + "_l1d", 1, len(self.cores), l1d_params)

        # Connect TLBs and caches
        for x in range(0, len(self.cores)):
            link0 = sst.Link(self.prefix + str(x) + "c1i")
            link0.connect( (self.cores[x].insn_tlb_wrapper, "cache_if", self.link_latency), (self.l1i.get(x), "highlink", self.link_latency) )
            link1 = sst.Link(self.prefix + str(x) + "c1d")
            link1.connect( (self.cores[x].data_tlb_wrapper, "cache_if", self.link_latency), (self.l1d.get(x), "highlink", self.link_latency) )
            link0.setNoCut()
            link1.setNoCut()

        # Create OS cache - treat as an L1 for level purposes
        if os_cache_params == None:
            os_cache_params = l1d_params
        self.l1_os = PrivateCache(self.prefix + "_l1os", 1, 1, os_cache_params)
        link = sst.Link(self.prefix + "l1os")
        link.connect( (self.os.setSubComponent("mem_interface", "memHierarchy.standardInterface"), "lowlink", self.link_latency), 
                      (self.l1_os.get(0), "highlink", self.link_latency) )
        
        # For error checking
        self.l1i.setHighConnected()
        self.l1d.setHighConnected()
        self.l1_os.setHighConnected() 


    def getL1ICaches(self):
        return self.l1i
    
    def getL1DCaches(self):
        return self.l1d
    
    def getL2Caches(self):
        return self.l2
    
    ### Configuring the CPU
    # If core < 0: Sets parameters on all cores
    # Else, sets parameters on requested core
    def configureCores(self, core_params, core=-1):
        if core > -1:
            if core >= len(self.cores):
                raise Exception("Error, core must less than core count. Core {} does not exist.\n".format(core))
            self.cores[core].configureCore(core_params)
            return
        
        for core in self.cores:
            core.configureCore(core_params)

    def configureDecoders(self, decoder_params, core=-1):
        if core > -1:
            if core >= len(self.cores):
                raise Exception("Error, core must less than core count. Core {} does not exist.\n".format(core))
            self.cores[core].configureDecoder(decoder_params)
            return
        
        for core in self.cores:
            core.configureDecoder(decoder_params)
    
    def configureBranchUnits(self, branch_params, core=-1):
        if core > -1:
            if core >= len(self.cores):
                raise Exception("Error, core must less than core count. Core {} does not exist.\n".format(core))
            self.cores[core].configureBranchUnit(branch_params)
            return
        
        for core in self.cores:
            core.configureBranchUnit(branch_params)
        
    def configureLoadStoreQueues(self, lsq_params, core=-1):
        if core > -1:
            if core >= len(self.cores):
                raise Exception("Error, core must less than core count. Core {} does not exist.\n".format(core))
            self.cores[core].configureLSQ(lsq_params)
            return
        
        for core in self.cores:
            core.configureLSQ(lsq_params)   

    def configureOperatingSystem(self, os_params):
        self.os.addParam("cores", len(self.cores))
        self.os.addParams(os_params)
        if "page_size" in os_params:
            self.mmu.addParam("page_size", os_params["page_size"])

    def configureMMU(self, mmu_params):
        self.os.setSubComponent("mmu", "mmu.simpleMMU")
    
    def configureTLBs(self, tlb_params, dtlb=True, core=-1):
        if core > -1:
            if core >= len(self.cores):
                raise Exception("Error, core must be less than core count. Core {} does not exist\n".format(core))
            self.cores[core].configureTLB(tlb_params, dtlb)
            return
        
        for core in self.cores:
            core.configureTLB(tlb_params, dtlb)
    
    def configureApplication(self, app : str, app_args=[], env_args=[]):
        process = "process" + str(self.process)
        app_no_path = app.split('/')[-1]

        self.os.addParam(process + ".env_count", len(env_args))
        for x in range(0, len(env_args)):
            self.os.addParam(process + ".env" + str(x), env_args[x])
        
        self.os.addParam(process + ".argc", 1 + len(app_args))
        self.os.addParam(process + ".exe", app)
        self.os.addParam(process + ".arg0", app_no_path)
        for x in range(0, len(app_args)):
            self.os.addParam(process + ".arg" + str(x+1), app_args[x])
        
        self.process += 1
