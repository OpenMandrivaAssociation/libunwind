%define oname		unwind
%define onamedump	unwindcoredump
%define major		8
%define majordump	0
%define libname	%mklibname %{oname} %{major}
%define libdump	%mklibname %{onamedump} %{majordump}
%define devname	%mklibname %{oname} -d
%define _disable_ld_no_undefined 1

%bcond_without	uclibc

Summary:	An unwinding library
Name:		libunwind
Version:	1.1
Release:	8
License:	BSD
Group:		System/Libraries
Url:		http://savannah.nongnu.org/projects/libunwind
Source0:	http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}.tar.gz
#Fedora specific patch
Patch1:		libunwind-disable-setjmp.patch
Patch2:		libunwind-aarch64.patch
BuildRequires:	libtool
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n %{libname}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n uclibc-%{libname}
Summary:	Dynamic libraries from %{oname} (uClibc build)
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{libdump}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Provides:	%{name}-coredump = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libdump}
Dynamic libraries from %{name}.

%package -n uclibc-%{libdump}
Summary:	Dynamic libraries from %{oname} (uClibc build)
Group:		System/Libraries
Provides:	uclibc-%{name}-coredump = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libdump}
Dynamic libraries from %{name}.

%package -n %{devname}
Summary:	Development package for libunwind
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name}-coredump = %{version}-%{release}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{version}-%{release}
Requires:	uclibc-%{name}-coredump = %{version}-%{release}
%endif
Provides:	%{name}-devel = %{version}-%{release}

%track
prog %name = {
	url = http://mirror3.layerjet.com/nongnu/libunwind/
	regex = %name-(__VER__)\.tar\.gz
	version = %version
}

%description -n %{devname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%prep
%setup -q
%apply_patches
autoreconf -fi

%build
export CONFIGURE_TOP=$PWD
%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
       --enable-static \
       --enable-shared

%make
popd
%endif

mkdir -p glibc
pushd glibc
%configure \
       --enable-static \
       --enable-shared

%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
%endif
%makeinstall_std -C glibc

# /usr/include/libunwind-ptrace.h
# [...] aren't really part of the libunwind API.  They are implemented in
# a archive library called libunwind-ptrace.a.
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a %{buildroot}%{_libdir}/libunwind-ptrace.a-save
rm %{buildroot}%{_libdir}/libunwind*.a
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a-save %{buildroot}%{_libdir}/libunwind-ptrace.a
rm %{buildroot}%{_libdir}/libunwind-ptrace*.so*

%if %{with uclibc}
mv -f %{buildroot}%{uclibc_root}%{_libdir}/libunwind-ptrace.a %{buildroot}%{uclibc_root}%{_libdir}/libunwind-ptrace.a-save
rm %{buildroot}%{uclibc_root}%{_libdir}/libunwind*.a
mv -f %{buildroot}%{uclibc_root}%{_libdir}/libunwind-ptrace.a-save %{buildroot}%{uclibc_root}%{_libdir}/libunwind-ptrace.a
rm  %{buildroot}%{uclibc_root}%{_libdir}/libunwind-ptrace*.so*
rm %{buildroot}%{uclibc_root}%{_libdir}/pkgconfig/libunwind*.pc
%endif

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%files -n %{libname}
%{_libdir}/libunwind*.so.%{major}*

%files -n %{libdump}
%{_libdir}/libunwind-coredump.so.%{majordump}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/libunwind*.so.%{major}*

%files -n uclibc-%{libdump}
%{uclibc_root}%{_libdir}/libunwind-coredump.so.%{majordump}*
%endif

%files -n %{devname}
%doc COPYING README NEWS
%{_libdir}/libunwind*.so
%{_libdir}/libunwind-ptrace.a
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libunwind*.so
%{uclibc_root}%{_libdir}/libunwind-ptrace.a
%endif
%{_mandir}/*/*
%{_libdir}/pkgconfig/*.pc
# <unwind.h> does not get installed for REMOTE_ONLY targets - check it.
%{_includedir}/unwind.h
%{_includedir}/libunwind*.h
