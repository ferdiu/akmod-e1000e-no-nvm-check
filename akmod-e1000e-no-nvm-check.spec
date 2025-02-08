%global debug_package %{nil}

%define major_version 1.0
%define release_version 1dev0

Name:       akmod-e1000e-no-nvm-check
Version:    %{major_version}
Release:    %{release_version}%{?dist}
Summary:    Akmod for e1000e with no NVM check
License:    MIT
URL:        https://github.com/ferdiu/akmod-e1000e-no-nvm-check
Source0:     %{url}/archive/refs/tags/v%{major_version}-%{release_version}.tar.gz
Requires:   akmods, kernel-devel, sed

BuildArch:  noarch


%description
Akmod to rebuild e1000e kernel module to skip NVM
checksum validation for buggy hardware (not faulty!)

Use this only if you are sure that your hardware is
working properly and the only thing preventing it from
working is the NVM checksum validation.

%prep
%setup -q -n akmod-e1000e-no-nvm-check-%{major_version}-%{release_version}

%install
install -D -m 0644 kmod-e1000e.spec %{buildroot}%{_usrsrc}/akmods/e1000e/kmod-e1000e.spec

%files
%attr(0644, root, root) %{_usrsrc}/akmods/e1000e/kmod-e1000e.spec
%doc README.md
%license LICENSE

%changelog
* Sat Feb 8 2025 Federico Manzella <ferdiu.manzella@gmail.com> 1.0-1
- Initial release of akmod-e1000e-no-nvm-check
