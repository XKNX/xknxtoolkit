from concurrent.futures import Future

from knx_gui.plugins.tasks.service import TaskService


def test_add_returns_running_task_by_default() -> None:
    service = TaskService()
    task_id = service.add("Loading demo.knxprod")

    tasks = service.tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert task.id == task_id
    assert task.label == "Loading demo.knxprod"
    assert task.status == "running"
    assert task.detail == ""


def test_update_changes_only_given_fields() -> None:
    service = TaskService()
    task_id = service.add("Loading demo.knxprod", status="queued")

    service.update(task_id, status="running")
    assert service.tasks()[0].label == "Loading demo.knxprod"
    assert service.tasks()[0].status == "running"

    service.update(task_id, status="error", detail="disk full")
    task = service.tasks()[0]
    assert task.status == "error"
    assert task.detail == "disk full"
    assert task.label == "Loading demo.knxprod"


def test_update_on_unknown_id_is_a_no_op() -> None:
    service = TaskService()
    service.update(999, status="error")
    assert service.tasks() == []


def test_remove_drops_the_task() -> None:
    service = TaskService()
    task_id = service.add("Programming 1.1.4")
    service.remove(task_id)
    assert service.tasks() == []
    # removing again, or an id that never existed, is also a no-op
    service.remove(task_id)
    service.remove(12345)


def test_tasks_orders_running_before_queued_before_error() -> None:
    service = TaskService()
    queued = service.add("Programming 1.1.7", status="queued")
    running = service.add("Loading demo.knxprod", status="running")
    errored = service.add("Exporting group addresses", status="queued")
    service.update(errored, status="error", detail="boom")

    assert [t.id for t in service.tasks()] == [running, queued, errored]


def test_track_removes_the_task_when_the_future_succeeds() -> None:
    service = TaskService()
    future: Future[None] = Future()

    task_id = service.track("Programming 1.1.4", future)
    assert [t.id for t in service.tasks()] == [task_id]

    future.set_result(None)
    assert service.tasks() == []


def test_track_turns_the_task_into_an_error_when_the_future_fails() -> None:
    service = TaskService()
    future: Future[None] = Future()

    task_id = service.track("Programming 1.1.4", future)
    future.set_exception(TimeoutError("no ack from device"))

    task = service.tasks()[0]
    assert task.id == task_id
    assert task.status == "error"
    assert task.detail == "no ack from device"


def test_track_removes_the_task_when_the_future_is_cancelled() -> None:
    service = TaskService()
    future: Future[None] = Future()
    future.cancel()

    service.track("Programming 1.1.4", future)
    assert service.tasks() == []
