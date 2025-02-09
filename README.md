# e1000e-kmod-no-nvm-check

This repository provides patched versions of the e1000e kernel module to bypass the NVM checksum validation, specifically for users with hardware that suffers from buggy NVM checks but is otherwise functioning properly.

> **Warning**: This patch should only be used if you're certain that your hardware is working and that the NVM checksum validation is the only thing preventing your network interface from operating.

## Overview

The kernel module in this repository skips the NVM checksum validation to address compatibility issues on certain Intel Ethernet controllers (e.g., e1000e). If your hardware works properly but the module fails to load due to NVM checksum validation errors, this module will allow you to bypass that check.

The project provides two main components:
1. **e1000e-kmod-common**: Contains common files shared across builds.
2. **e1000e-kmod**: The actual kernel module with the NVM checksum validation bypass.

## Prerequisites

This module requires a compatible kernel and the necessary development tools to build kernel modules.

### Build Dependencies:

- `kernel-devel`
- `kmodtool`
- `make`
- `gcc`

Additionally, ensure that you're building against the kernel version where the issue is present.

## Installation

### For common files:

The `e1000e-kmod-common` package contains the common files required to build the kernel module and is not specific to a particular kernel version. You can install this package on systems that need the shared build resources.

### For the kernel module:

1. Ensure that the `kernel-devel` package for your running kernel is installed.
2. Install the `e1000e-kmod` package, which includes the patched kernel module with the NVM checksum bypass.

For `e1000e-kmod`, the steps to build and install would look something like this:

```bash
# To build the kernel module for your kernel version:
rpmbuild -bb e1000e-kmod.spec

# Install the module:
sudo rpm -i /path/to/e1000e-kmod-6.12-1.x86_64.rpm
```

Note: The build will prepare and compile the kernel module for your specific kernel version, ensuring compatibility with your system.

## Module Patch Details

### Patched Code

The primary patch made to the `e1000e` module consists of modifying the NVM checksum validation logic in the source code. The original code produces an error when the checksum is invalid. The patch changes the message and bypasses the validation:

```c
sed -i 's/The NVM Checksum Is Not Valid\\n");/The NVM Checksum Is Not Valid (loading anyway)\\n"); break;/' \
    %{kmod_path_kernel}/netdev.c
```

### Supported Kernel Versions
This module is designed to be built for a range of kernel versions. The `buildforkernels` parameter allows you to specify which kernel versions to target. By default, this is set to `akmod`, but you can change it if you need to build for specific kernels.

## Usage

Once installed, the module should load automatically with the correct kernel. You can check if the module is loaded by running:

```bash
lsmod | grep e1000e
```

To manually load the module, use:

```bash
sudo modprobe e1000e
```

## Troubleshooting

- If the module does not load, ensure that the correct kernel version is being targeted.
- Check the `dmesg` logs for any errors related to module loading.

## License

This project is licensed under the MIT License.

## Changelog

* **Sun Feb 9 2025** Federico Manzella <ferdiu.manzella@gmail.com> - 6.12-1
  - Initial release