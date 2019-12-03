import testlink.enums as enums

def test_ExecutionType():
    assert enums.ExecutionType.MANUAL == 1
    assert enums.ExecutionType.AUTOMATIC == 2

def test_ImportanceLevel():
    assert enums.ImportanceLevel.HIGH == 3
    assert enums.ImportanceLevel.MEDIUM == 2
    assert enums.ImportanceLevel.LOW == 1

def test_DuplicateStrategy():
    assert enums.DuplicateStrategy.NEW_VERSION.value == 'create_new_version'
    assert enums.DuplicateStrategy.GENERATE_NEW.value == 'generate_new'
    assert enums.DuplicateStrategy.BLOCK.value == 'block'

def test_CustomFieldDetails():
    assert enums.CustomFieldDetails.VALUE_ONLY.value == 'value'

def test_APIType():
    assert enums.APIType.XML_RPC.value == 'XML-RPC'
    assert enums.APIType.REST.value == 'REST'

def test_TestCaseStatus():
    assert enums.TestCaseStatus.DRAFT == 1
    assert enums.TestCaseStatus.READY_FOR_REVIEW == 2
    assert enums.TestCaseStatus.REVIEW_IN_PROGRESS == 3
    assert enums.TestCaseStatus.REWORK == 4
    assert enums.TestCaseStatus.OBSOLETE == 5
    assert enums.TestCaseStatus.FUTURE == 6
    assert enums.TestCaseStatus.FINAL == 7
