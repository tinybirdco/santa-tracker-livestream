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

### Update the inventory data generator with your Confluent cluster details

### Create the inventory events Data Source in Tinybird

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

### Create a `children` info Data Source



### Push the remaining resources to the Tinybird server

Push the remaining Pipes and Data Sources to Tinybird with...

```
tb push
```

### Build a frontend!

You'll now have several Tinybird APIs that you can build with. We used Retool to build a simple frontend application. If you'd like to see how we did that, watch the [recording of our live coding session](https://www.youtube.com/watch?v=rf7ZannHDf0)

## Contributing

If you find any issues or have suggestions for improvements, please submit an issue or a [pull request](https://github.com/tinybirdco/santa-tracker/pulls?q=is%3Apr+is%3Aopen+sort%3Aupdated-desc).

## License

This code is available under the MIT license. See the [LICENSE](https://github.com/tinybirdco/scooter-rental-iot-analytics/blob/main/LICENSE.txt) file for more details.

## Need help?

&bull; [Community Slack](https://www.tinybird.co/community) &bull; [Tinybird Docs](https://www.tinybird.co/docs) &bull;

## Authors

- [Cameron Archer](https://github.com/tb-peregrine)
- [Jim Moffitt](https://github.com/jimmoffitt)
