from pyspark import keyword_only
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, DecimalType
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param


class ValueMappingTransformer(Transformer, HasInputCol, HasOutputCol):

    """
    Maps the key values on inputCol to values in the mapDict
    """

    @keyword_only
    def __init__(self,
                 inputCol: str = None,
                 outputCol: str = None,
                 mapDict: dict = None):
        # call Transformer classes constructor since were extending it.
        super(Transformer, self).__init__()

        # set Parameter objects minimum mapping dictionary
        self.mapDict = Param(self,
                             "mapDict",
                             "A key string to value string dict, key is the value to be replaced with the value.")
        self._setDefault(mapDict={None: None})

        # set the input keywork arguments
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

        # initialize any other objects
        # self.my_obj = my_utility_objects()

    @keyword_only
    def setParams(self,
                  inputCol: str = None,
                  outputCol: str = None,
                  mapDict: dict = None
                  ) -> None:
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _trans_func(self, in_map_value: str) -> str:
        """
        Replacing a string value with another string value.
        The input value is looked up as a key on the dictMap and replaced
        by the corresponding dict value.

        Args:
            in_map_value: A string to be replaced with a corresponding value string on mapDict

        Returns:
            The mapped target value to be placed in the output column

        """

        # Get the specified mapping dictionary
        map_dict = self.getMapDict()

        # Select mapping value from dict and assign to out_col
        out_map_value = map_dict[in_map_value]

        return out_map_value

    def _transform(self, df: DataFrame) -> DataFrame:
        # Get the names of the input and output columns to use
        out_col = self.getOutputCol()
        in_col = self.getInputCol()

        # create the transformation function UDF
        trans_func_udf = F.udf(self._trans_func, StringType())

        # apply the UDF to the in_col column in the dataframe and add a
        # new out_col column with the transformed results
        df2 = df.withColumn(out_col, trans_func_udf(df[in_col]))

        return df2

    def setMapDict(self, value):
        self._paramMap[self.mapDict] = value
        return self

    def getMapDict(self) -> int:
        return self.getOrDefault(self.mapDict)


class TitleFoldTransformer(Transformer, HasInputCol, HasOutputCol):
    """
    Converts capitalized strings to start letter capital/title-caps.
    This string folding won't be performed for strings of defined length,
    contain numbers or are title-caps already.
    """

    @keyword_only
    def __init__(self,
                 inputCol: str = None,
                 outputCol: str = None,
                 capLength: int = None,
                 strSep: str = None):
        # call Transformer classes constructor since were extending it.
        super(Transformer, self).__init__()

        # set Parameter objects minimum capital letters and string separator
        self.capLength = Param(self,
                               "capLength",
                               "Number of characters in a String that should remain all-cap.")
        self._setDefault(capLength=0)
        self.strSep = Param(self,
                            "strSep",
                            "Single character String by which to separate multiple consecutive strings in inputCol.")
        self._setDefault(strSep="")

        # set the input keywork arguments
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

        # initialize any other objects
        # self.my_obj = my_utility_objects()

    @keyword_only
    def setParams(self,
                  inputCol: str = None,
                  outputCol: str = None,
                  capLength: int = None,
                  strSep: str = None
                  ) -> None:

        kwargs = self._input_kwargs
        return self._set(**kwargs)

    @staticmethod
    def _contains_number(in_str: str) -> str:
        """
        Checks a single string of any length for any digit.

        Args:
            in_str: A string

        Returns:
            True if a digit is found. False otherwise

        """
        return_bool = False
        return_bool = any(char.isdigit() for char in in_str)

        return return_bool

    def _trans_func(self, in_value: str) -> str:
        """
        Folds all words in an input string into title-caps, where words are
        separated by strSep cannot contain numbers and
        only words longer than capLength are changed.

        Args:
            in_value: A string with one or more words separated by a strSep

        Returns:
            A string with all words in title-cap

        """

        # Get the specified string length to keep capitalized and separator
        cap_length = self.getCapLength()
        str_sep = self.getStrSep()

        if in_value is not None:
            in_value_list = in_value.split(str_sep)
            out_value = ""

            # TODO: Needs good testing; var is only assigne dif if-statements completed as expected!!!
            for item in in_value_list:
                done = False
                if in_value_list[-1] == item:
                    # Only convert strings long enough, without numbers and not starting with single capital letter
                    if len(item) <= cap_length or self._contains_number(item) or item.istitle():
                        out_value = out_value + item
                        done = True
                    if (len(item) > cap_length or not self._contains_number(item) or item.istitle()) and not done:
                        out_value = out_value + item.title()
                if in_value_list[-1] != item:
                    # Only convert strings long enough, without numbers and not starting with single capital letter
                    if len(item) <= cap_length or self._contains_number(item) or item.istitle():
                        out_value = out_value + item + str_sep
                        done = True
                    if (len(item) > cap_length or self._contains_number(item) or item.istitle()) and not done:
                        out_value = out_value + item.title() + str_sep
        if in_value is None:
            out_value = None

        return out_value

    def _transform(self, df: DataFrame) -> DataFrame:
        # Get the names of the input and output columns to use
        out_col = self.getOutputCol()
        in_col = self.getInputCol()

        # create the transformation function UDF
        trans_func_udf = F.udf(self._trans_func, StringType())

        # apply the UDF to the in_col column in the dataframe and add a
        # new out_col column with the transformed results
        df2 = df.withColumn(out_col, trans_func_udf(df[in_col]))

        return df2

    def setCapLength(self, value):
        self._paramMap[self.capLength] = value
        return self

    def getCapLength(self) -> int:
        return self.getOrDefault(self.capLength)

    def setStrSep(self, value):
        self._paramMap[self.strSep] = value
        return self

    def getStrSep(self) -> int:
        return self.getOrDefault(self.strSep)


class StringDecimalTransformer(Transformer, HasInputCol, HasOutputCol):
    """
    Converts string numbers into decimals and removing white space,
    commas and thousands indicators as specified in the process
    """

    @keyword_only
    def __init__(self,
                 inputCol: str = None,
                 outputCol: str = None,
                 removeTokens: list = None,
                 decSplitStr: str = None,
                 precision: int = None,
                 scale: int = None):
        # call Transformer classes constructor since were extending it.
        super(Transformer, self).__init__()

        # set Parameter objects
        self.removeTokens = Param(self,
                                  "removeTokens",
                                  "A list of string tokens to remove, if one use [char], e.g., thousands indicators.")
        self._setDefault(removeTokens=[None])
        self.decSplitStr = Param(self,
                                 "decSplitStr",
                                 "A single character string indicating the decimal character, e.g. '.' in '0.1'.")
        self._setDefault(decSplitStr="")
        self.precision = Param(self,
                               "precision",
                               "Int for max digits before decimal, e.g, '2' in '0.1'. Defaults of DecimalType()")
        self._setDefault(precision=None)
        self.scale = Param(self,
                           "scale",
                           "Int number of precision to after decimals, e.g. '1' in '0.1'. Defaults of DecimalType()")
        self._setDefault(scale=None)

        # set the input keywork arguments
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

        # initialize any other objects
        # self.my_obj = my_utility_objects()

    @keyword_only
    def setParams(self,
                  inputCol: str = None,
                  outputCol: str = None,
                  removeTokens: list = None,
                  decSplitStr: str = None,
                  precision: int = None,
                  scale: int = None
                  ) -> None:
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _num_formater(self, in_value: str) -> str:
        """
        Checks if the in_value only contains permissible characters such as digits, tokens or separator,
        then removes these items.
        Additionally ensures that there is only a single separator.

        Args:
            in_value: A string to be checked

        Returns:
            A string of digits with tokens removed and a single separator value. None otherwise.

        """
        remove_tokens = self.getRemoveTokens()
        dec_split_str = self.getDecSplitStr()
        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        allowed = remove_tokens + [dec_split_str] + digits
        return_val = ""
        split_ct = 0

        for item in in_value:
            if item == dec_split_str:
                split_ct = split_ct + 1
                if split_ct > 1:
                    return_val = None
                    break
            if item not in allowed:
                return_val = None
                break
            if item in remove_tokens:
                in_value = in_value.replace(item, "")
            if item == in_value[-1]:
                return_val = in_value

        # Number formats work poor with anything else than "." therefore replacing dec_split_str
        if dec_split_str != "." and return_val is not None:
            return_val = return_val.replace(dec_split_str, ".")

        return return_val

    def _trans_func(self, in_value: str) -> str:

        clean_in_value = self._num_formater(str(in_value))

        return clean_in_value

    def _transform(self, df: DataFrame) -> DataFrame:
        # Get the names of the input and output columns to use
        # TODO: Make this work for a number of column names
        out_col = self.getOutputCol()
        in_col = self.getInputCol()

        # create the transformation function UDF
        trans_func_udf = F.udf(self._trans_func, StringType())

        # apply the UDF to the in_col column in the dataframe and add a
        # new out_col column with the transformed results
        df = df.withColumn(out_col, trans_func_udf(df[in_col]))

        # Compute precision/scale for adequate decimal value conversion unless defined by user
        # Note: This expects that the decSplitStr has been replaced by _numFormater with a "."!!!
        # TODO: Consider to simplify the query
        if self.getScale() is None or self.getPrecision() is None:
            pre_scl_df = df.select(df[out_col]) \
                .withColumn("pre_dec",
                            F.when(F.instr(out_col, ".") != 0,
                                   F.instr(out_col, ".") - 1) \
                            .otherwise(F.length(df[out_col]))) \
                .withColumn("post_dec",
                            F.when(
                                    F.when(F.instr(out_col, ".") != 0,
                                        F.length(df[out_col]) - 1) \
                                    .otherwise(F.length(df[out_col])) \
                                   - F.when(F.instr(out_col, ".") - 1 > 0,
                                            F.instr(out_col, ".") - 1) \
                                   .otherwise(0) == \
                                    F.when(F.instr(out_col, ".") != 0,
                                        F.length(df[out_col]) - 1) \
                                    .otherwise(F.length(df[out_col])), 0) \
                            .otherwise(
                                    F.when(F.instr(out_col, ".") != 0,
                                        F.length(df[out_col]) - 1) \
                                    .otherwise(F.length(df[out_col])) \
                                       - F.when(F.instr(out_col, ".") - 1 > 0,
                                                F.instr(out_col, ".") - 1) \
                                       .otherwise(0)))

            scale = pre_scl_df.agg(F.max("post_dec")).collect()[0][0]
            precision = pre_scl_df.agg(F.max("pre_dec")).collect()[0][0] + scale

            # TODO: Make this additive so that precision = scale + max characters because now too much of precision
            #       gets used by scale!
            self.setPrecision(precision)
            self.setScale(scale)

        df = df.withColumn(out_col, F.col(out_col).cast(DecimalType(self.getPrecision(),
                                                                    self.getScale())))

        return df

    def setRemoveTokens(self, value):
        self._paramMap[self.removeTokens] = value
        return self

    def getRemoveTokens(self) -> int:
        return self.getOrDefault(self.removeTokens)

    def setDecSplitStr(self, value):
        self._paramMap[self.decSplitStr] = value
        return self

    def getDecSplitStr(self) -> int:
        return self.getOrDefault(self.decSplitStr)

    def setPrecision(self, value):
        self._paramMap[self.precision] = value
        return self

    def getPrecision(self) -> int:
        return self.getOrDefault(self.precision)

    def setScale(self, value):
        self._paramMap[self.scale] = value
        return self

    def getScale(self) -> int:
        return self.getOrDefault(self.scale)
