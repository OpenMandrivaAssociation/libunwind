# rpmbuild parameters:
# --without check: Do not run the testsuite.  Default is to run it.
%define major           1
%define oname           unwind
%define libname         %mklibname %{oname} %major
%define develname       %mklibname %{oname} -d


Summary: An unwinding library
Name: libunwind
Version: 1.0.1
Release: 3
License: BSD
Group: System/Libraries
Source0: http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}.tar.gz
#Fedora specific patch
Patch1: libunwind-disable-setjmp.patch
Patch2: libunwind-automake-1.13.patch
Patch3: libunwind-arm-register-rename.patch
URL: http://savannah.nongnu.org/projects/libunwind
ExclusiveArch: %{arm} hppa ia64 mips ppc ppc64 %{ix86} x86_64

BuildRequires: automake libtool autoconf

# host != target would cause REMOTE_ONLY build even if building i386 on x86_64.
#% global _host %{_target_platform}

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n     %{libname}
Summary:        Dynamic libraries from %{oname}
Group:          System/Libraries
Provides:       %{name} = %{version}-%{release}

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{develname}
Summary: Development package for libunwind
Group: Development/C
Requires: libunwind = %{version}-%{release}
Provides: libunwind-devel = %{version}-%{release}

%track
prog %name = {
	url = http://mirror3.layerjet.com/nongnu/libunwind/
	regex = %name-(__VER__)\.tar\.gz
	version = %version
}

%description -n %{develname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%prep
%setup -q
%patch1 -p1
%patch2 -p1 -b .am113~
%patch3 -p1 -b .arm

%build
aclocal
libtoolize --force
autoheader
automake --add-missing
autoconf
%configure2_5x --enable-static --enable-shared
make

%install
%makeinstall_std
find %{buildroot} -name '*.la' -exec rm -f {} ';'

# /usr/include/libunwind-ptrace.h
# [...] aren't really part of the libunwind API.  They are implemented in
# a archive library called libunwind-ptrace.a.
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a %{buildroot}%{_libdir}/libunwind-ptrace.a-save
rm -f %{buildroot}%{_libdir}/libunwind*.a
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a-save %{buildroot}%{_libdir}/libunwind-ptrace.a
rm -f %{buildroot}%{_libdir}/libunwind-ptrace*.so*

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%files -n %{libname}
%{_libdir}/libunwind*.so.*

%files -n %{develname}
%doc COPYING README NEWS
%{_libdir}/libunwind*.so
%{_libdir}/libunwind-ptrace.a
%{_mandir}/*/*
# <unwind.h> does not get installed for REMOTE_ONLY targets - check it.
%{_includedir}/unwind.h
%{_includedir}/libunwind*.h
