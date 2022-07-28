(function() {
    // Create the connector object
    var myConnector = tableau.makeConnector();

    // Define the schema
    // Define columns in the table
    myConnector.getSchema = function(schemaCallback) {
        var cols = [{
            id: "city",
            dataType: tableau.dataTypeEnum.string,
            alias:"City",
            description:"Some Cities"
        },{
            id: "parameter",
            dataType: tableau.dataTypeEnum.string
        },{
            id: "value",
        dataType: tableau.dataTypeEnum.float
        },{
            id: "unit",
        dataType: tableau.dataTypeEnum.string
        },{
            id: "date",
        dataType: tableau.dataTypeEnum.datetime
        },{
            id: "latitude",
        dataType: tableau.dataTypeEnum.float
        },{
            id: "longitude",
        dataType: tableau.dataTypeEnum.float
        }];

        var tableSchema = {
            id: "openaqsea",
            alias: "Open AQ Seattle",
            columns: cols
        };

        schemaCallback([tableSchema]);
    };

    // Download the data
    myConnector.getData = function(table, doneCallback) {
        $.getJSON("api.openaq.org/v2/measurements.json?date_from=2022-07-01&date_to=2022-07-23&parameter=pm25&coordinates=47.597,-122.3197&radius=200000", function(resp) {
            var feat = resp.results,
                tableData = [];

            // Iterate over the JSON object
            for (var i = 0, len = feat.length; i < len; i++) {
                tableData.push({
                    "city": feat[i].city,
                    "parameter": feat[i].parameter,
                    "value": feat[i].value,
                    "unit": feat[i].unit,
                    "date": new Date(feat[i].date.local),
                    "latitude": feat[i].coordinates.latitude,
                    "longitude": feat[i].coordinates.longitude

                });
            }

            table.appendRows(tableData);
            doneCallback();
        });
    };

    tableau.registerConnector(myConnector);

    // Create event listeners for when the user submits the form
    $(document).ready(function() {
        $("#submitButton").click(function() {
            tableau.connectionName = "Open AQ Seattle"; // This will be the data source name in Tableau
            tableau.submit(); // This sends the connector object to Tableau
        });
    });
})();
