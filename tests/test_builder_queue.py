from builder.queue import BuilderQueue
from agents.product_manager import ProductManagerAgent
from tests.test_product_manager import report


def test_only_build_packages_enter_queue(tmp_path):
    queue = BuilderQueue(str(tmp_path / "queue.jsonl"))
    build = ProductManagerAgent().productize(report("BUILD"))
    validate = ProductManagerAgent().productize(report("VALIDATE"))

    assert queue.enqueue(build) is True
    assert queue.enqueue(build) is False
    assert queue.enqueue(validate) is False
