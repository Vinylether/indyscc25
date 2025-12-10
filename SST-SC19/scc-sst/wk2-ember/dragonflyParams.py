
debug = 0

netConfig = {
    "topology" : "dragonfly",
    "shape"    : "16:32:16:32",
    "num_groups" : "32",
    "routers_per_group" : "32",
    "intergroup_links" : "16",
    "hosts_per_router" : "16",
    "algorithm" : "adaptive-local",
}

networkParams = {
    "packetSize" : "2048B",
    "link_bw" : "100Gb/s",
    "xbar_bw" : "150Gb/s",
    "link_lat" : "150ns",
    "input_latency" : "0ns",
    "output_latency" : "0ns",
    "flitSize" : "16B",
    "input_buf_size" : "14KB",
    "output_buf_size" : "14KB",
}

nicParams = {
    "detailedCompute.name" : "thornhill.SingleThread",
    "module" : "merlin.reorderlinkcontrol",
    "packetSize" : networkParams['packetSize'],
    "link_bw" : networkParams['link_bw'],
    "input_buf_size" : networkParams['input_buf_size'],
    "output_buf_size" : networkParams['output_buf_size'],
    "rxMatchDelay_ns" : 100,
    "txDelay_ns" : 50,
    "nic2host_lat" : "100ns",
    "useSimpleMemoryModel" : 0,

    "simpleMemoryModel.verboseLevel" : 0,
    "simpleMemoryModel.verboseMask" : -1,

    "simpleMemoryModel.memNumSlots" : 32,
    "simpleMemoryModel.memReadLat_ns" : 150, 
    "simpleMemoryModel.memWriteLat_ns" : 40, 
    
    "simpleMemoryModel.hostCacheUnitSize" : 32, 
    "simpleMemoryModel.hostCacheNumMSHR" : 32, 
    "simpleMemoryModel.hostCacheLineSize" : 64, 
    
    "simpleMemoryModel.widgetSlots" : 32, 
    
    "simpleMemoryModel.nicNumLoadSlots" : 16, 
    "simpleMemoryModel.nicNumStoreSlots" : 16, 
    
    "simpleMemoryModel.nicHostLoadSlots" : 1, 
    "simpleMemoryModel.nicHostStoreSlots" : 1, 
    
    "simpleMemoryModel.busBandwidth_Gbs" : 7.8,
    "simpleMemoryModel.busNumLinks" : 8,
    "simpleMemoryModel.detailedModel.name" : "firefly.detailedInterface",
    "maxRecvMachineQsize" : 100,
    "maxSendMachineQsize" : 100,
}

emberParams = {
    "os.module"    : "firefly.hades",
    "os.name"      : "hermesParams",
    "api.0.module" : "firefly.hadesMP",
    "api.1.module" : "firefly.hadesSHMEM",
    "api.2.module" : "firefly.hadesMisc",
    'firefly.hadesSHMEM.verboseLevel' : 0,
    'firefly.hadesSHMEM.verboseMask'  : -1,
    'firefly.hadesSHMEM.enterLat_ns'  : 7,
    'firefly.hadesSHMEM.returnLat_ns' : 7,
    "verbose" : 0,
}

hermesParams = {
    "hermesParams.detailedCompute.name" : "thornhill.SingleThread",
    "hermesParams.memoryHeapLink.name" : "thornhill.MemoryHeapLink",
    "hermesParams.nicModule" : "firefly.VirtNic",

    "hermesParams.functionSM.defaultEnterLatency" : 30000,
    "hermesParams.functionSM.defaultReturnLatency" : 30000,

    "hermesParams.ctrlMsg.shortMsgLength" : 12000,
    "hermesParams.ctrlMsg.matchDelay_ns" : 150,

    "hermesParams.ctrlMsg.txSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txSetupModParams.range.0" : "0-:130ns",

    "hermesParams.ctrlMsg.rxSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.rxSetupModParams.range.0" : "0-:100ns",

    "hermesParams.ctrlMsg.txMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.txMemcpyModParams.range.0" : "0-:344ps",

    "hermesParams.ctrlMsg.rxMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.rxMemcpyModParams.range.0" : "0-:344ps",

    "hermesParams.ctrlMsg.sendAckDelay_ns" : 0,
    "hermesParams.ctrlMsg.regRegionBaseDelay_ns" : 3000,
    "hermesParams.ctrlMsg.regRegionPerPageDelay_ns" : 100,
    "hermesParams.ctrlMsg.regRegionXoverLength" : 4096,
    "hermesParams.loadMap.0.start" : 0,
    "hermesParams.loadMap.0.len" : 2,
}
