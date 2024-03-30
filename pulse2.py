import anthropic
import requests

# Prometheus server URL
prometheus_url = "http://localhost:9090/api/v1"

def fetch_metrics():
    """
    Fetch all metric names from Prometheus.
    """
    try:
        response = requests.get(f"{prometheus_url}/label/__name__/values")
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Failed to fetch metrics: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def fetch_labels():
    """
    Fetch all labels from Prometheus.
    """
    try:
        response = requests.get(f"{prometheus_url}/labels")
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Failed to fetch labels: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def fetch_targets():
    """
    Fetch all targets from Prometheus.
    """
    try:
        response = requests.get(f"{prometheus_url}/targets")
        if response.status_code == 200:
            return response.json()['data']['activeTargets']
        else:
            print(f"Failed to fetch targets: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def fetch_series(metric_name):
    """
    Fetch series for a specific metric from Prometheus.
    """
    try:
        response = requests.get(f"{prometheus_url}/series", params={"match[]": metric_name})
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Failed to fetch series for metric {metric_name}: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def fetch_query_exemplars(query):
    """
    Fetch query exemplars from Prometheus for a specific query.
    """
    try:
        response = requests.get(f"{prometheus_url}/query_exemplars", params={"query": query})
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Failed to fetch query exemplars for query {query}: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def map_data_together():
    """
    Map fetched data (metrics, labels, targets, series, query exemplars) together.
    """
    mapped_data = {}

    # Fetch metrics
    metrics = fetch_metrics()
    if metrics:
        for metric in metrics:
            metric_name = metric
            mapped_data[metric_name] = {
                "labels": None,
                "targets": None,
                # "series": None,
                # "query_exemplars": None
            }

    # Fetch labels
    labels = fetch_labels()
    if labels:
        for label in labels:
            if label in mapped_data:
                mapped_data[label]["labels"] = label

    # Fetch targets
    targets = fetch_targets()
    if targets:
        for target in targets:
            labels = target['labels']
            metric_name = labels.get('__metrics_path__')
            if metric_name in mapped_data:
                mapped_data[metric_name]["targets"] = labels

    # # Fetch series
    # for metric_name in mapped_data.keys():
    #     series = fetch_series(metric_name)
    #     if series:
    #         mapped_data[metric_name]["series"] = series

    # # Fetch query exemplars
    # for metric_name in mapped_data.keys():
    #     query = f"{metric_name}[5m]"
    #     query_exemplars = fetch_query_exemplars(query)
    #     if query_exemplars:
    #         mapped_data[metric_name]["query_exemplars"] = query_exemplars

    return mapped_data

# Initialize Anthropi client
client = anthropic.Anthropic(api_key="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")

# Get PromQL query from user input
query_input = input("Enter your PromQL query: ")

# Map the data together
mapped_data = map_data_together()


# Create the prompt and call the API with the PromQL query and Prometheus data
if mapped_data:
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=100,
        temperature=0.0,
        system="""
This system is designed to process PromQL queries and execute them against the Prometheus API. 
Please provide a PromQL query for me to execute against Prometheus API. 
A PromQL query is a query language used to retrieve time series data from Prometheus.
It allows you to filter, aggregate, and manipulate metrics to extract valuable insights. 
Ensure that your query is formatted correctly and targets relevant metrics for analysis.
Feel free to refer to the Prometheus documentation for guidance on constructing PromQL queries.
""",
       # system="PLease provide data based on the request from the user! Data is comming from the assitant and you can look through that data and provide information by mentioning the time when you were trained, and provide the query that the data can be searched. The query: should be format like this exampple: sum(metrics_name) by (job)",
        messages=[
            {
              "role": "user",
              "content": query_input
            },
            {
              "role": "assistant",
              "content": str(mapped_data)  # Include Prometheus data as response
            }
        ]
    )

    print("Claude's response:", message.content)
else:
    print("Failed to fetch data from Prometheus. Exiting...")
