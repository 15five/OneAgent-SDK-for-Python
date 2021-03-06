#
# Copyright 2018 Dynatrace LLC
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

from __future__ import print_function

import sys

import pytest

#pylint:disable=wrong-import-order
from testhelpers import run_in_new_interpreter

import oneagent

#pylint:disable=unsupported-membership-test

@pytest.mark.dependsnative
def test_run_public_sdk():
    '''Test that using the native SDK without any special options works.'''
    out = run_in_new_interpreter(__name__)
    print('OUTPUT:\n' + out)
    assert '-main' in out
    assert 'DONE.' in out

@pytest.mark.dependsnative
def test_run_public_sdk_checkinit():
    '''Test that using the native SDK, additionally checking init return
    value.'''
    out = run_in_new_interpreter(__name__, ['tryinit'])
    print('OUTPUT:\n' + out)
    assert '-main' in out
    assert 'DONE.' in out

def test_run_public_sdk_noc():
    '''Test that using the native SDK without the stub does not crash'''
    out = run_in_new_interpreter(__name__, ['noc'])
    assert 'Error during SDK initialization' in out
    assert '-main' in out
    assert 'DONE.' in out

    out = run_in_new_interpreter(__name__, ['tryinit noc'])
    assert 'Error during SDK initialization' not in out
    assert '-main' in out
    assert 'DONE.' in out

def test_mk_sdkopts_alldefaults():
    oldargs = sys.argv
    newargs = ['--dt_foo=bar', 'qu', '--dt_bla=off', 'dt_quak=on']
    try:
        sys.argv = list(newargs) # copy
        opts = oneagent.sdkopts_from_commandline()
        assert sys.argv == newargs # Nothing should be removed
    finally:
        sys.argv = oldargs
    assert opts == ['foo=bar', 'bla=off']

def test_mk_sdkopts_customprefix():
    argv_orig = ['/SDKfoo=bar', 'qu', '/SDKbla=off', '/sdkquak=on']
    argv = list(argv_orig) # copy
    opts = oneagent.sdkopts_from_commandline(argv, prefix='/SDK')
    assert argv == argv_orig
    assert opts == ['foo=bar', 'bla=off']

def test_mk_sdkopts_remove():
    argv_orig = ['/SDKfoo=bar', 'qu', '/SDKbla=off', '--SDKquak=on']
    argv = list(argv_orig) # copy
    opts = oneagent.sdkopts_from_commandline(argv, remove=True, prefix='/SDK')
    assert argv == [argv_orig[1], argv_orig[3]]
    assert opts == ['foo=bar', 'bla=off']


#pylint:enable=unsupported-membership-test

def main():
    import logging
    logger = logging.getLogger('py_sdk')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    flags = sys.argv[1].split() if len(sys.argv) > 1 else ()
    if 'noc' in flags:
        sys.modules['oneagent._impl.native.sdkctypesiface'] = False

    if 'tryinit' in flags:
        init_result = oneagent.initialize(['loglevelsdk=finest'])
        if 'noc' in flags:
            assert not init_result
            assert init_result.status == init_result.STATUS_STUB_LOAD_ERROR
            assert isinstance(init_result.error, ImportError)
        else:
            assert init_result
            assert init_result.status == init_result.STATUS_INITIALIZED


    from test import onesdksamplepy
    onesdksamplepy.main()
    print('DONE.')

if __name__ == '__main__':
    main()
