aws cloudwatch get-metric-data \
    --metric-data-queries '[{
        "Id": "cpuUtilizationQuery",
        "MetricStat": {
            "Metric": {
                "Namespace": "AWS/EC2",
                "MetricName": "CPUUtilization",
                "Dimensions": [{
                    "Name": "InstanceId",
                    "Value": ""
                }]
            },
            "Period": 300,
            "Stat": "Average"
        },
        "ReturnData": true
    }]' \
    --start-time 2024-04-01T00:00:00Z \
    --end-time 2024-06-19T00:00:00Z \
    --region us-east-1 > cpu_utilization_logs.json
