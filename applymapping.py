# Convert AWS Glue DynamicFrame to Apache Spark DataFrame before applying lambdas.
df = datasource0.toDF()

# Extract latitude, longitude from location.  location looks like ["-48.8712", "-151.6866"]
get_latitude = udf(lambda loc: loc[0], StringType())
df = df.withColumn("tmp_latitude", get_latitude(df["sensor.location"]))

get_longitude = udf(lambda loc: loc[1], StringType())
df = df.withColumn("tmp_longitude", get_longitude(df["sensor.location"]))

# Compose the 10-digit sensor ID by hashing latitude, longitude and sensor number.
# So lat="-48.8712", lng="-151.6866", num=4 gets hashed to 8712 6866 04.
get_sensor_id = udf(
    lambda lat, lng, num: lat.split(".")[1] + lng.split(".")[1] + "{:0>2d}".format(num),
    StringType(),
)
df = df.withColumn(
    "tmp_sensorid",
    get_sensor_id(df["tmp_latitude"], df["tmp_longitude"], df["sensor.number"]),
)

# Address looks like "123 Main St, LAX, CA". Split into:
# block=123, street=Main St, city=LAX, state=CA
get_block = udf(lambda addr: addr.split(",")[0].split(" ", 1)[0].strip(), StringType())
df = df.withColumn("tmp_block", get_block(df["sensor.address"]))

get_street = udf(lambda addr: addr.split(",")[0].split(" ", 1)[1].strip(), StringType())
df = df.withColumn("tmp_street", get_street(df["sensor.address"]))

get_city = udf(lambda addr: addr.split(",")[1].strip(), StringType())
df = df.withColumn("tmp_city", get_city(df["sensor.address"]))

get_state = udf(lambda addr: addr.split(",")[2].strip(), StringType())
df = df.withColumn("tmp_state", get_state(df["sensor.address"]))

# Compose sensor name. For block=123, street=Main St, city=LAX, state=CA, sensor number=4,
# sensor name is CA-LAX-MainSt-123-04
get_sensor_name = udf(
    lambda blk, street, cty, state, num: "-".join(
        [state, cty, street.replace(" ", ""), blk, "{:0>2d}".format(num)]
    ),
    StringType(),
)
df = df.withColumn(
    "tmp_sensorname",
    get_sensor_name(
        df["tmp_block"],
        df["tmp_street"],
        df["tmp_city"],
        df["tmp_state"],
        df["sensor.number"],
    ),
)

# Multiply timestamp by 1,000. Import timestamp (int) looks like 1519516800 but RedShift needs it scaled by 1,000.
get_timestamp = udf(lambda ts: long(ts) * 1000, LongType())
df = df.withColumn("tmp_timestamp", get_timestamp(df["timestamp"]))

# Turn Apache Spark DataFrame back to AWS Glue DynamicFrame
datasource0 = DynamicFrame.fromDF(df, glueContext, "nested")

## @type: ApplyMapping
## @args: [mapping = [("timestamp", "int", "timestamp", "timestamp"), ("temperature", "double", "temperature", "double"), ("sensor.number", "int", "number", "int"), ("sensor.location", "array", "location", "string"), ("sensor.address", "string", "address", "string")], transformation_ctx = "applymapping1"]
## @return: applymapping1
## @inputs: [frame = datasource0]
applymapping1 = ApplyMapping.apply(
    frame=datasource0,
    mappings=[
        ("tmp_timestamp", "bigint", "timestamp", "timestamp"),
        ("tmp_sensorid", "string", "sensorid", "bigint"),
        ("tmp_sensorname", "string", "sensorname", "string"),
        ("tmp_latitude", "string", "latitude", "decimal(8,4)"),
        ("tmp_longitude", "string", "longitude", "decimal(8,4)"),
        ("tmp_block", "string", "block", "string"),
        ("tmp_street", "string", "street", "string"),
        ("tmp_city", "string", "city", "string"),
        ("tmp_state", "string", "state", "string"),
        ("temperature", "double", "temperature", "double"),
        ("sensor.number", "int", "number", "int"),
        ("sensor.location", "array", "location", "string"),
        ("sensor.address", "string", "address", "string"),
    ],
    transformation_ctx="applymapping1",
)

