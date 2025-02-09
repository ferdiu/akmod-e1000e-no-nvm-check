# (un)define the next line to either build for the newest or all current kernels

%define kmod_name             e1000e
%define kmod_version          6.12
%define kmod_release_version  1dev2
%define kmod_path_kernel      drivers/net/ethernet/intel/e1000e

Name:           %{kmod_name}-kmod-common

Version:        %{kmod_version}
Release:        %{kmod_release_version}%{?dist}
Summary:        Common files for kernel module e1000e with no NVM check

Group:          System Environment/Kernel

License:        MIT
URL:            https://github.com/ferdiu/akmod-e1000e-no-nvm-check
Source0:        %{url}/archive/refs/tags/v%{version}-%{kmod_release_version}.tar.gz#/akmod-e1000e-no-nvm-check-v%{version}.tar.gz
BuildArch:	    noarch

%description
Patched version of e1000e kernel module to skip NVM
checksum validation for buggy hardware (not faulty!)

Use this only if you are sure that your hardware is
working properly and the only thing preventing it from
working is the NVM checksum validation.

This package provides common files for the module.

%prep
%setup -q -n akmod-e1000e-no-nvm-check-%{version}-%{kmod_release_version}

%files
%doc README.md
%license LICENSE

%changelog
* Sun Feb 9 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 6.12-1
- Initial release