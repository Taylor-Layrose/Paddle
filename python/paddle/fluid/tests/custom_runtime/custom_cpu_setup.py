# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import site
from paddle.fluid import core
from distutils.sysconfig import get_python_lib
from distutils.core import setup, Extension
from setuptools.command.build_ext import build_ext


# refer: https://note.qidong.name/2018/03/setup-warning-strict-prototypes
# Avoid a gcc warning below:
# cc1plus: warning: command line option ‘-Wstrict-prototypes’ is valid
# for C/ObjC but not for C++
class BuildExt(build_ext):

    def build_extensions(self):
        if '-Wstrict-prototypes' in self.compiler.compiler_so:
            self.compiler.compiler_so.remove('-Wstrict-prototypes')
        super(BuildExt, self).build_extensions()


# cc flags
paddle_extra_compile_args = [
    '-std=c++14',
    '-shared',
    '-fPIC',
    '-Wno-parentheses',
    '-DPADDLE_WITH_CUSTOM_KERNEL',
    '-DPADDLE_WITH_CUSTOM_DEVICE',
]
if core.is_compiled_with_npu():
    paddle_extra_compile_args += ['-D_GLIBCXX_USE_CXX11_ABI=0']

# include path
site_packages_path = site.getsitepackages()
include_dirs = list(
    map(lambda path: os.path.join(path, 'paddle', 'include'),
        site_packages_path))

# include path third_party
compile_third_party_path = os.path.join(os.environ['PADDLE_ROOT'],
                                        'build/third_party')
include_dirs += [
    os.path.join(compile_third_party_path, 'boost/src/extern_boost'),  # boost
    os.path.join(compile_third_party_path, 'install/gflags/include'),  # gflags
    os.path.join(compile_third_party_path, 'install/glog/include'),  # glog
]

# libs path
library_dirs = list(
    map(lambda path: os.path.join(path, 'paddle', 'fluid'), site_packages_path))

# libs
libs = [':core_avx.so']
if not core.has_avx_core and core.has_noavx_core:
    libs = [':core_noavx.so']

custom_cpu_plugin_so = Extension('custom_cpu_runtime',
                                 sources=['custom_cpu_runtime.cc'],
                                 include_dirs=include_dirs,
                                 library_dirs=library_dirs,
                                 libraries=libs,
                                 extra_compile_args=paddle_extra_compile_args)

setup(name='custom_kernel_dot',
      version='1.0',
      description='custom kernel fot compiling',
      cmdclass={'build_ext': BuildExt},
      ext_modules=[custom_cpu_plugin_so])
