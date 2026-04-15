import unittest
import unittest_shared
import importer_api.unittest_importer_api as unittest_api
import importer_web_worker.unittest_web_worker as unittest_web_worker
import importer_telegram.unittest_telegram as unittest_telegram


test_cases = list()
# shared
test_cases.append(unittest_shared.TestDefineSourceUrl)
test_cases.append(unittest_shared.TestDefineType)
test_cases.append(unittest_shared.TestIsUUID)
test_cases.append(unittest_shared.TestLocalDateTimeFromString)
test_cases.append(unittest_shared.TestImportDateLocalize)
test_cases.append(unittest_api.TestStaticPath)
test_cases.append(unittest_api.TestRoutes)
test_cases.append(unittest_api.TestCrawlHandlersGetParseResultsHandler)
# test_cases.append(unittest_shared.TestCheckVkDate)
# Web Worker
test_cases.append(unittest_web_worker.TestWebCrawler)
test_cases.append(unittest_web_worker.TestRSSCrawler)
test_cases.append(unittest_web_worker.TestBaseParser)
test_cases.append(unittest_web_worker.TestWebParser)
# Telegram
test_cases.append(unittest_telegram.TestChecker)

testLoad = unittest.TestLoader()

suites = []
for tc in test_cases:
    suites.append(testLoad.loadTestsFromTestCase(tc))

res_suite = unittest.TestSuite(suites)

runner = unittest.TextTestRunner(verbosity=2)
testResult = runner.run(res_suite)
if any([len(testResult.errors) > 0, len(testResult.failures) > 0]):
    exit(1)
print("errors: {}".format(len(testResult.errors)))
print("failures: {}".format(len(testResult.failures)))
print("skipped: {}".format(len(testResult.skipped)))
print("tests ran: {}".format(testResult.testsRun))
