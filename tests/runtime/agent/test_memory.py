from scios.runtime.agent.memory import Memory


def test_memory_store():

    memory = Memory()

    memory.add(
        "hello"
    )

    assert memory.last() == "hello"



def test_memory_search():

    memory = Memory()

    memory.add("python")
    memory.add("scios")

    result = memory.search(
        "python"
    )

    assert "python" in result