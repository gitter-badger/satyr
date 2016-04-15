from __future__ import absolute_import, division, print_function

import pytest
from satyr.proxies.messages import CommandInfo, Cpus, Mem, TaskID, TaskInfo
from satyr.scheduler import BaseScheduler

pytest.skip()


@pytest.fixture
def command():
    task = TaskInfo(name='test-task',
                    task_id=TaskID(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],
                    command=CommandInfo(value='echo 100'))
    return task


@pytest.fixture
def docker_command():
    task = TaskInfo(name='testdocker--task',
                    task_id=TaskID(value='test-docker-task-id'),
                    resources=[Cpus(0.1), Mem(64)],
                    command=CommandInfo(value='echo 100'))
    task.container.type = 'DOCKER'
    task.container.docker.image = 'lensacom/satyr:latest'
    return task


def test_state_transitions(mocker, command):
    driver = mocker.Mock()
    sched = SingleTaskScheduler(name='test-scheduler', task=command)

    # mock the driver, then call on_offers, on_update(running), on_update(finished)
    # watch driver.launch called, then driver.stop called
    # move this code to a system test e.g. test_framework.py testing executor,
    # scheduler simultaneusly

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_dockerized_state_transitions(mocker, docker_command):
    sched = SingleTaskScheduler(name='test-scheduler', task=docker_command)
    mocker.spy(sched, 'on_update')
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_FINISHED'
