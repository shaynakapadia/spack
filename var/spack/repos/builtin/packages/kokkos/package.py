# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack import *


class Kokkos(CMakePackage, CudaPackage):
    """Kokkos implements a programming model in C++ for writing performance
    portable applications targeting all major HPC platforms."""

    homepage = "https://github.com/kokkos/kokkos"
    git = "https://github.com/kokkos/kokkos.git"
    url = "https://github.com/kokkos/kokkos/archive/3.1.01.tar.gz"

    version('develop', branch='develop')
    version('master',  branch='master')
    version('3.1.01', sha256='ff5024ebe8570887d00246e2793667e0d796b08c77a8227fe271127d36eec9dd')
    version('3.1.00', sha256="b935c9b780e7330bcb80809992caa2b66fd387e3a1c261c955d622dae857d878")
    version('3.0.00', sha256="c00613d0194a4fbd0726719bbed8b0404ed06275f310189b3493f5739042a92b")

    depends_on("cmake@3.10:", type='build')

    devices_variants = {
        'cuda': [False, 'Whether to build CUDA backend'],
        'openmp': [False, 'Whether to build OpenMP backend'],
        'pthread': [False, 'Whether to build Pthread backend'],
        'serial': [True,  'Whether to build serial backend'],
        'hip': [False, 'Whether to build HIP backend'],
    }
    conflicts("+hip", when="@:3.0")

    tpls_variants = {
        'hpx': [False, 'Whether to enable the HPX library'],
        'hwloc': [False, 'Whether to enable the HWLOC library'],
        'numactl': [False, 'Whether to enable the LIBNUMA library'],
        'memkind': [False, 'Whether to enable the MEMKIND library'],
    }

    options_variants = {
        'aggressive_vectorization': [False,
                                     'Aggressively vectorize loops'],
        'compiler_warnings': [False,
                              'Print all compiler warnings'],
        'cuda_lambda': [False,
                        'Activate experimental lambda features'],
        'cuda_ldg_intrinsic': [False,
                               'Use CUDA LDG intrinsics'],
        'cuda_relocatable_device_code': [False,
                                         'Enable RDC for CUDA'],
        'cuda_uvm': [False,
                     'Enable unified virtual memory (UVM) for CUDA'],
        'debug': [False,
                  'Activate extra debug features - may increase compiletimes'],
        'debug_bounds_check': [False,
                               'Use bounds checking - will increase runtime'],
        'debug_dualview_modify_check': [False, 'Debug check on dual views'],
        'deprecated_code': [False, 'Whether to enable deprecated code'],
        'examples': [False, 'Whether to build OpenMP  backend'],
        'explicit_instantiation': [False,
                                   'Explicitly instantiate template types'],
        'hpx_async_dispatch': [False,
                               'Whether HPX supports asynchronous dispath'],
        'profiling': [True,
                      'Create bindings for profiling tools'],
        'profiling_load_print': [False,
                                 'Print which profiling tools got loaded'],
        'qthread': [False, 'Eenable the QTHREAD library'],
        'tests': [False, 'Build for tests'],
    }

    amd_gpu_arches = [
        'fiji',
        'gfx901',
        'vega900',
        'vega906',
    ]
    variant("amd_gpu_arch", default='none', values=amd_gpu_arches,
            description="AMD GPU architecture")
    conflicts("+hip", when="amd_gpu_arch=none")

    spack_micro_arch_map = {
        "aarch64": "",
        "arm": "",
        "ppc": "",
        "ppc64": "",
        "ppc64le": "",
        "ppcle": "",
        "sparc": None,
        "sparc64": None,
        "x86": "",
        "x86_64": "",
        "thunderx2": "THUNDERX2",
        "k10": None,
        "zen": "ZEN",
        "bulldozer": "",
        "piledriver": "",
        "zen2": "ZEN2",
        "steamroller": "KAVERI",
        "excavator": "CARIZO",
        "a64fx": "",
        "power7": "POWER7",
        "power8": "POWER8",
        "power9": "POWER9",
        "power8le": "POWER8",
        "power9le": "POWER9",
        "i686": None,
        "pentium2": None,
        "pentium3": None,
        "pentium4": None,
        "prescott": None,
        "nocona": None,
        "nehalem": None,
        "sandybridge": "SNB",
        "haswell": "HSW",
        "mic_knl": "KNL",
        "cannonlake": "SKX",
        "cascadelake": "SKX",
        "westmere": "WSM",
        "core2": None,
        "ivybridge": "SNB",
        "broadwell": "BDW",
        # @AndrewGaspar: Kokkos does not have an arch for plain-skylake - only
        # for Skylake-X (i.e. Xeon). For now, I'm mapping this to Broadwell
        # until Kokkos learns to optimize for SkyLake without the AVX-512
        # extensions. SkyLake with AVX-512 will still be optimized using the
        # separate `skylake_avx512` arch.
        "skylake": "BDW",
        "icelake": "SKX",
        "skylake_avx512": "SKX",
    }

    spack_cuda_arch_map = {
        "30": 'kepler30',
        "32": 'kepler32',
        "35": 'kepler35',
        "37": 'kepler37',
        "50": 'maxwell50',
        "52": 'maxwell52',
        "53": 'maxwell53',
        "60": 'pascal60',
        "61": 'pascal61',
        "70": 'volta70',
        "72": 'volta72',
        "75": 'turing75',
    }
    cuda_arches = spack_cuda_arch_map.values()
    conflicts("+cuda", when="cuda_arch=none")

    devices_values = list(devices_variants.keys())
    for dev in devices_variants:
        dflt, desc = devices_variants[dev]
        variant(dev, default=dflt, description=desc)

    options_values = list(options_variants.keys())
    for opt in options_values:
        if "cuda" in opt:
            conflicts('+%s' % opt, when="~cuda",
                      msg="Must enable CUDA to use %s" % opt)
        dflt, desc = options_variants[opt]
        variant(opt, default=dflt, description=desc)

    tpls_values = list(tpls_variants.keys())
    for tpl in tpls_values:
        dflt, desc = tpls_variants[tpl]
        variant(tpl, default=dflt, description=desc)
        depends_on(tpl, when="+%s" % tpl)

    variant("wrapper", default=False,
            description="Use nvcc-wrapper for CUDA build")
    depends_on("kokkos-nvcc-wrapper", when="+wrapper")
    conflicts("+wrapper", when="~cuda")

    variant("std", default="11", values=["11", "14", "17", "20"], multi=False)
    # nvcc does not currently work with C++17 or C++20
    conflicts("+cuda", when="std=17")
    conflicts("+cuda", when="std=20")

    variant('shared', default=True, description='Build shared libraries')

    def append_args(self, cmake_prefix, cmake_options, spack_options):
        for opt in cmake_options:
            enablestr = "+%s" % opt
            optuc = opt.upper()
            optname = "Kokkos_%s_%s" % (cmake_prefix, optuc)
            option = None
            if enablestr in self.spec:
                option = "-D%s=ON" % optname
            else:
                # explicitly turn off if not enabled
                # this avoids any confusing implicit defaults
                # that come from the CMake
                option = "-D%s=OFF" % optname
            if option not in spack_options:
                spack_options.append(option)

    def setup_dependent_package(self, module, dependent_spec):
        try:
            self.spec.kokkos_cxx = self.spec["kokkos-nvcc-wrapper"].kokkos_cxx
        except Exception:
            self.spec.kokkos_cxx = spack_cxx

    def cmake_args(self):
        spec = self.spec
        options = []

        isdiy = "+diy" in spec
        if isdiy:
            options.append("-DSpack_WORKAROUND=On")

        spack_microarches = []
        if "+cuda" in spec:
            # this is a list
            for cuda_arch in spec.variants["cuda_arch"].value:
                if not cuda_arch == "none":
                    kokkos_arch_name = self.spack_cuda_arch_map[cuda_arch]
                    spack_microarches.append(kokkos_arch_name)
        kokkos_microarch_name = self.spack_micro_arch_map[spec.target.name]
        if kokkos_microarch_name:
            spack_microarches.append(kokkos_microarch_name)

        for arch in self.amd_gpu_arches:
            keyval = "amd_gpu_arch=%s" % arch
            if keyval in spec:
                spack_microarches.append(arch)

        for arch in spack_microarches:
            options.append("-DKokkos_ARCH_%s=ON" % arch.upper())

        self.append_args("ENABLE", self.devices_values, options)
        self.append_args("ENABLE", self.options_values, options)
        self.append_args("ENABLE", self.tpls_values, options)

        for tpl in self.tpls_values:
            var = "+%s" % tpl
            if var in self.spec:
                options.append("-D%s_DIR=%s" % (tpl, spec[tpl].prefix))

        # we do not need the compiler wrapper from Spack
        # set the compiler explicitly (may be Spack wrapper or nvcc-wrapper)
        try:
            options.append("-DCMAKE_CXX_COMPILER=%s" %
                           self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
        except Exception:
            options.append("-DCMAKE_CXX_COMPILER=%s" % spack_cxx)

        # Set the C++ standard to use
        options.append("-DKokkos_CXX_STANDARD=%s" %
                       self.spec.variants["std"].value)

        options.append('-DBUILD_SHARED_LIBS=%s' % ('+shared' in self.spec))

        return options
