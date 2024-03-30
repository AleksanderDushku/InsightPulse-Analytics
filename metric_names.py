import requests

# Prometheus server URL
prometheus_url = "http://localhost:9090/api/v1"

def get_metric_names_with_tags():
    """
    Get all metric names along with their associated tags from Prometheus.
    """
    try:
        # Get all metric names
        metric_names_response = requests.get(f"{prometheus_url}/label/__name__/values")
        print(metric_names_response)
        if metric_names_response.status_code != 200:
            print(f"Failed to fetch metric names from Prometheus: {metric_names_response.text}")
            return None

        metric_names = metric_names_response.json()['data']
        print(metric_names)

        metric_names_with_tags = {}

        # For each metric name, get series (metric instances) and their labels
        for metric_name in metric_names:
            series_response = requests.get(f"{prometheus_url}/series", params={"match[]": metric_name})
            if series_response.status_code != 200:
                print(f"Failed to fetch series for metric {metric_name}: {series_response.text}")
                continue

            series_data = series_response.json()['data']

            # Extract unique label sets from series data
            label_sets = set()
            for series in series_data:
                if 'metric' in series:
                    labels = series['metric']
                    label_set = frozenset(labels.items())
                    label_sets.add(label_set)

            metric_names_with_tags[metric_name] = label_sets

        return metric_names_with_tags
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
metric_names_with_tags = get_metric_names_with_tags()
if metric_names_with_tags:
    print("Metric names along with their associated tags:")
    for metric_name, tags in metric_names_with_tags.items():
        print(f"Metric Name: {metric_name}")
        print("Tags:")
        for tag_set in tags:
            label_str = ', '.join([f"{k}={v}" for k, v in tag_set])
            print(label_str)
        print()
