## Transform and Import a JSON file into Amazon Redshift with AWS Glue

Let’s say we have JSON file containing the past year of temperature data collected from IoT Sensors. One million rows of JSON. Let’s analyse the sensor data to predict and simulate the tweaks to our cooling systems that will compensate for the overheating.

### Sample Data

[{
	"timestamp": 1519516800,
	"temperature": 26.7,
	"sensor": {
		"number": 4,
		"location": ["-75.5712", "-130.5355"],
		"address": "123 Main St, LAX, CA"
	}
}, {
	"timestamp": 1519517100,
	"temperature": 29.8,
	"sensor": {
		"number": 2,
		"location": ["-48.8712", "-151.6866"],
		"address": "456 Side St, SFO, CA"
	}
}]

