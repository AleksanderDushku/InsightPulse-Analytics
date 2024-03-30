import re

# Given text containing the PromQL query
text = "[ContentBlock(text='up{job="prometheus"}', type='text')]"

# Regular expression pattern to extract the query
pattern = r"'(.*?)'"

# Search for the pattern in the text
match = re.search(pattern, text)

# If a match is found, extract the query
if match:
    promql_query = match.group(1)
    print("PromQL Query:", promql_query)
else:
    print("No PromQL query found.")
