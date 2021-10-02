from pyspark import keyword_only
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.types import ArrayType, StringType, IntegerType, DecimalType
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param


class ValueMappingTransformer(Transformer, HasInputCol, HasOutputCol):
    """
    Maps the values on inputCol to values in the mapDict
    """

    @keyword_only
    def __init__(self,
                 inputCol: str = None,
                 outputCol: str = None,
                 mapDict: dict = None):
        # call Transformer classes constructor since were extending it.
        super(Transformer, self).__init__()

        # set Parameter objects minimum mapping dictionary
        self.mapDict = Param(self, "mapDict", "")
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
    Converts capitalized strings to start letter capital, except for
    string with a defined length which will remain all-cap
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
        self.capLength = Param(self, "capLength", "")
        self._setDefault(capLength=0)
        self.strSep = Param(self, "strSep", "")
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

    def _contains_number(self, in_str: str) -> str:
        return_bool = False
        return_bool = any(char.isdigit() for char in in_str)

        return return_bool


    def _trans_func(self, in_value: str) -> str:

        # Get the specified string length to keep capitalized and separator
        cap_length = self.getCapLength()
        str_sep = self.getStrSep()

        if in_value is not None:
            in_value_list = in_value.split(str_sep)
            out_value = ""

            # TODO: Needs good testing!!!
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
    Converts string numbers into Decimals
    """

    @keyword_only
    def __init__(self,
                 inputCol: str = None,
                 outputCol: str = None,
                 mapDict: dict = None):
        # call Transformer classes constructor since were extending it.
        super(Transformer, self).__init__()

        # set Parameter objects minimum mapping dictionary
        self.mapDict = Param(self, "mapDict", "")
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