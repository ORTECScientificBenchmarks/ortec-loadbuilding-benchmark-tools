import unittest

from tests.TestUtils         import TestCase as TestUtils
from tests.TestDescription   import TestCase as TestDescription
from tests.TestContainerkind import TestCase as TestContainerkind
from tests.TestPalletkind    import TestCase as TestPalletkind
from tests.TestBoxkind       import TestCase as TestBoxkind
from tests.TestItemkind      import TestCase as TestItemkind
from tests.TestLoadingspace  import TestCase as TestLoadingspace
from tests.TestObjective     import TestCase as TestObjective
from tests.TestConstraint    import TestCase as TestConstraint
from tests.TestInstance      import TestCase as TestInstance
from tests.TestReadInstance  import TestCase as TestReadInstance


from tests.TestContainer     import TestCase as TestContainer
from tests.TestBox           import TestCase as TestBox
from tests.TestPlacement     import TestCase as TestPlacement
from tests.TestReadSolution  import TestCase as TestReadSolution

suite = unittest.TestSuite()
suite.addTest(TestUtils)
suite.addTest(TestDescription)
suite.addTest(TestContainerkind)
suite.addTest(TestPalletkind)
suite.addTest(TestBoxkind)
suite.addTest(TestItemkind)
suite.addTest(TestLoadingspace)
suite.addTest(TestObjective)
suite.addTest(TestConstraint)
suite.addTest(TestInstance)
suite.addTest(TestReadInstance)
suite.addTest(TestContainer)
suite.addTest(TestBox)
suite.addTest(TestPlacement)
suite.addTest(TestReadSolution)
unittest.TextTestRunner(verbosity=2).run(suite)