# Build a Real-Time Santa Tracker

This demo builds a real-time application to help Santa deliver toys. This demo consists of:
* Streaming time-series data from Confluent Cloud that tracks when Santa delivers a toy, and when Santa's inventory gets increased from a workshop. This data stream mimics a Change Data Capture (CDC) that supplis inventory updates coming from a database. 
* An Amazon S3 `children` data store with 50 million toy recipients. 
* A `toys` dimensional table with a list of 106 different toys. 
* A Retool app that is driven by a set of Tinybird API Endpoints.

## Instructions

### 1. Set up a free Tinybird Workspace

Navigate to [tinybird.co/signup](https://www.tinybird.co/signup) and create a free account. Create a new Workspace (name it whatever you want).

### 2. Clone the repository

```bash
git clone https://github.com/tinybirdco/santa-tracker.git
cd santa-tracker
```

### 3. Install the Tinybird CLI

```bash
python -mvenv .e
. .e/bin/activate
pip install tinybird-cli
```

### 4. Authenticate to Tinybird

Copy your user admin token from [ui.tinybird.co/tokens](https://ui.tinybird.co/tokens). Your user admin token is the token with the format `admin <your email address>`.

In the Tinybird CLI, run the following command

```bash
cd tinybird
export TB_TOKEN=<your user admin token>
tb auth -i
```

If you intend to push this to your own repo, add the `.tinyb` file to your `.gitignore`, as it contains your user admin token.

```bash
echo ".tinyb" >> .gitignore
```

### 5. Create the inventory events Data Source in Tinybird

You're going to capture streaming data from Confluent into Tinybird so you can query it and build your APIs.

You can do this in the Tinybird UI using the [Confluent Connector](https://www.tinybird.co/docs/ingest/confluent.html), or in the CLI using the following command:

```bash
tb connection create kafka
# Kafka Bootstrap Server: <your Confluent server>
# Key: <your Confluent access key>
# Secret: <your Confluent secret>
# Connection name: <Give your connection a name, defaults to bootstrap server>
```

Then, update the `santa_inventory_cdc.datasource` file as follows:

```
SCHEMA >
    `inventory` Int16 `json:$.inventory`,
    `timestamp` DateTime `json:$.timestamp`,
    `toy_id` String `json:$.toy_id`

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(timestamp)"
ENGINE_SORTING_KEY "timestamp"

KAFKA_CONNECTION_NAME <your connection name>
KAFKA_TOPIC <your Confluent topic>
KAFKA_GROUP_ID <choose a consumer group ID>

```

### 6. Create the other Data Sources

This demo is based on two Data Sources, `toys` and `children`. 

For the `toys` Data Source, use the `toy_uuid_generator.py` Python script to generate a list of toys, each with a unique UUID. Once created you can drag and drop it onto the Tinybird UI, or use the "File Upload" option to add the Data Source. 

For the `children` Data Source, use the `generate_child_list.py` Python script to create a set of files with children metadata. This script uses the Faker package to generate these child metadata: child_id, child_first_name, child_last_name, latitude, longitude, status, toy_id, naughty_reason. By default, this script will create a single file with 1,000 entries. For the demo, we created 50 files, each with a million entries (!). 

### 7. Run the live inventory data generator

The `santa_inventory_events.py` data generator generates fresh inventory of Santa's toys for delivery. This script creates and writes inventory events to the Kafka stream (with help of the using the `confluent_kafka` Python package). Near the start of the script, be sure to enter your `CONFLUENT_SERVER`, `CONFLUENT_KEY`, and `CONFLUENT_SECRET` details. 

This script has command-line options for both restocking toys (`--restock`) and remove all inventory (`--drop`). There is also a `--speed`` option to control the rate at which Santa's inventory gets depleted. 

This script makes calls to the demo `santa_current-inventory` API Endpoint, so it can pick up from where it left off. 

When restocking, it will loop through the list of toys and created between 50 and 500 of each. 


### 8. Push the remaining resources to the Tinybird server

Push the remaining Pipes and Data Sources to Tinybird with:

```
tb push
```

### 9. Build a frontend!

You'll now have several Tinybird APIs that you can build with. We used Retool to build a simple frontend application. If you'd like to see how we did that, watch the [recording of our live coding session](https://www.youtube.com/watch?v=RI0k1P6UdLQ)

## Contributing

If you find any issues or have suggestions for improvements, please submit an issue or a [pull request](https://github.com/tinybirdco/santa-tracker/pulls?q=is%3Apr+is%3Aopen+sort%3Aupdated-desc).

## License

This code is available under the MIT license. See the [LICENSE](https://github.com/tinybirdco/scooter-rental-iot-analytics/blob/main/LICENSE.txt) file for more details.

## Need help?

&bull; [Community Slack](https://www.tinybird.co/community) &bull; [Tinybird Docs](https://www.tinybird.co/docs) &bull;

## Authors

- [Cameron Archer](https://github.com/tb-peregrine)
- [Jim Moffitt](https://github.com/jimmoffitt)
