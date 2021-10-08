from FileUtility import __get_type__, __get_encoding__


class TestFileUtility:
    def test_load_file(self):
        assert True

    def test__get_type__(self):
        test_file_name = "///./"
        test_result = __get_type__(test_file_name)
        assert test_result == "/"

    def test__get_encoding__(file_name):
        test_file_name = "data_utf8.csv"
        test_result = __get_encoding__(test_file_name)
        assert test_result == "utf-8" or test_result == "ascii"
