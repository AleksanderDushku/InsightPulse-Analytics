import re

import anthropic
from prometheus_api_client import PrometheusConnect

# Prometheus server URL
prometheus_url = "http://localhost:9090"

# Initialize Anthropi client
client = anthropic.Anthropic(
    api_key=""
)


def fetch_metrics():
    """
    Fetch all metric names from Prometheus.
    """
    try:
        prom = PrometheusConnect(url=prometheus_url)
        return prom.all_metrics()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_prometheus_data(promql_query):
    """
    Fetch data from Prometheus based on the given PromQL query.
    """
    try:
        prom = PrometheusConnect(url=prometheus_url)
        prom.custom_query(query="sum(prometheus_http_requests_total)")
        print(prom.custom_query(query=promql_query))
        return prom.custom_query(query=promql_query)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def map_data_together():
    """
    Map fetched data (metrics) together.
    """
    mapped_data = {}

    # Fetch metrics
    metrics = fetch_metrics()
    if metrics:
        for metric in metrics:
            mapped_data[metric[0]] = None

    return mapped_data


# Map the data together
mapped_data = map_data_together()

query_input = input("Enter your request (Type 'exit' to quit): ")


def main():

    # Check if user wants to exit
    if query_input.lower() == "exit":
        print("Exiting...")
        return
    # Get user input
    # Create the prompt and call the API with the user input
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=100,
        temperature=0.0,
        system="""
        Please provide only the PromQL query for analysis like: up{job="prometheus"} and only this no other text like this one: 'To check if the Prometheus instance is up and running, you can use the following PromQL query:\n\n```\nup{job="prometheus"}\n```\n\nThis query uses the `up` metric, which is a special metric in Prometheus that indicates the health status of a target. The `up` metric has a value of 1 if the target is reachable and a value of 0 if it is not.\n\nThe `{job="prometheus"}`':

        Restrictions and Guidelines:
        - Format: Your query should follow the correct syntax and format of PromQL.
        - Target Metrics: Ensure that your query targets relevant metrics for analysis.
        - Complexity: Avoid overly complex queries that may result in long execution times.
        - Functionality: Use appropriate functions and operators to filter, aggregate, and manipulate metrics effectively.
        - Accuracy: Double-check your query for accuracy before submission.

        For more information on constructing PromQL queries, refer to the Prometheus documentation:
        https://prometheus.io/docs/prometheus/latest/querying/basics/

        Enter your PromQL query below:
        """,
        messages=[
            {"role": "user", "content": query_input},
        ],
    )

    # Extract PromQL query from Claude's response content
    promql_query_match = message.content
    print("Extract PromQL query from Claude's response content")
    pattern = r"'(.*?)'"
    # Search for the pattern in the text
    match = re.search(pattern, str(promql_query_match))
    print("Search done")
    if match:
        promql_query = match.group(1)
        print(promql_query)

        # Fetch data from Prometheus based on the PromQL query
        prometheus_data = fetch_prometheus_data(promql_query)
        print("Printing data")

        if prometheus_data:
            # Format Prometheus data as a dictionary
            formatted_data = {}
            for result in prometheus_data:
                metric_name = result["metric"]["__name__"]
                metric_value = result["value"]
                formatted_data[metric_name] = metric_value
                data = str(formatted_data)
                print(data, formatted_data)

            # Send Prometheus data back to Claude
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=100,
                temperature=0.0,
                system="Response from Prometheus API",
                messages=[
                    {"role": "user", "content": query_input},
                    {"role": "assistant", "content": data},
                ],
            )
            print(response.content)
        else:
            print("Failed to fetch data from Prometheus.")
    else:
        print("No PromQL query found in Claude's response.")


if __name__ == "__main__":
    main()
