# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod
%global debug_package %{nil}

%define kmod_name             e1000e
%define kmod_path_kernel      drivers/net/ethernet/intel/%{kmod_name}
%define kmod_version          1.0
%define kmod_release_version  1
%define repo                  rpmfusion

Name:           %{kmod_name}-kmod
Version:        %{kmod_version}
Release:        %{kmod_release_version}%{?dist}
Summary:        Kernel module e1000e with no NVM check
Group:          System Environment/Kernel
License:        GPLv2
URL:            https://github.com/ferdiu/akmod-e1000e-no-nvm-check
Source0:        %{url}/archive/refs/tags/v%{version}-%{kmod_release_version}.tar.gz#/akmod-e1000e-no-nvm-check-v%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  kernel-devel
BuildRequires:  koji
BuildRequires:  %{_bindir}/kmodtool

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g') }

# NOTE: the previous command is piped to two call to sed to substitute the destination
# path of the module to updates directory (instead of extra) because this SPEC is intended
# to be used with in-tree modules

%description
Patched version of e1000e kernel module to skip NVM
checksum validation for buggy hardware (not faulty!)

Use this only if you are sure that your hardware is
working properly and the only thing preventing it from
working is the NVM checksum validation.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g'

%setup -q -c -T -a 0

for kernel_version in %{?kernel_versions} ; do
    kernel_v=${kernel_version%%___*}                            # eg. 6.12.11-200.fc41.x86_64
    kernel_v_no_arch=${kernel_v%.*}                             # eg. 6.12.11-200.fc41
    kernel_extra=${kernel_v#*-}                                 # eg. 200.fc41.x86_64
    kernel_v_no_extra="$(echo -n ${kernel_v} | cut -d"-" -f1)"  # eg. 6.12.11
    kernel_src_dir=${kernel_version##*__}                       # eg. /usr/src/kernels/6.12.11-200.fc41.x86_64

    mkdir -p "${kernel_v_no_arch}"

    # ------------------------------------------------------------------------
    pushd "${kernel_v_no_arch}"

    # Download kernel source
    koji download-build --arch=src "kernel-${kernel_v}"

    ls

    # Unpack source and kernel.spec file
    rpm \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -Uvh kernel-${kernel_v_no_arch}.src.rpm

    ls

    # Unpack source and apply (original) patches
    rpmbuild \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -bp --target="$(uname -m)" kernel.spec

    if [ %{fedora} -gt 40 ]; then
        build_dir="./kernel-${kernel_v_no_extra}-build/kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    else
        build_dir="./kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    fi

    # Prepare build directory
    mv "$build_dir" ../_kmod_build_${kernel_v}

    popd
    # ------------------------------------------------------------------------
    rm -r "${kernel_v_no_arch}"

    # Copy essential files from kernel src directory
    cp -a ${kernel_src_dir}/{.config,Module.symvers,System.map} ./_kmod_build_${kernel_v}/

    # Set correct extra version in Makefile
    sed -i 's/^EXTRAVERSION.*$/EXTRAVERSION=-'"${kernel_extra}"'/' "./_kmod_build_${kernel_v}/Makefile"

    # Apply patch
    sed -i 's/The NVM Checksum Is Not Valid\\n");/The NVM Checksum Is Not Valid (loading anyway)\\n"); break;/' \
        ./_kmod_build_${kernel_v}/%{kmod_path_kernel}/netdev.c
done


%build
for kernel_version in %{?kernel_versions}; do
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" prepare
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" modules_prepare
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_path_kernel} modules
done


%install
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_path_kernel} INSTALL_MOD_PATH=${RPM_BUILD_ROOT} modules_install

    # Delete modules.* files
    rm -f ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}/modules.*
done
%{?akmod_install}


%changelog
* Tue Feb 11 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-1
- Initial release
