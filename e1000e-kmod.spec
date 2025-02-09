# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod
%global debug_package %{nil}

%define kmod_name             e1000e
%define kmod_version          6.12
%define kmod_release_version  1dev2

Name:           %{kmod_name}-kmod

Version:        %{kmod_version}
Release:        %{kmod_release_version}%{?dist}.1
Summary:        Kernel module e1000e with no NVM check

Group:          System Environment/Kernel

License:        GPLv2
URL:            https://github.com/ferdiu/akmod-e1000e-no-nvm-check
Source0:        %{url}/archive/refs/tags/v%{version}-%{kmod_release_version}.tar.gz#/akmod-e1000e-no-nvm-check-v%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
BuildRequires:  kernel-devel
BuildRequires:  %{_bindir}/kmodtool

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


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
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T -a 0 -n akmod-e1000e-no-nvm-check-%{version}-%{kmod_release_version}

# Apply patches
pushd akmod-e1000e-no-nvm-check-%{version}
mv src/* .
rmdir src
sed -i 's/The NVM Checksum Is Not Valid\\n");/The NVM Checksum Is Not Valid (loading anyway)\\n"); break;/' \
    ./netdev.c
popd

for kernel_version in %{?kernel_versions} ; do
    # echo "The builddir for ${kernel_version%%___*} is ${kernel_version##*__}"
    cp -a akmod-e1000e-no-nvm-check-%{version} _kmod_build_${kernel_version%%___*}
    cp -a ${kernel_version##*__}/. _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" M=${PWD}/_kmod_build_${kernel_version%%___*} modules
done


%install
for kernel_version in %{?kernel_versions}; do
    make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
done
%{?akmod_install}


%changelog
* Sun Feb 9 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 6.12-1
- Initial release