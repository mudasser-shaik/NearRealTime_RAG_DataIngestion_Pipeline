import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, lit, from_json
from pyspark.sql.functions import concat_ws, col, initcap
from pyspark.sql.types import ArrayType, FloatType, StringType, StructType, StructField, IntegerType
import openai

class DataPipeline:
    def __init__(self, app_name: str, master: str = "local[*]"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .master(master) \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
            .getOrCreate()

    def read_topic_data(self, topic_name: str, kafka_bootstrap_servers: str):
        schema = StructType([
            StructField("store_id", IntegerType()),
            StructField("product_id", IntegerType()),
            StructField("count", IntegerType()),
            StructField("price", FloatType()),
            StructField("size", StringType()),
            StructField("ageGroup", StringType()),
            StructField("gender", StringType()),
            StructField("season", StringType()),
            StructField("fashionType", StringType()),
            StructField("brandName", StringType()),
            StructField("baseColor", StringType()),
            StructField("articleType", StringType())
        ])

        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("subscribe", topic_name) \
            .option("startingOffsets", "earliest") \
            .load()

        df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

        return df

    def generate_embedding(self, text):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
        return response['data'][0]['embedding']

    def process_data(self, df):
        df = df.withColumn("content", initcap(concat_ws(' ',
                                                        col("size"),
                                                        col("ageGroup"),
                                                        col("gender"),
                                                        col("season"),
                                                        col("fashionType"),
                                                        col("brandName"),
                                                        col("baseColor"),
                                                        col("articleType"),
                                                        concat_ws('', lit(', price: '), col("price").cast("string")),
                                                        concat_ws('', lit(', store number: '), col("store_id").cast("string")),
                                                        concat_ws('', lit(', product id: '), col("product_id").cast("string"))
                                                        )))
        return df

    def write_data(self, df, output_path: str, file_format: str = "parquet", mode: str = "overwrite"):
        query = df.writeStream \
            .format(file_format) \
            .outputMode(mode) \
            .option("path", output_path) \
            .option("checkpointLocation", "resources/checkpoint") \
            .start()
        query.awaitTermination()

    def stop(self):
        self.spark.stop()

if __name__ == "__main__":
    pipeline = DataPipeline(app_name="IngestionPipeline-VectorEmbedding-ProductRAG")
    kafka_topic = "product-updates"
    kafka_bootstrap_servers = "localhost:29092"

    generate_embedding_udf = udf(pipeline.generate_embedding, ArrayType(FloatType()))

    data = pipeline.read_topic_data(kafka_topic, kafka_bootstrap_servers)
    processed_data = pipeline.process_data(data)
    df_with_embeddings = processed_data.withColumn("vector", generate_embedding_udf(col("content")))

    df_with_embeddings.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .option("path", "resources/output") \
        .option("checkpointLocation", "resources/checkpoint") \
        .start() \
        .awaitTermination()

    pipeline.stop()