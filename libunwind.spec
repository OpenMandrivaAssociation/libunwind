%define oname unwind
%define onamedump unwindcoredump
%define onameptrace unwindptrace
%define major 8
%define majordump 0
%define majorptrace 0
%define majorsetjmp 0
%define libname %mklibname %{oname} %{major}
%define libdump %mklibname %{onamedump} %{majordump}
%define libptrace %mklibname %{onameptrace} %{majorptrace}
%define devname %mklibname %{oname}-nongnu -d
%define _disable_ld_no_undefined 1

%ifarch %{x86_64}
%bcond_without compat32
%define lib32name %mklib32name %{oname} %{major}
%define dev32name %mklib32name %{oname}-nongnu -d
%endif

Summary:	An unwinding library
Name:		libunwind
Version:	1.6.2
Release:	4
License:	BSD
Group:		System/Libraries
# See also https://github.com/libunwind/libunwind
Url:		http://savannah.nongnu.org/projects/libunwind
Source0:	http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}%{?beta:-%{beta}}.tar.gz
Source1:	%{name}.rpmlintrc
Patch3:		libunwind-musl.patch
BuildRequires:	libtool
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	texlive
BuildRequires:	texlive-latex2man

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n %{libname}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{libdump}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Requires:	%{libname} = %{EVRD}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libdump}
Dynamic libraries from %{name}.

%package -n %{libptrace}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries

%description -n %{libptrace}
Dynamic libraries from %{name}.

%define setjmpname %mklibname %{oname}-setjmp %{majorsetjmp}

%package -n %{devname}
Summary:	Development package for libunwind
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	%{libdump} = %{EVRD}
Requires:	%{setjmpname} = %{EVRD}

%description -n %{devname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%package -n %{setjmpname}
Summary:	Libunwind setjmp library
Group:		System/Libraries

%description -n %{setjmpname}
Libunwind setjmp library

%if %{with compat32}
%package -n %{lib32name}
Summary:	32-bit version of the libunwind library
Group:		System/Libraries
BuildRequires:	libc6

%description -n %{lib32name}
32-bit version of the libunwind library

%files -n %{lib32name}
%{_prefix}/lib/libunwind/libunwind*.so.*
%{_prefix}/lib/lib*.so.*

%package -n %{dev32name}
Summary:	Development files for the 32-bit version of libunwind
Group:		Development/C and C++
Requires:	%{lib32name} = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{dev32name}
Development files for the 32-bit version of libunwind

%files -n %{dev32name}
%{_prefix}/lib/libunwind/lib*.so
%{_prefix}/lib/libunwind/lib*.a
%{_prefix}/lib/pkgconfig/*.pc
%endif

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}
autoreconf -fi

export CONFIGURE_TOP="$(pwd)"
mkdir build
cd build
%configure \
	--includedir=%{_includedir}/libunwind \
	--libdir=%{_libdir}/libunwind \
	--enable-static \
	--enable-shared

%if %{with compat32}
cd ..
mkdir build32
cd build32
%configure32 \
	--includedir=%{_includedir}/libunwind \
	--libdir=%{_prefix}/lib/libunwind \
	--target=i686-openmandriva-linux-gnu \
	--host=i686-openmandriva-linux-gnu \
	--enable-static \
	--enable-shared
%endif

%build
%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%install
%if %{with compat32}
%make_install -C build32
mv %{buildroot}%{_prefix}/lib/libunwind/pkgconfig %{buildroot}%{_prefix}/lib
cd %{buildroot}%{_prefix}/lib
ln -s libunwind/*.so.* .
cd -
%endif
%make_install -C build

mv %{buildroot}%{_libdir}/libunwind/pkgconfig %{buildroot}%{_libdir}

# FIXME re-enable once we switch to LLVM libunwind by default
%if 0
# Don't conflict with LLVM libunwind
mv %{buildroot}%{_libdir}/pkgconfig/libunwind.pc %{buildroot}%{_libdir}/pkgconfig/libunwind-nongnu.pc
%endif

cd %{buildroot}%{_libdir}
ln -s libunwind/*.so.* .

# (tpg) strip LTO from "LLVM IR bitcode" files
check_convert_bitcode() {
    printf '%s\n' "Checking for LLVM IR bitcode"
    llvm_file_name=$(realpath ${1})
    llvm_file_type=$(file ${llvm_file_name})

    if printf '%s\n' "${llvm_file_type}" | grep -q "LLVM IR bitcode"; then
# recompile without LTO
    clang %{optflags} -fno-lto -Wno-unused-command-line-argument -x ir ${llvm_file_name} -c -o ${llvm_file_name}
    elif printf '%s\n' "${llvm_file_type}" | grep -q "current ar archive"; then
    printf '%s\n' "Unpacking ar archive ${llvm_file_name} to check for LLVM bitcode components."
# create archive stage for objects
    archive_stage=$(mktemp -d)
    archive=${llvm_file_name}
    cd ${archive_stage}
    ar x ${archive}
    for archived_file in $(find -not -type d); do
        check_convert_bitcode ${archived_file}
        printf '%s\n' "Repacking ${archived_file} into ${archive}."
        ar r ${archive} ${archived_file}
    done
    ranlib ${archive}
    cd ..
    fi
}

for i in $(find %{buildroot} -type f -name "*.[ao]"); do
    check_convert_bitcode ${i}
done

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%files -n %{libname}
%{_libdir}/libunwind/libunwind*.so.%{major}*
%{_libdir}/libunwind*.so.*

%files -n %{libdump}
%{_libdir}/libunwind/libunwind-coredump.so.%{majordump}*

%files -n %{libptrace}
%{_libdir}/libunwind/libunwind-ptrace.so.%{majorptrace}*

%files -n %{setjmpname}
%{_libdir}/libunwind/libunwind-setjmp.so.%{majorsetjmp}*

%files -n %{devname}
%doc COPYING README NEWS
%{_libdir}/libunwind/libunwind*.so
%{_libdir}/libunwind/libunwind*.a
%{_libdir}/pkgconfig/*.pc
%{_includedir}/libunwind
%doc %{_mandir}/man3/*
