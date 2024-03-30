import requests

# Prometheus server URL
prometheus_url = "http://localhost:9090/api/v1"

def get_jobs():
    """
    Get all job names from Prometheus.
    """
    try:
        # Get all job names
        jobs_response = requests.get(f"{prometheus_url}/targets")
        if jobs_response.status_code != 200:
            print(f"Failed to fetch job names from Prometheus: {jobs_response.text}")
            return None

        job_data = jobs_response.json()['data']['activeTargets']
        jobs = set()

        # Extract unique job names from job data
        for target in job_data:
            job = target['labels']['job']
            jobs.add(job)

        return jobs
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_metrics_for_job(job_name):
    """
    Get unique metrics associated with a specific job from Prometheus.
    """
    try:
        # Get all metric names for the job
        metrics_response = requests.get(f"{prometheus_url}/metrics", params={"match[]": f"{job_name}_"})
        if metrics_response.status_code != 200:
            print(f"Failed to fetch metrics for job {job_name}: {metrics_response.text}")
            return None

        metric_data = metrics_response.json()['data']
        metrics = set()

        # Extract unique metric names from metric data
        for metric in metric_data:
            metric_name = metric['name']
            metrics.add(metric_name)

        return metrics
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
jobs = get_jobs()
if jobs:
    print("Unique metrics based on jobs:")
    for job in jobs:
        print(f"Job: {job}")
        metrics = get_metrics_for_job(job)
        if metrics:
            print("Metrics:")
            for metric in metrics:
                print(metric)
        print()
