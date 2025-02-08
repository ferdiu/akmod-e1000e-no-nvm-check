# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%define kmod_name e1000e
%define module_kernel_path drivers/net/ethernet/intel
%define major_version 1.0
%define release_version 1

Summary:        Patched %{kmod_name} kernel module rebuilt via akmods
Name:           akmod-%{kmod_name}
Version:        %{major_version}
Release:        %{release_version}%{?dist}
License:        GPL
BuildRoot:      %{_tmppath}/%{name}-%{version}-root
BuildRequires:  kernel-devel, kmodtool

%description
This package rebuilds the %{kmod_name} kernel module with a custom patch.

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
for kernel_version in %{?kernel_versions}; do
    # Download the kernel sources
    # TODO: enable real download
    # if [ ! -f "kernel-$(uname -r | sed s/\.$(uname -m)//).src.rpm" ]; then
    #     koji download-build --arch=src "kernel-${kernel_version%%___*}"
    # fi
    echo "Downloading kernel-${kernel_version%%___*}"
    cp /home/ferdiu/Programmi/rpmbuild/kernel-$(uname -r | sed s/\.$(uname -m)//).src.rpm .

    # Work in this directory ONLY
    pwd=$(pwd)

    # Extract kernel sources
    rpm \
        --define "_sourcedir ${pwd}" \
        --define "_specdir ${pwd}" \
        --define "_builddir ${pwd}" \
        --define "_srcrpmdir ${pwd}" \
        --define "_rpmdir ${pwd}" \
        --define "_buildrootdir ${pwd}/.build" \
        -Uvh "kernel-$(uname -r | sed s/\.$(uname -m)//)".src.rpm

    # Unpack source and apply patch
    rpmbuild \
        --define "_sourcedir ${pwd}" \
        --define "_specdir ${pwd}" \
        --define "_builddir ${pwd}" \
        --define "_srcrpmdir ${pwd}" \
        --define "_rpmdir ${pwd}" \
        --define "_buildrootdir ${pwd}/.build" \
        -bp --target="$(uname -m)" %{_specdir}/kernel.spec

    ls -l

    ls -l *

    # Patch e1000e driver (ugly to use sed but this way
    #    it will survive to small changes in the module)
    sed -i 's/The NVM Checksum Is Not Valid\\n");/The NVM Checksum Is Not Valid (loading anyway)\\n"); break;/' e1000e/netdev.c

    # Copy module source from kernel sources
    cp drivers/net/ethernet/intel/e1000e ..
    cd ..
    rm -rf src

    ls
    # TODO: copy following files from /usr/src/kernels/%{kernel_version}/
    # - System.map
    # - Module.symvers
    # - .config
    # TODO: proper copy
    # cp -a LookingGlass-%{tag}/module _kmod_build_${kernel_version%%___*}
done

exit 1


%build
for kernel_version in %{?kernel_versions}; do
    # Prepare
    make -C _kmod_build_${kernel_version%%___*} %{?_smp_mflags} prepare
    make -C _kmod_build_${kernel_version%%___*} %{?_smp_mflags} modules_prepare

    # Build
    make -C _kmod_build_${kernel_version%%___*} %{?_smp_mflags} M="%{module_kernel_path}" modules
done

%install
for kernel_version in %{?kernel_versions}; do
    make -C _kmod_build_${kernel_version%%___*} %{?_smp_mflags} M="%{module_kernel_path}" modules_install
done
%{?akmod_install}

%post
for kernel_version in %{?kernel_versions}; do
    depmod -a "${kernel_version}"
done
