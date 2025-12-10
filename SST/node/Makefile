# LLVM_INSTALL_PATH should point to the install directory for LLVM
# RISCV_TOOLCHAIN_INSTALL_PATH should point to the install directory for the RISC-V GNU Toolchain                        
CC = $(LLVM_INSTALL_PATH)/bin/clang

RISCV_SYSROOT := $(RISCV_TOOLCHAIN_INSTALL_PATH)/sysroot/
CFLAGS_RV = --target=riscv64-unknown-linux-gnu -march=rv64gc -static-libgcc --gcc-toolchain=$(RISCV_TOOLCHAIN_INSTALL_PATH) --sysroot=$(RISCV_SYSROOT) -Wall -g 

.PHONY: check_rvtools all clean

# Check to make sure LLVM_INSTALL_PATH and RISCV_TOOLCHAIN_INSTALL_PATH are defined                                       
# 'else' is just to suppress the 'nothing to be done' message from make if the check passes                               
check_llvm:
ifndef LLVM_INSTALL_PATH
    $(error env LLVM_INSTALL_PATH is not set)
else
	@echo > /dev/null
endif

check_rvtools:
ifndef RISCV_TOOLCHAIN_INSTALL_PATH
    $(error env RISCV_TOOLCHAIN_INSTALL_PATH is not set)
else
	@echo > /dev/null
endif

all: beam

beam: beam.c
	$(CC) -static -mno-relax $(CFLAGS_RV) -o beam beam.c -lm -pthread

clean:
	rm -f beam
