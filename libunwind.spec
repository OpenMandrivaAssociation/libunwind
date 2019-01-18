%define oname unwind
%define onamedump unwindcoredump
%define major 8
%define majordump 0
%define majorsetjmp 0
%define libname %mklibname %{oname} %{major}
%define libdump %mklibname %{onamedump} %{majordump}
%define devname %mklibname %{oname} -d
%define _disable_ld_no_undefined 1
%define _disable_lto 1

Summary:	An unwinding library
Name:		libunwind
Version:	1.3.1
Release:	1
License:	BSD
Group:		System/Libraries
Url:		http://savannah.nongnu.org/projects/libunwind
Source0:	http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}.tar.gz
Source1:	%{name}.rpmlintrc
#Fedora specific patch
# (tpg) dunno if it is still needed
#Patch1:		libunwind-disable-setjmp.patch
Patch3:		libunwind-musl.patch
BuildRequires:	libtool
BuildRequires:	pkgconfig(liblzma)

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n %{libname}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Provides:	%{name} = %{EVRD}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{libdump}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Provides:	%{name}-coredump = %{EVRD}
Requires:	%{name} = %{EVRD}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libdump}
Dynamic libraries from %{name}.

%package -n %{devname}
Summary:	Development package for libunwind
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	%{name}-coredump = %{EVRD}
Requires:	%{mklibname %{oname}-setjmp %{majorsetjmp}} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%dependinglibpackage %{oname}-setjmp %{majorsetjmp}

%prep
%setup -q
%autopatch -p1
autoreconf -fi

%build
%ifarch %arm
export CC=gcc
export CXX=g++
%endif

# (tpg) fix linking on znver1
%global ldflags %{ldflags} -fuse-ld=bfd

%configure \
       --enable-static \
       --enable-shared

%make_build

%install
%make_install

# /usr/include/libunwind-ptrace.h
# [...] aren't really part of the libunwind API.  They are implemented in
# a archive library called libunwind-ptrace.a.
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a %{buildroot}%{_libdir}/libunwind-ptrace.a-save
rm %{buildroot}%{_libdir}/libunwind*.a
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a-save %{buildroot}%{_libdir}/libunwind-ptrace.a
rm %{buildroot}%{_libdir}/libunwind-ptrace*.so*

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

%files -n %{devname}
%doc COPYING README NEWS
%{_libdir}/libunwind*.so
%{_libdir}/libunwind-ptrace.a
%{_libdir}/pkgconfig/*.pc
# <unwind.h> does not get installed for REMOTE_ONLY targets - check it.
%{_includedir}/unwind.h
%{_includedir}/libunwind*.h
