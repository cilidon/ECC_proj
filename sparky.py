import praw
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace
import api


def spark_call(topic='indiana', post_counts=20):

    results = api.fetch_reddit_api(topic, post_counts)
# Initializing SparkSession
    spark = SparkSession.builder.appName("Reddit_Data_Cleaning").getOrCreate()

    # Creating a list of dictionaries representing the scraped data
    data = []
    for post in result.new(limit=100):
        post_dict = {'data': post.title + post.selftext,
                    'score': post.score,
                    'author': post.author.name if post.author else '',
                    'created_utc': post.created_utc}
        data.append(post_dict)

    # Converting the list of dictionaries to a Spark DataFrame
    df = spark.createDataFrame(data)

    # Defining a function to clean the "title" field
    def clean_title(title):
        cleaned_title = regexp_replace(title, "[^A-Za-z0-9\s]+", "")
        return cleaned_title

    # Applying clean_title() function using map() function
    cleaned_rdd = df.rdd.map(lambda x: (x.data, x.author, x.created_utc))

    # Converting RDD to DataFrame
    cleaned_df = cleaned_rdd.toDF(["data", "user_id", "post_date"])

    # Removing null or empty values using filter() function
    cleaned_df = cleaned_df.filter((col("data") != "") & (col("user_id").isNotNull()))

    # Saving cleaned data as JSON
    dfJso=cleaned_df.toJSON()
    json_string = cleaned_df.toJSON().collect()

    # Converting JSON string to JSON object
    json_object = [json.loads(record) for record in json_string]

    # Stopping SparkSession
    spark.stop()

    return json_object