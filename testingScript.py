# -----------------------#
# Author: J Cameron Barge
#------------------------#

import unittest, app, sys, json, re, threading

# ------------------------ THREADING CODE ------------------------#


fail = False
thread1_done = 0
def thread_test1():
    global fail
    global thread1_done
    fail = False
    thread1_done = 0
    for i in range(0,20):
        if fail:
            thread1_done = 1
            return
        info = app.results_by_area(877)
        info = json.loads(info)
        if info[0]["area_code"] != "877" :
            fail = True
            thread1_done = 1
            return
    thread1_done = 1
    return

thread2_done = 0
def thread_test2():
    global fail
    global thread2_done
    fail = False
    thread2_done = 0
    for i in range(0,20):
        if fail:
            thread2_done = 1
            return
        info = app.results_by_area(770)
        info = json.loads(info)
        if info[0]["area_code"] != "770":
            fail = True
            thread2_done = 1
            return
    thread2_done = 1
    return

# ------------------------ THREADING CODE ------------------------#

class TestMethod(unittest.TestCase):

    #Test for '/interview/api/v1.0/results' functionality
    def test_results(self):
        info = app.results()
        info = json.loads(info)

        #test if matches eq expected values
        self.assertEqual(info[0]["area_code"],"844")
        self.assertEqual(info[1]["area_code"],"770")

        self.assertEqual(info[0]["phone_number"],"844-857-5628")
        self.assertEqual(info[1]["phone_number"],"770-232-6548")

        self.assertEqual(info[0]["report_count"],"2")
        self.assertEqual(info[1]["report_count"],"1")

        self.assertEqual(info[0]["comment"], "The company calling is loan me but they're just spoofing the number. I had them on me for the longest time. Get your credit fixed, its better than waiting for this stuff to come off. 408-753-0177 they don't always answer right away but they are really really good.")
        self.assertEqual(info[1]["comment"], "Scammer posing as breeder for puppies! Then the owner told me that was just the adoption fee and a ship to door fee as the puppy was in Maryland with her as her husband was having cancer surgery. They never answered my questions I asked about the size of the puppies parents. AND kept stressing DO...")

        #check all area codes
        for i in range(0,len(info)):
            self.assertTrue(info[i]["area_code"].isdigit())
            self.assertEqual(len(info[i]["area_code"]),3)

        #check all phone numbers
        for i in range(0,len(info)):
            self.assertTrue(re.match(r'^\d{3}-\d{3}-\d{4}$',info[i]["phone_number"]))
            #NOTE: There may be other phone number layouts or international numbers eg:
                # xxx-xxx-xxxx is handled,
                # xxxxxxxxxx   is not handled,
                # xxx xxx xxxx is not handled,
                # x xxx xxx xxxx is not handled,
                # (xxx)-xxx-xxxx is not handled,
                # These can be included by using more regex's depending on what forms you want to allow
                # ! - Different number formats will require different area_code parsing methods

        #check report numbers
        for i in range(0,len(info)):
            self.assertTrue(info[i]["report_count"].isdigit())
            self.assertTrue(int(info[i]["report_count"]) > 0)

    #Test for '/interview/api/v1.0/results/<int:number>' functionality
    def test_results_limit(self):
        #Base Case
        info = app.results_with_limit(1)
        self.assertNotEqual(info,None,"Expecting values")

        info = json.loads(info)
        self.assertEqual(info[0]["phone_number"], "844-857-5628", "Value does not equal expected value")

        #0 Case
        info = app.results_with_limit(0)
        self.assertEqual(info,None,"Limit of 0 should return None")

        #Negative
        try:
            info = app.results_with_limit(-1)
        except:
            self.fail("Invalid input handling: negative")
        self.assertEqual(info,None,"Index less than 0, should return None")

        #Out of bounds
        info = app.results_with_limit(sys.maxint)
        info = json.loads(info)
        info2 = app.results()
        info2 = json.loads(info2)
        self.assertEqual(len(info),len(info2),"Incorrect number of responses")

        #Non-int (String, float)
        try:
            info = app.results_with_limit("a")
        except:
            self.fail("Invalid input handling: string")
        self.assertEqual(info,None,"Character case failed")

        try:
            info = app.results_with_limit("3.14")
        except:
            self.fail("Invalid input handling: float")
        self.assertEqual(info,None,"Float case failed")

    #Test for '/interview/api/v1.0/resultsForArea/<string:area_code>' functionality
    def test_area_code(self):
        #Base case
        info = app.results_by_area(877)
        self.assertNotEqual(info,None,"Expecting result - got none")

        info = json.loads(info)
        self.assertEqual(info[0]["comment"],"A scam","Value did not meet expected value")

        #Negative
        try:
            info = app.results_by_area(-111)
        except:
            self.fail("Invalid input handling: float")
        self.assertEqual(info,None,"Index less than 0, should return none")

        #Out of bounds
        info = app.results_by_area(4444)
        self.assertEqual(info,None,"Index out of bounds not handled properly")

        #Non-int
        try:
            info = app.results_by_area("abc")
        except:
            self.fail("Invalid input handling: string")
        self.assertEqual(info,None, "Index cannot be a string")

    #Test for '/interview/api/v1.0/resultsForArea/<string:area_code>/<int:number>' functionality
    def test_area_code_limit(self):
        #Base case
        info = app.results_by_area_with_limit(877,1)
        self.assertNotEqual(info,None,"Expecting result - got none")

        #Zero Case
        info = app.results_by_area_with_limit(877,0)
        self.assertEqual(info,None,"Limit of 0 should return None")

        #Negative
        try:
            info = app.results_by_area_with_limit(877,-1)
        except:
            self.fail("Invalid input handling: negative")
        self.assertEqual(info,None,"Index less than 0, should return none")

        #Out of bounds
        info = app.results_by_area_with_limit(877, sys.maxint)
        self.assertNotEqual(info,None,"Index out of bounds not handled properly")

        #Non-int
        try:
            info = app.results_by_area_with_limit("abc", 1)
        except:
            self.fail("Invalid input handling: string")
        self.assertEqual(info,None, "Index cannot be a string")

        try:
            info = app.results_by_area_with_limit(877, "a")
        except:
            self.fail("Invalid input handling: string")
        self.assertEqual(info, None, "Index cannot be a string")

        try:
            info = app.results_by_area_with_limit("abc", "a")
        except:
            self.fail("Invalid input handling: string")
        self.assertEqual(info, None, "Index cannot be a string")


    #Test for correct information retrieval with multiple concurrent requests
    def test_overwhelm(self):
        thread1 = threading.Thread(target=thread_test1)
        thread2 = threading.Thread(target=thread_test2)
        thread1.start()
        thread2.start()

        global thread1_done
        global thread2_done
        global fail

        count = 0
        while not thread1_done and not thread2_done:
            count+=1

        self.assertFalse(fail, "Multi-threading conflict")

#Run the tests
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMethod)
    unittest.TextTestRunner(verbosity=2).run(suite)
